import uuid
import requests

from functools import reduce
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator, _lazy_re_compile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException

from bothub.authentication.models import User

from . import languages
from .exceptions import RepositoryUpdateAlreadyStartedTraining
from .exceptions import RepositoryUpdateAlreadyTrained
from .exceptions import TrainingNotAllowed
from .exceptions import DoesNotHaveTranslation


item_key_regex = _lazy_re_compile(r"^[-a-z0-9_]+\Z")
validate_item_key = RegexValidator(
    item_key_regex,
    _(
        "Enter a valid value consisting of lowercase letters, numbers, "
        + "underscores or hyphens."
    ),
    "invalid",
)


def can_t_be_other(value):
    if value == "other":
        raise ValidationError(_('The label can\'t be named as "other"'))


class RepositoryCategory(models.Model):
    class Meta:
        verbose_name = _("repository category")
        verbose_name_plural = _("repository categories")

    name = models.CharField(_("name"), max_length=32)
    icon = models.CharField(_("icon"), max_length=16, default="botinho")

    def __str__(self):
        return self.name  # pragma: no cover


class RepositoryQuerySet(models.QuerySet):
    def publics(self):
        return self.filter(is_private=False)

    def order_by_relevance(self):
        return self.annotate(examples_sum=models.Sum("versions")).order_by(
            "-versions__repositoryversionlanguage__total_training_end",
            "-examples_sum",
            "-created_at",
        )

    def supported_language(self, language):
        valid_examples = RepositoryExample.objects.all()
        valid_updates = RepositoryVersionLanguage.objects.filter(
            added__in=valid_examples
        )
        return self.filter(
            models.Q(language=language)
            | models.Q(
                versions__repositoryversionlanguage__in=valid_updates,
                versions__repositoryversionlanguage__language=language,
            )
            | models.Q(
                versions__repositoryversionlanguage__in=valid_updates,
                versions__repositoryversionlanguage__added__translations__language=language,
            )
        )


class RepositoryManager(models.Manager):
    def get_queryset(self):
        return RepositoryQuerySet(self.model, using=self._db)


class Repository(models.Model):
    class Meta:
        verbose_name = _("repository")
        verbose_name_plural = _("repositories")
        unique_together = ["owner", "slug"]

    CATEGORIES_HELP_TEXT = _(
        "Categories for approaching repositories with " + "the same purpose"
    )
    DESCRIPTION_HELP_TEXT = _("Tell what your bot do!")

    ALGORITHM_STATISTICAL_MODEL = "statistical_model"
    ALGORITHM_NEURAL_NETWORK_INTERNAL = "neural_network_internal"
    ALGORITHM_NEURAL_NETWORK_EXTERNAL = "neural_network_external"
    ALGORITHM_CHOICES = [
        (ALGORITHM_STATISTICAL_MODEL, _("Statistical Model")),
        (
            ALGORITHM_NEURAL_NETWORK_INTERNAL,
            _("Neural Network with internal vocabulary"),
        ),
        (
            ALGORITHM_NEURAL_NETWORK_EXTERNAL,
            _("Neural Network with external vocabulary (BETA)"),
        ),
    ]

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    owner = models.ForeignKey(User, models.CASCADE, related_name="repositories")
    name = models.CharField(
        _("name"), max_length=64, help_text=_("Repository display name")
    )
    slug = models.SlugField(
        _("slug"),
        max_length=32,
        help_text=_("Easy way to found and share repositories"),
    )
    language = models.CharField(
        _("language"),
        max_length=5,
        help_text=_(
            "Repository's examples language. The examples can be "
            + "translated to other languages."
        ),
        validators=[languages.validate_language],
    )
    algorithm = models.CharField(
        _("algorithm"),
        max_length=24,
        choices=ALGORITHM_CHOICES,
        default=ALGORITHM_STATISTICAL_MODEL,
    )
    use_competing_intents = models.BooleanField(
        _("Use competing intents"),
        help_text=_(
            "When using competing intents the confidence of the "
            + "prediction is distributed in all the intents."
        ),
        default=False,
    )
    use_name_entities = models.BooleanField(
        _("Use name entities"),
        help_text=_(
            "When enabling name entities you will receive name of "
            + "people, companies and places as results of your "
            + "predictions."
        ),
        default=False,
    )
    use_analyze_char = models.BooleanField(
        _("Use analyze char"),
        help_text=_(
            "When selected, the algorithm will learn the patterns of "
            + "individual characters instead of whole words. "
            + "This approach works better for some languages."
        ),
        default=False,
    )
    categories = models.ManyToManyField(
        RepositoryCategory, help_text=CATEGORIES_HELP_TEXT
    )
    description = models.TextField(
        _("description"), blank=True, help_text=DESCRIPTION_HELP_TEXT
    )
    is_private = models.BooleanField(
        _("private"),
        default=False,
        help_text=_(
            "Your repository can be private, only you can see and"
            + " use, or can be public and all community can see and "
            + "use."
        ),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    nlp_server = models.URLField(_("Base URL NLP"), null=True, blank=True)

    objects = RepositoryManager()

    __algorithm = None
    __use_competing_intents = None
    __use_name_entities = None
    __use_analyze_char = None

    def __init__(self, *args, **kwargs):
        super(Repository, self).__init__(*args, **kwargs)
        self.__algorithm = self.algorithm
        self.__use_competing_intents = self.use_competing_intents
        self.__use_name_entities = self.use_name_entities
        self.__use_analyze_char = self.use_analyze_char

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if (
            self.algorithm != self.__algorithm
            or self.use_competing_intents != self.__use_competing_intents
            or self.use_name_entities != self.__use_name_entities
            or self.use_analyze_char != self.__use_analyze_char
        ):

            update = self.current_version(self.language)
            update.last_update = timezone.now()
            update.save(update_fields=["last_update"])

        super(Repository, self).save(force_insert, force_update, using, update_fields)

        self.__algorithm = self.algorithm
        self.__use_competing_intents = self.use_competing_intents
        self.__use_name_entities = self.use_name_entities
        self.__use_analyze_char = self.use_analyze_char

    def request_nlp_train(self, user_authorization):
        try:  # pragma: no cover
            r = requests.post(  # pragma: no cover
                "{}train/".format(
                    self.nlp_server if self.nlp_server else settings.BOTHUB_NLP_BASE_URL
                ),
                data={},
                headers={"Authorization": "Bearer {}".format(user_authorization.uuid)},
            )
            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_analyze(self, user_authorization, data):
        try:  # pragma: no cover
            r = requests.post(  # pragma: no cover
                "{}parse/".format(
                    self.nlp_server if self.nlp_server else settings.BOTHUB_NLP_BASE_URL
                ),
                data={"text": data.get("text"), "language": data.get("language")},
                headers={"Authorization": "Bearer {}".format(user_authorization.uuid)},
            )
            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_evaluate(self, user_authorization, data):
        try:  # pragma: no cover
            r = requests.post(  # pragma: no cover
                "{}evaluate/".format(
                    self.nlp_server if self.nlp_server else settings.BOTHUB_NLP_BASE_URL
                ),
                data={"language": data.get("language")},
                headers={"Authorization": "Bearer {}".format(user_authorization.uuid)},
            )
            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @property
    def available_languages(self):
        examples = self.examples()
        examples_languages = examples.values_list(
            "repository_version_language__language", flat=True
        )
        translations_languages = (
            examples.annotate(translations_count=models.Count("translations"))
            .filter(translations_count__gt=0)
            .values_list("translations__language", flat=True)
        )
        return list(
            set(
                [self.language]
                + list(examples_languages)
                + list(translations_languages)
            )
        )

    @property
    def languages_status(self):
        return dict(
            map(
                lambda language: (language, self.language_status(language)),
                settings.SUPPORTED_LANGUAGES.keys(),
            )
        )

    @property
    def current_versions(self):
        return map(lambda lang: self.current_version(lang), self.available_languages)

    @property
    def requirements_to_train(self):
        return dict(
            filter(
                lambda l: l[1],
                map(
                    lambda u: (u.language, u.requirements_to_train),
                    self.current_versions,
                ),
            )
        )

    @property
    def languages_ready_for_train(self):
        return dict(
            map(lambda u: (u.language, u.ready_for_train), self.current_versions)
        )

    @property
    def ready_for_train(self):
        return reduce(
            lambda current, u: u.ready_for_train or current,
            self.current_versions,
            False,
        )

    @property
    def languages_warnings(self):
        return dict(
            filter(
                lambda w: len(w[1]) > 0,
                map(lambda u: (u.language, u.warnings), self.current_versions),
            )
        )

    @property
    def intents(self):
        return list(
            set(
                self.examples(exclude_deleted=True)
                .exclude(intent="")
                .values_list("intent", flat=True)
            )
        )

    @property
    def current_entities(self):
        return self.entities.filter(
            value__in=self.examples(exclude_deleted=True)
            .exclude(entities__entity__value__isnull=True)
            .values_list("entities__entity__value", flat=True)
            .distinct()
        )

    @property
    def entities_list(self):
        return self.current_entities.values_list("value", flat=True).distinct()

    @property
    def current_labels(self):
        return self.labels.filter(entities__value__in=self.entities_list).distinct()

    @property
    def labels_list(self):
        return self.current_labels.values_list("value", flat=True).distinct()

    @property
    def other_entities(self):
        return self.current_entities.filter(label__isnull=True)

    @property
    def admins(self):
        admins = [self.owner] + [
            authorization.user
            for authorization in self.authorizations.filter(
                role=RepositoryAuthorization.ROLE_ADMIN
            )
        ]
        return list(set(admins))

    @property
    def use_language_model_featurizer(self):
        return self.algorithm != Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL

    def __str__(self):
        return "Repository {} - {}/{}".format(
            self.name, self.owner.nickname, self.slug
        )  # pragma: no cover

    def examples(
        self, language=None, exclude_deleted=True, queryset=None, version_default=True
    ):
        if queryset is None:
            queryset = RepositoryExample.objects
        query = queryset.filter(
            repository_version_language__repository_version__repository=self
        )

        if version_default:
            query = query.filter(
                repository_version_language__repository_version__is_default=True
            )
        if language:
            query = query.filter(repository_version_language__language=language)
        return query

    def evaluations(
        self, language=None, exclude_deleted=True, queryset=None, version_default=True
    ):
        if queryset is None:
            queryset = RepositoryEvaluate.objects
        query = queryset.filter(
            repository_version_language__repository_version__repository=self
        )
        if version_default:
            query = query.filter(
                repository_version_language__repository_version__is_default=True
            )
        if language:
            query = query.filter(repository_version_language__language=language)
        return query  # pragma: no cover

    def evaluations_results(self, queryset=None, version_default=True):
        if queryset is None:
            queryset = RepositoryEvaluateResult.objects
        if version_default:
            queryset = queryset.filter(
                repository_version_language__repository_version__is_default=True
            )
        query = queryset.filter(
            repository_version_language__repository_version__repository=self
        )
        return query

    def language_status(self, language):
        is_base_language = self.language == language
        examples = self.examples(language)
        base_examples = self.examples(self.language)
        base_translations = RepositoryTranslatedExample.objects.filter(
            original_example__in=base_examples, language=language
        )

        examples_count = examples.count()
        base_examples_count = base_examples.count()
        base_translations_count = base_translations.count()
        base_translations_percentage = (
            base_translations_count
            / (base_examples_count if base_examples_count > 0 else 1)
        ) * 100

        return {
            "is_base_language": is_base_language,
            "examples": {
                "count": examples_count,
                "entities": list(
                    set(
                        filter(
                            lambda x: x,
                            examples.values_list(
                                "entities__entity", flat=True
                            ).distinct(),
                        )
                    )
                ),
            },
            "base_translations": {
                "count": base_translations_count,
                "percentage": base_translations_percentage,
            },
        }

    def current_version(self, language=None, is_default=True):
        language = language or self.language

        repository_version, created = self.versions.get_or_create(is_default=is_default)

        repository_version_language, created = RepositoryVersionLanguage.objects.get_or_create(
            repository_version=repository_version, language=language
        )
        return repository_version_language

    def last_trained_update(self, language=None):
        language = language or self.language
        version = self.versions.filter(
            created_by__isnull=False, is_default=True
        ).first()

        if version:
            return version.version_languages.filter(
                language=language, training_end_at__isnull=False
            ).first()
        return RepositoryVersionLanguage.objects.none()

    def get_specific_version_language(self, language=None):
        query = RepositoryVersionLanguage.objects.filter(
            repository_version__repository=self
        )
        if language:
            query = query.filter(language=language)
        return query.first()

    def get_user_authorization(self, user):
        if user.is_anonymous:
            return RepositoryAuthorization(repository=self)
        get, created = RepositoryAuthorization.objects.get_or_create(
            user=user, repository=self
        )
        return get

    def get_absolute_url(self):
        return "{}{}/{}/".format(
            settings.BOTHUB_WEBAPP_BASE_URL, self.owner.nickname, self.slug
        )


class RepositoryVersion(models.Model):
    class Meta:
        verbose_name = _("repository version")
        ordering = ["-is_default"]

    name = models.CharField(max_length=40, default="master")
    last_update = models.DateTimeField(_("last update"), auto_now_add=True)
    is_default = models.BooleanField(default=True)
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="versions")
    created_by = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @property
    def version_languages(self):
        return RepositoryVersionLanguage.objects.filter(repository_version=self)


class RepositoryVersionLanguage(models.Model):
    class Meta:
        verbose_name = _("repository version language")
        verbose_name_plural = _("repository version languages")
        ordering = ["-created_at"]

    MIN_EXAMPLES_PER_INTENT = 2
    MIN_EXAMPLES_PER_ENTITY = 2
    RECOMMENDED_INTENTS = 2

    language = models.CharField(
        _("language"), max_length=5, validators=[languages.validate_language]
    )
    bot_data = models.TextField(_("bot data"), blank=True)
    training_started_at = models.DateTimeField(
        _("training started at"), blank=True, null=True
    )
    training_end_at = models.DateTimeField(_("trained at"), blank=True, null=True)
    failed_at = models.DateTimeField(_("failed at"), blank=True, null=True)
    use_analyze_char = models.BooleanField(default=False)
    use_name_entities = models.BooleanField(default=False)
    use_competing_intents = models.BooleanField(default=False)
    algorithm = models.CharField(
        _("algorithm"),
        max_length=24,
        choices=Repository.ALGORITHM_CHOICES,
        default=Repository.ALGORITHM_STATISTICAL_MODEL,
    )
    repository_version = models.ForeignKey(
        RepositoryVersion, models.CASCADE
    )
    training_log = models.TextField(_("training log"), blank=True, editable=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(
        _("last update"),
        null=True
    )
    total_training_end = models.IntegerField(
        _("total training end"), default=0, blank=False, null=False
    )

    @property
    def examples(self):
        examples = self.repository_version.repository.examples(
            exclude_deleted=False
        ).filter(
            models.Q(repository_version_language__language=self.language)
            | models.Q(translations__language=self.language)
        )
        if self.training_end_at and (self.training_end_at >= self.last_update):
            t_started_at = self.training_started_at
            examples = examples.exclude(
                models.Q(last_update__lte=self.training_end_at)
            )
        return examples.distinct()

    @property
    def requirements_to_train(self):
        try:
            self.validate_init_train()
        except RepositoryUpdateAlreadyTrained:  # pragma: no cover
            return [_("This bot version has already been trained.")]
        except RepositoryUpdateAlreadyStartedTraining:  # pragma: no cover
            return [_("This bot version is being trained.")]

        r = []

        intents = self.examples.values_list("intent", flat=True)

        if "" in intents:
            r.append(_("All examples need have a intent."))

        weak_intents = (
            self.examples.values("intent")
            .annotate(intent_count=models.Count("id"))
            .order_by()
            .exclude(intent_count__gte=self.MIN_EXAMPLES_PER_INTENT)
        )
        if weak_intents.exists():
            for i in weak_intents:
                r.append(
                    _('Intent "{}" has only {} examples. ' + "Minimum is {}.").format(
                        i.get("intent"),
                        i.get("intent_count"),
                        self.MIN_EXAMPLES_PER_INTENT,
                    )
                )

        weak_entities = (
            self.examples.annotate(es_count=models.Count("entities"))
            .filter(es_count__gte=1)
            .values("entities__entity__value")
            .annotate(entities_count=models.Count("id"))
            .order_by()
            .exclude(entities_count__gte=self.MIN_EXAMPLES_PER_ENTITY)
        )
        if weak_entities.exists():
            for e in weak_entities:
                r.append(
                    _('Entity "{}" has only {} examples. ' + "Minimum is {}.").format(
                        e.get("entities__entity__value"),
                        e.get("entities_count"),
                        self.MIN_EXAMPLES_PER_ENTITY,
                    )
                )

        return r

    @property
    def ready_for_train(self):
        previous_update = None
        if len(self.requirements_to_train) > 0:
            return False

        if self.training_end_at:
            previous = self.repository_version.repository.versions.filter(
                repositoryversionlanguage__language=self.language,
                last_update__gte=self.training_end_at,
                created_by__isnull=False,
            ).first()
        else:
            previous = self.repository_version.repository.versions.filter(
                repositoryversionlanguage__language=self.language,
                created_by__isnull=False,
            ).first()

        if previous:
            previous_update = previous.version_languages.filter(
                language=self.language
            ).first()

        if previous_update:
            if (
                previous_update.algorithm
                != self.repository_version.repository.algorithm
            ):
                return True
            if (
                previous_update.use_competing_intents
                is not self.repository_version.repository.use_competing_intents
            ):
                return True
            if (
                previous_update.use_name_entities
                is not self.repository_version.repository.use_name_entities
            ):
                return True
            if (
                previous_update.use_analyze_char
                is not self.repository_version.repository.use_analyze_char
            ):
                return True
            if previous_update.failed_at:
                return True

        if (
            not self.added.exists()
            and not self.translated_added.exists()
        ):
            return False

        if self.examples.count() == 0:
            return False

        return len(self.requirements_to_train) == 0

    @property
    def intents(self):
        return list(set(self.examples.values_list("intent", flat=True)))

    @property
    def warnings(self):
        w = []
        if 0 < len(self.intents) < self.RECOMMENDED_INTENTS:
            w.append(
                _(
                    "You need to have at least {} intents for the "
                    + "algorithm to identify intents."
                ).format(self.RECOMMENDED_INTENTS)
            )
        return w

    @property
    def use_language_model_featurizer(self):
        return self.algorithm != Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL

    def __str__(self):
        return "Repository Version Language #{}".format(self.id)  # pragma: no cover

    def validate_init_train(self, by=None):
        if by:
            authorization = self.repository_version.repository.get_user_authorization(
                by
            )
            if not authorization.can_write:
                raise TrainingNotAllowed()

    def start_training(self, created_by):
        self.validate_init_train(created_by)
        self.repository_version.created_by = created_by
        self.training_started_at = timezone.now()
        self.algorithm = self.repository_version.repository.algorithm
        self.use_competing_intents = (
            self.repository_version.repository.use_competing_intents
        )
        self.use_name_entities = self.repository_version.repository.use_name_entities
        self.use_analyze_char = self.repository_version.repository.use_analyze_char
        self.save(
            update_fields=[
                "training_started_at",
                "algorithm",
                "use_competing_intents",
                "use_name_entities",
                "use_analyze_char",
            ]
        )
        self.repository_version.save(update_fields=["created_by"])

    def save_training(self, bot_data):
        last_time = timezone.now()

        self.training_end_at = last_time
        self.last_update = last_time
        self.bot_data = bot_data
        self.total_training_end += 1
        self.save(update_fields=["total_training_end", "training_end_at", "bot_data", "last_update"])

    def get_bot_data(self):
        return self.bot_data

    def train_fail(self):
        self.failed_at = timezone.now()
        self.save(update_fields=["failed_at"])


class RepositoryExample(models.Model):
    class Meta:
        verbose_name = _("repository example")
        verbose_name_plural = _("repository examples")
        ordering = ["-created_at"]

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage, models.CASCADE, related_name="added", editable=False
    )
    text = models.TextField(_("text"), help_text=_("Example text"))
    intent = models.CharField(
        _("intent"),
        max_length=64,
        default="no_intent",
        help_text=_("Example intent reference"),
        validators=[validate_item_key],
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"))

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()
        self.repository_version_language.last_update = timezone.now()
        self.repository_version_language.save(update_fields=["last_update"])
        print(args)
        print(kwargs)
        super(RepositoryExample, self).save(*args, **kwargs)

    @property
    def language(self):
        return self.repository_version_language.language

    def has_valid_entities(self, language=None):  # pragma: no cover
        if not language or language == self.repository_version_language.language:
            return True
        return self.get_translation(language).has_valid_entities

    def get_translation(self, language):
        try:
            return self.translations.get(language=language)
        except RepositoryTranslatedExample.DoesNotExist:
            raise DoesNotHaveTranslation()

    def get_text(self, language=None):  # pragma: no cover
        if not language or language == self.repository_version_language.language:
            return self.text
        return self.get_translation(language).text

    def get_entities(self, language):  # pragma: no cover
        if not language or language == self.repository_version_language.language:
            return self.entities.all()
        return self.get_translation(language).entities.all()


class RepositoryTranslatedExampleManager(models.Manager):
    def create(
        self,
        *args,
        original_example=None,
        language=None,
        clone_repository=False,
        **kwargs
    ):
        repository = (
            original_example.repository_version_language.repository_version.repository
        )
        if clone_repository:
            return super().create(
                *args, original_example=original_example, language=language, **kwargs
            )
        return super().create(
            *args,
            repository_version_language=repository.current_version(language),
            original_example=original_example,
            language=language,
            **kwargs
        )


class RepositoryTranslatedExample(models.Model):
    class Meta:
        verbose_name = _("repository translated example")
        verbose_name_plural = _("repository translated examples")
        unique_together = ["original_example", "language"]
        ordering = ["-created_at"]

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        related_name="translated_added",
        editable=False,
    )
    original_example = models.ForeignKey(
        RepositoryExample,
        models.CASCADE,
        related_name="translations",
        editable=False,
        help_text=_("Example object"),
    )
    language = models.CharField(
        _("language"),
        max_length=5,
        help_text=_("Translation language"),
        validators=[languages.validate_language],
    )
    text = models.TextField(_("text"), help_text=_("Translation text"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    objects = RepositoryTranslatedExampleManager()

    def entities_list_lambda_sort(item):
        return item.get("entity")

    @classmethod
    def same_entities_validator(cls, a, b):
        a_len = len(a)
        if a_len != len(b):
            return False
        a_sorted = sorted(a, key=cls.entities_list_lambda_sort)
        b_sorted = sorted(b, key=cls.entities_list_lambda_sort)
        for i in range(a_len):
            if a_sorted[i].get("entity") != b_sorted[i].get("entity"):
                return False
        return True

    @classmethod
    def count_entities(cls, entities_list, to_str=False):
        r = {}
        for e in entities_list:
            r.update({e.get("entity"): r.get("entity", 0) + 1})
        if to_str:
            r = (
                ", ".join(map(lambda x: "{} {}".format(x[1], x[0]), r.items()))
                if entities_list
                else "no entities"
            )
        return r

    @property
    def has_valid_entities(self):
        original_entities = self.original_example.entities.all()
        my_entities = self.entities.all()
        return RepositoryTranslatedExample.same_entities_validator(
            list(map(lambda x: x.to_dict, original_entities)),
            list(map(lambda x: x.to_dict, my_entities)),
        )


class RepositoryEntityLabelQueryset(models.QuerySet):
    def get(self, repository, value):
        try:
            return super().get(repository=repository, value=value)
        except self.model.DoesNotExist:
            return super().create(repository=repository, value=value)


class RepositoryEntityLabelManager(models.Manager):
    def get_queryset(self):
        return RepositoryEntityLabelQueryset(self.model, using=self._db)


class RepositoryEntityLabel(models.Model):
    class Meta:
        unique_together = ["repository", "value"]

    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="labels"
    )
    value = models.CharField(
        _("label"),
        max_length=64,
        validators=[validate_item_key, can_t_be_other],
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    objects = RepositoryEntityLabelManager()

    def examples(self, exclude_deleted=True):  # pragma: no cover
        return self.repository.examples(exclude_deleted=exclude_deleted).filter(
            entities__entity__label=self
        )


class RepositoryEntityQueryset(models.QuerySet):
    def get(self, repository, value, create_entity=True):
        try:
            return super().get(repository=repository, value=value)
        except self.model.DoesNotExist:
            if not create_entity:
                raise self.model.DoesNotExist  # pragma: no cover

            return super().create(repository=repository, value=value)


class RepositoryEntityManager(models.Manager):
    def get_queryset(self):
        return RepositoryEntityQueryset(self.model, using=self._db)


class RepositoryEntity(models.Model):
    class Meta:
        unique_together = ["repository", "value"]

    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="entities"
    )
    value = models.CharField(
        _("entity"),
        max_length=64,
        help_text=_("Entity name"),
        validators=[validate_item_key],
    )
    label = models.ForeignKey(
        RepositoryEntityLabel,
        on_delete=models.CASCADE,
        related_name="entities",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    objects = RepositoryEntityManager()

    def set_label(self, value):
        if not value:
            self.label = None
        else:
            self.label = RepositoryEntityLabel.objects.get(
                repository=self.repository, value=value
            )


class EntityBaseQueryset(models.QuerySet):  # pragma: no cover
    def create(self, entity, **kwargs):
        if type(entity) is not RepositoryEntity:
            instance = self.model(**kwargs)
            if "repository_evaluate_id" in instance.__dict__:
                evaluate = instance.repository_evaluate
                repository = (
                    evaluate.repository_version_language.repository_version.repository
                )
            elif "evaluate_result_id" in instance.__dict__:
                result = instance.evaluate_result
                repository = (
                    result.repository_version_language.repository_version.repository
                )
            else:
                repository = (
                    instance.example.repository_version_language.repository_version.repository
                )

            entity = RepositoryEntity.objects.get(repository=repository, value=entity)

        return super().create(entity=entity, **kwargs)


class EntityBaseManager(models.Manager):
    def get_queryset(self):
        return EntityBaseQueryset(self.model, using=self._db)


class EntityBase(models.Model):
    class Meta:
        verbose_name = _("repository example entity")
        verbose_name_plural = _("repository example entities")
        abstract = True

    start = models.PositiveIntegerField(
        _("start"), help_text=_("Start index of entity value in example text")
    )
    end = models.PositiveIntegerField(
        _("end"), help_text=_("End index of entity value in example text")
    )
    entity = models.ForeignKey(RepositoryEntity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    objects = EntityBaseManager()

    @property
    def example(self):
        return self.get_example()

    @property
    def value(self):
        return self.example.text[self.start : self.end]

    @property
    def rasa_nlu_data(self):  # pragma: no cover
        return {
            "start": self.start,
            "end": self.end,
            "value": self.value,
            "entity": self.entity.value,
        }

    @property
    def to_dict(self):
        return self.get_rasa_nlu_data()

    def get_example(self):
        pass  # pragma: no cover

    def get_rasa_nlu_data(self, label_as_entity=False):
        return {
            "start": self.start,
            "end": self.end,
            "entity": self.entity.label.value if label_as_entity else self.entity.value,
        }


class RepositoryExampleEntity(EntityBase):
    repository_example = models.ForeignKey(
        RepositoryExample,
        models.CASCADE,
        related_name="entities",
        editable=False,
        help_text=_("Example object"),
    )

    def get_example(self):
        return self.repository_example


class RepositoryTranslatedExampleEntity(EntityBase):
    repository_translated_example = models.ForeignKey(
        RepositoryTranslatedExample,
        models.CASCADE,
        related_name="entities",
        editable=False,
        help_text=_("Translated example object"),
    )

    def get_example(self):
        return self.repository_translated_example


class RepositoryAuthorization(models.Model):
    class Meta:
        verbose_name = _("repository authorization")
        verbose_name_plural = _("repository authorizations")
        unique_together = ["user", "repository"]

    LEVEL_NOTHING = 0
    LEVEL_READER = 1
    LEVEL_CONTRIBUTOR = 2
    LEVEL_ADMIN = 3

    ROLE_NOT_SETTED = 0
    ROLE_USER = 1
    ROLE_CONTRIBUTOR = 2
    ROLE_ADMIN = 3

    ROLE_CHOICES = [
        (ROLE_NOT_SETTED, _("not set")),
        (ROLE_USER, _("user")),
        (ROLE_CONTRIBUTOR, _("contributor")),
        (ROLE_ADMIN, _("admin")),
    ]

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(User, models.CASCADE)
    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="authorizations"
    )
    role = models.PositiveIntegerField(
        _("role"), choices=ROLE_CHOICES, default=ROLE_NOT_SETTED
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @property
    def level(self):
        try:
            user = self.user
        except User.DoesNotExist:
            user = None

        if user and self.repository.owner == user:
            return RepositoryAuthorization.LEVEL_ADMIN

        if self.role == RepositoryAuthorization.ROLE_NOT_SETTED:
            if self.repository.is_private:
                return RepositoryAuthorization.LEVEL_NOTHING
            return RepositoryAuthorization.LEVEL_READER

        if self.role == RepositoryAuthorization.ROLE_USER:
            return RepositoryAuthorization.LEVEL_READER

        if self.role == RepositoryAuthorization.ROLE_CONTRIBUTOR:
            return RepositoryAuthorization.LEVEL_CONTRIBUTOR

        if self.role == RepositoryAuthorization.ROLE_ADMIN:
            return RepositoryAuthorization.LEVEL_ADMIN

        return RepositoryAuthorization.LEVEL_NOTHING  # pragma: no cover

    @property
    def can_read(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_READER,
            RepositoryAuthorization.LEVEL_CONTRIBUTOR,
            RepositoryAuthorization.LEVEL_ADMIN,
        ]

    @property
    def can_contribute(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_CONTRIBUTOR,
            RepositoryAuthorization.LEVEL_ADMIN,
        ]

    @property
    def can_write(self):
        return self.level in [RepositoryAuthorization.LEVEL_ADMIN]

    @property
    def is_admin(self):
        return self.level == RepositoryAuthorization.LEVEL_ADMIN

    @property
    def is_owner(self):
        try:
            user = self.user
        except User.DoesNotExist:  # pragma: no cover
            return False  # pragma: no cover
        return self.repository.owner == user

    @property
    def role_verbose(self):
        return dict(RepositoryAuthorization.ROLE_CHOICES).get(self.role)

    def send_new_role_email(self, responsible=None):
        if not settings.SEND_EMAILS:
            return False  # pragma: no cover
        responsible_name = (
            responsible and responsible.name or self.repository.owner.name
        )
        context = {
            "base_url": settings.BASE_URL,
            "responsible_name": responsible_name,
            "user_name": self.user.name,
            "repository_name": self.repository.name,
            "repository_url": self.repository.get_absolute_url(),
            "new_role": self.role_verbose,
        }
        send_mail(
            _("New role in {}").format(self.repository.name),
            render_to_string("common/emails/new_role.txt", context),
            None,
            [self.user.email],
            html_message=render_to_string("common/emails/new_role.html", context),
        )


class RepositoryVote(models.Model):
    class Meta:
        verbose_name = _("repository vote")
        verbose_name_plural = _("repository votes")
        unique_together = ["user", "repository"]

    user = models.ForeignKey(User, models.CASCADE, related_name="repository_votes")
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="votes")
    created = models.DateTimeField(editable=False, default=timezone.now)


class RequestRepositoryAuthorization(models.Model):
    class Meta:
        unique_together = ["user", "repository"]

    user = models.ForeignKey(User, models.CASCADE, related_name="requests")
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="requests")
    text = models.CharField(_("text"), max_length=250)
    approved_by = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, editable=False
    )

    def send_new_request_email_to_admins(self):
        if not settings.SEND_EMAILS:
            return False  # pragma: no cover
        context = {
            "base_url": settings.BASE_URL,
            "user_name": self.user.name,
            "repository_name": self.repository.name,
            "text": self.text,
            "repository_url": self.repository.get_absolute_url(),
        }
        for admin in self.repository.admins:
            send_mail(
                _("New authorization request in {}").format(self.repository.name),
                render_to_string("common/emails/new_request.txt", context),
                None,
                [admin.email],
                html_message=render_to_string(
                    "common/emails/new_request.html", context
                ),
            )

    def send_request_rejected_email(self):
        if not settings.SEND_EMAILS:
            return False  # pragma: no cover
        context = {
            "repository_name": self.repository.name,
            "base_url": settings.BASE_URL,
        }
        send_mail(
            _("Access denied to {}").format(self.repository.name),
            render_to_string("common/emails/request_rejected.txt", context),
            None,
            [self.user.email],
            html_message=render_to_string(
                "common/emails/request_rejected.html", context
            ),
        )

    def send_request_approved_email(self):
        if not settings.SEND_EMAILS:
            return False  # pragma: no cover
        context = {
            "base_url": settings.BASE_URL,
            "admin_name": self.approved_by.name,
            "repository_name": self.repository.name,
        }
        send_mail(
            _("Authorization Request Approved to {}").format(self.repository.name),
            render_to_string("common/emails/request_approved.txt", context),
            None,
            [self.user.email],
            html_message=render_to_string(
                "common/emails/request_approved.html", context
            ),
        )


class RepositoryEvaluate(models.Model):
    class Meta:
        verbose_name = _("repository evaluate test")
        verbose_name_plural = _("repository evaluate tests")
        ordering = ["-created_at"]
        db_table = "common_repository_evaluate"

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        related_name="added_evaluate",
        editable=False,
    )
    deleted_in = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        related_name="deleted_evaluate",
        blank=True,
        null=True,
    )
    text = models.TextField(_("text"), help_text=_("Evaluate test text"))
    intent = models.CharField(
        _("intent"),
        max_length=64,
        default="no_intent",
        help_text=_("Evaluate intent reference"),
        validators=[validate_item_key],
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @property
    def language(self):
        return self.repository_version_language.language

    def get_text(self, language=None):  # pragma: no cover
        if not language or language == self.repository_version_language.language:
            return self.text
        return None

    def get_entities(self, language):  # pragma: no cover
        if not language or language == self.repository_version_language.language:
            return self.entities.all()
        return None

    def delete(self):
        self.deleted_in = self.repository_version_language.repository_version.repository.current_version(
            self.repository_version_language.language
        )
        self.save(update_fields=["deleted_in"])

    def delete_entities(self):
        self.entities.all().delete()


class RepositoryEvaluateEntity(EntityBase):
    class Meta:
        db_table = "common_repository_evaluate_entity"

    repository_evaluate = models.ForeignKey(
        RepositoryEvaluate,
        models.CASCADE,
        related_name="entities",
        editable=False,
        help_text=_("evaluate object"),
    )

    def get_evaluate(self):  # pragma: no cover
        return self.repository_evaluate


class RepositoryEvaluateResultScore(models.Model):
    class Meta:
        db_table = "common_repository_evaluate_result_score"
        ordering = ["-created_at"]

    precision = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    f1_score = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    accuracy = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    recall = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    support = models.IntegerField(null=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)


class RepositoryEvaluateResult(models.Model):
    class Meta:
        db_table = "common_repository_evaluate_result"
        verbose_name = _("evaluate results")
        verbose_name_plural = _("evaluate results")
        ordering = ["-created_at"]

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        editable=False,
        related_name="results",
    )

    intent_results = models.ForeignKey(
        RepositoryEvaluateResultScore,
        models.CASCADE,
        editable=False,
        related_name="intent_results",
    )

    entity_results = models.ForeignKey(
        RepositoryEvaluateResultScore,
        models.CASCADE,
        editable=False,
        related_name="entity_results",
    )

    matrix_chart = models.URLField(
        verbose_name=_("Intent Confusion Matrix Chart"), editable=False
    )

    confidence_chart = models.URLField(
        verbose_name=_("Intent Prediction Confidence Distribution"), editable=False
    )

    log = models.TextField(verbose_name=_("Evaluate Log"), blank=True, editable=False)

    version = models.IntegerField(
        verbose_name=_("Version"), blank=False, default=0, editable=False
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def save(self, *args, **kwargs):
        repository = self.repository_version_language.repository_version.repository
        self.version = repository.evaluations_results().count() + 1
        return super().save(*args, **kwargs)


class RepositoryEvaluateResultIntent(models.Model):
    class Meta:
        db_table = "common_repository_evaluate_result_intent"

    evaluate_result = models.ForeignKey(
        RepositoryEvaluateResult, models.CASCADE, related_name="evaluate_result_intent"
    )

    intent = models.CharField(
        _("intent"),
        max_length=64,
        help_text=_("Evaluate intent reference"),
        validators=[validate_item_key],
    )

    score = models.ForeignKey(
        RepositoryEvaluateResultScore,
        models.CASCADE,
        related_name="evaluation_intenties_score",
        editable=False,
    )


class RepositoryEvaluateResultEntity(models.Model):
    class Meta:
        db_table = "common_repository_evaluate_result_entity"

    evaluate_result = models.ForeignKey(
        RepositoryEvaluateResult, models.CASCADE, related_name="evaluate_result_entity"
    )

    entity = models.ForeignKey(
        RepositoryEntity, models.CASCADE, related_name="entity", editable=False
    )

    score = models.ForeignKey(
        RepositoryEvaluateResultScore,
        models.CASCADE,
        related_name="evaluation_entities_score",
        editable=False,
    )

    objects = EntityBaseManager()


@receiver(models.signals.pre_save, sender=RequestRepositoryAuthorization)
def set_user_role_on_approved(instance, **kwargs):
    current = None
    try:
        current = RequestRepositoryAuthorization.objects.get(pk=instance.pk)
    except RequestRepositoryAuthorization.DoesNotExist:
        pass

    if not current:
        return False

    if current.approved_by is None and current.approved_by is not instance.approved_by:
        user_authorization = instance.repository.get_user_authorization(instance.user)
        user_authorization.role = RepositoryAuthorization.ROLE_USER
        user_authorization.save(update_fields=["role"])
        instance.send_request_approved_email()
    else:
        raise ValidationError(_("You can change approved_by just one time."))


@receiver(models.signals.post_save, sender=RequestRepositoryAuthorization)
def send_new_request_email_to_admins_on_created(instance, created, **kwargs):
    if created:
        instance.send_new_request_email_to_admins()


@receiver(models.signals.post_delete, sender=RequestRepositoryAuthorization)
def send_request_rejected_email(instance, **kwargs):
    user_authorization = instance.repository.get_user_authorization(instance.user)
    user_authorization.delete()
    instance.send_request_rejected_email()
