import uuid
from functools import reduce

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator, _lazy_re_compile
from django.db import models
from django.db.models import Sum, Q, IntegerField, Case, When, Count
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

from bothub.authentication.models import User, RepositoryOwner
from . import languages
from .exceptions import DoesNotHaveTranslation
from .exceptions import RepositoryUpdateAlreadyStartedTraining
from .exceptions import RepositoryUpdateAlreadyTrained
from .exceptions import TrainingNotAllowed
from .. import utils

item_key_regex = _lazy_re_compile(r"^[-a-z0-9_]+\Z")
validate_item_key = RegexValidator(
    item_key_regex,
    _(
        "Enter a valid value consisting of lowercase letters, numbers, "
        + "underscores or hyphens."
    ),
    "invalid",
)


def can_t_be_other(value):  # pragma: no cover
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
        return self.annotate(
            trainings_count=Sum(
                "versions__repositoryversionlanguage__total_training_end"
            )
        ).order_by("-trainings_count", "-created_at")

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

    def count_logs(self, start_date=None, end_date=None, user=None, *args, **kwargs):
        return self.annotate(
            total_count=Sum(
                Case(
                    When(
                        versions__repositoryversionlanguage__repository_reports__user=user,
                        versions__repositoryversionlanguage__repository_reports__report_date__range=(
                            start_date,
                            end_date,
                        ),
                        then="versions__repositoryversionlanguage__repository_reports__count_reports",
                    ),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        ).filter(*args, **kwargs)


class RepositoryManager(models.Manager):
    def get_queryset(self):
        return RepositoryQuerySet(self.model, using=self._db)


class Organization(RepositoryOwner):
    class Meta:
        verbose_name = _("repository organization")

    description = models.TextField(_("description"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    verificated = models.BooleanField(default=False)

    repository_owner = models.OneToOneField(
        RepositoryOwner,
        on_delete=models.CASCADE,
        parent_link=True,
        related_name="organization_owner",
    )

    def get_organization_authorization(self, org):
        if org.is_anonymous:
            return OrganizationAuthorization(organization=self)
        get, created = OrganizationAuthorization.objects.get_or_create(
            user=org.repository_owner, organization=self
        )
        return get

    def set_user_permission(self, user: User, permission: int):
        perm, created = self.organization_authorizations.get_or_create(user=user)
        perm.role = permission
        perm.save(update_fields=["role"])


class OrganizationAuthorization(models.Model):
    class Meta:
        verbose_name = _("organization authorization")
        verbose_name_plural = _("organization authorizations")
        unique_together = ["user", "organization"]

    LEVEL_NOTHING = 0
    LEVEL_READER = 1
    LEVEL_CONTRIBUTOR = 2
    LEVEL_ADMIN = 3
    LEVEL_TRANSLATE = 4

    ROLE_NOT_SETTED = 0
    ROLE_USER = 1
    ROLE_CONTRIBUTOR = 2
    ROLE_ADMIN = 3
    ROLE_TRANSLATE = 4

    ROLE_CHOICES = [
        (ROLE_NOT_SETTED, _("not set")),
        (ROLE_USER, _("user")),
        (ROLE_CONTRIBUTOR, _("contributor")),
        (ROLE_ADMIN, _("admin")),
        (ROLE_TRANSLATE, _("translate")),
    ]

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(
        RepositoryOwner,
        models.CASCADE,
        null=True,
        related_name="organization_user_authorization",
    )
    organization = models.ForeignKey(
        Organization, models.CASCADE, related_name="organization_authorizations"
    )
    role = models.PositiveIntegerField(
        _("role"), choices=ROLE_CHOICES, default=ROLE_NOT_SETTED
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @property
    def level(self):
        if self.role == OrganizationAuthorization.ROLE_USER:
            return OrganizationAuthorization.LEVEL_READER

        if self.role == OrganizationAuthorization.ROLE_CONTRIBUTOR:
            return OrganizationAuthorization.LEVEL_CONTRIBUTOR

        if self.role == OrganizationAuthorization.ROLE_ADMIN:
            return OrganizationAuthorization.LEVEL_ADMIN

        if self.role == OrganizationAuthorization.ROLE_TRANSLATE:
            return OrganizationAuthorization.LEVEL_TRANSLATE

        return OrganizationAuthorization.LEVEL_NOTHING  # pragma: no cover

    @property
    def can_read(self):
        return self.level in [
            OrganizationAuthorization.LEVEL_READER,
            OrganizationAuthorization.LEVEL_CONTRIBUTOR,
            OrganizationAuthorization.LEVEL_ADMIN,
            OrganizationAuthorization.LEVEL_TRANSLATE,
        ]

    @property
    def can_contribute(self):
        return self.level in [
            OrganizationAuthorization.LEVEL_CONTRIBUTOR,
            OrganizationAuthorization.LEVEL_ADMIN,
        ]

    @property
    def can_write(self):
        return self.level in [OrganizationAuthorization.LEVEL_ADMIN]

    @property
    def can_translate(self):
        return self.level in [
            OrganizationAuthorization.LEVEL_CONTRIBUTOR,
            OrganizationAuthorization.LEVEL_ADMIN,
            OrganizationAuthorization.LEVEL_TRANSLATE,
        ]

    @property
    def is_admin(self):
        return self.level == OrganizationAuthorization.LEVEL_ADMIN

    @property
    def role_verbose(self):
        return dict(OrganizationAuthorization.ROLE_CHOICES).get(self.role)


class Repository(models.Model):
    class Meta:
        verbose_name = _("repository")
        verbose_name_plural = _("repositories")
        unique_together = ["owner", "slug"]

    CATEGORIES_HELP_TEXT = _(
        "Categories for approaching repositories with " + "the same purpose"
    )
    DESCRIPTION_HELP_TEXT = _("Tell what your bot do!")

    ALGORITHM_NEURAL_NETWORK_INTERNAL = "neural_network_internal"
    ALGORITHM_NEURAL_NETWORK_EXTERNAL = "neural_network_external"
    ALGORITHM_TRANSFORMER_NETWORK_DIET = "transformer_network_diet"
    ALGORITHM_TRANSFORMER_NETWORK_DIET_WORD_EMBEDDING = (
        "transformer_network_diet_word_embedding"
    )
    ALGORITHM_TRANSFORMER_NETWORK_DIET_BERT = "transformer_network_diet_bert"
    ALGORITHM_CHOICES = [
        (
            ALGORITHM_NEURAL_NETWORK_INTERNAL,
            _("Neural Network with internal vocabulary"),
        ),
        (
            ALGORITHM_NEURAL_NETWORK_EXTERNAL,
            _("Neural Network with external vocabulary (BETA)"),
        ),
        (
            ALGORITHM_TRANSFORMER_NETWORK_DIET,
            _("Transformer Neural Network with internal vocabulary"),
        ),
        (
            ALGORITHM_TRANSFORMER_NETWORK_DIET_WORD_EMBEDDING,
            _("Transformer Neural Network with word embedding external vocabulary"),
        ),
        (
            ALGORITHM_TRANSFORMER_NETWORK_DIET_BERT,
            _("Transformer Neural Network with BERT word embedding"),
        ),
    ]

    TYPE_CLASSIFIER = "classifier"
    TYPE_CONTENT = "content"
    TYPE_CHOICES = [(TYPE_CLASSIFIER, _("Classifier")), (TYPE_CONTENT, _("Content"))]

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    owner = models.ForeignKey(
        RepositoryOwner, models.CASCADE, related_name="repositories"
    )
    name = models.CharField(
        _("name"), max_length=64, help_text=_("Repository display name")
    )
    slug = models.SlugField(
        _("slug"),
        max_length=32,
        help_text=_("Easy way to found and share repositories"),
    )
    repository_type = models.CharField(
        _("repository type"),
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_CLASSIFIER,
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
        max_length=50,
        choices=ALGORITHM_CHOICES,
        default=ALGORITHM_TRANSFORMER_NETWORK_DIET_BERT,
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

    count_authorizations = models.IntegerField(
        _("Authorization count calculated by celery"), default=0
    )

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
            RepositoryVersionLanguage.objects.filter(
                repository_version__repository=self
            ).update(last_update=timezone.now())

        super(Repository, self).save(force_insert, force_update, using, update_fields)

        self.__algorithm = self.algorithm
        self.__use_competing_intents = self.use_competing_intents
        self.__use_name_entities = self.use_name_entities
        self.__use_analyze_char = self.use_analyze_char

    def have_at_least_one_test_phrase_registered(self, language: str) -> bool:
        return self.evaluations(language=language).count() > 0

    def have_at_least_two_intents_registered(self) -> bool:
        return len(self.intents()) >= 2

    def have_at_least_twenty_examples_for_each_intent(self, language: str) -> bool:
        return all(
            [
                self.examples(language=language).filter(intent__text=intent).count()
                >= 20
                for intent in self.intents()
            ]
        )

    def validate_if_can_run_manual_evaluate(self, language: str) -> None:
        if not self.have_at_least_one_test_phrase_registered(language=language):
            raise ValidationError(
                _("You need to have at least " + "one registered test phrase")
            )

        if not self.have_at_least_two_intents_registered():
            raise ValidationError(
                _("You need to have at least " + "two registered intents")
            )

    def validate_if_can_run_automatic_evaluate(self, language: str) -> None:
        if not self.have_at_least_two_intents_registered():
            raise ValidationError(
                _("You need to have at least " + "two registered intents")
            )

        if not self.have_at_least_twenty_examples_for_each_intent(language=language):
            raise ValidationError(
                _("You need to have at least " + "twenty train phrases for each intent")
            )

    @property
    def nlp_base_url(self) -> str:
        return self.nlp_server if self.nlp_server else settings.BOTHUB_NLP_BASE_URL

    def request_nlp_train(self, user_authorization, data):
        try:  # pragma: no cover
            url = f"{self.nlp_base_url}v2/train/"
            payload = {"repository_version": data.get("repository_version")}
            headers = {"Authorization": f"Bearer {user_authorization.uuid}"}

            r = requests.post(url, json=payload, headers=headers)

            return r  # pragma: no cover

        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_analyze(self, user_authorization, data):
        try:  # pragma: no cover
            url = f"{self.nlp_base_url}v2/parse/"
            payload = {
                "text": data.get("text"),
                "language": data.get("language"),
                "repository_version": data.get("repository_version"),
                "from_backend": True,
            }
            headers = {"Authorization": f"Bearer {user_authorization.uuid}"}
            r = requests.post(url, json=payload, headers=headers)

            return r  # pragma: no cover

        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_debug_parse(self, user_authorization, data):
        try:  # pragma: no cover
            payload = {"text": data.get("text"), "language": data.get("language")}

            repository_version = data.get("repository_version")

            if repository_version:
                payload["repository_version"] = repository_version

            r = requests.post(  # pragma: no cover
                "{}v2/debug_parse/".format(self.nlp_base_url),
                json=payload,
                headers={"Authorization": "Bearer {}".format(user_authorization.uuid)},
            )

            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_words_distribution(self, user_authorization, data):
        try:  # pragma: no cover
            payload = {"language": data.get("language")}

            repository_version = data.get("repository_version")

            if repository_version:
                payload["repository_version"] = repository_version

            r = requests.post(  # pragma: no cover
                "{}v2/words_distribution/".format(self.nlp_base_url),
                json=payload,
                headers={"Authorization": "Bearer {}".format(user_authorization.uuid)},
            )
            return r  # pragma: no cover

        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_manual_evaluate(self, user_authorization, data):
        self.validate_if_can_run_manual_evaluate(language=data.get("language"))

        try:  # pragma: no cover
            payload = {
                "language": data.get("language"),
                "repository_version": data.get("repository_version"),
                "cross_validation": False,
            }
            r = requests.post(
                "{}v2/evaluate/".format(self.nlp_base_url),
                json=payload,
                headers={"Authorization": f"Bearer {user_authorization.uuid}"},
            )

            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_automatic_evaluate(self, user_authorization, data):
        self.validate_if_can_run_automatic_evaluate(language=data.get("language"))

        try:  # pragma: no cover
            payload = {
                "language": data.get("language"),
                "repository_version": data.get("repository_version"),
                "cross_validation": True,
            }
            r = requests.post(
                "{}v2/evaluate/".format(self.nlp_base_url),
                json=payload,
                headers={"Authorization": f"Bearer {user_authorization.uuid}"},
            )

            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def request_nlp_qa(self, user_authorization, data):
        try:  # pragma: no cover
            url = f"{self.nlp_base_url}v2/question-answering/"
            payload = {
                "knowledge_base_id": data.get("knowledge_base_id"),
                "question": data.get("question"),
                "language": data.get("language"),
            }
            headers = {"Authorization": f"Bearer {user_authorization.uuid}"}
            r = requests.post(url, json=payload, headers=headers)

            return r  # pragma: no cover
        except requests.exceptions.ConnectionError:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": status.HTTP_503_SERVICE_UNAVAILABLE},
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def available_languages(self, language=None, queryset=None, version_default=True):
        examples = self.examples(
            language=language, queryset=queryset, version_default=version_default
        )
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

    def current_versions(
        self,
        language=None,
        queryset=None,
        version_default=True,
        repository_version=None,
    ):
        if repository_version:
            return map(
                lambda lang: self.get_specific_version_id(
                    repository_version=repository_version, language=lang
                ),
                self.available_languages(
                    language=language,
                    queryset=queryset,
                    version_default=version_default,
                ),
            )
        return map(
            lambda lang: self.current_version(lang, is_default=version_default),
            self.available_languages(
                language=language, queryset=queryset, version_default=version_default
            ),
        )

    def ready_for_train(
        self, queryset=None, version_default=True, repository_version=None
    ):
        return reduce(
            lambda current, u: u.ready_for_train or current,
            self.current_versions(
                queryset=queryset,
                version_default=version_default,
                repository_version=repository_version,
            ),
            False,
        )

    def languages_warnings(
        self, language=None, queryset=None, version_default=True
    ):  # pragma: no cover
        return dict(
            filter(
                lambda w: len(w[1]) > 0,
                map(
                    lambda u: (u.language, u.warnings),
                    self.current_versions(
                        language=language,
                        queryset=queryset,
                        version_default=version_default,
                    ),
                ),
            )
        )

    def intents(self, queryset=None, version_default=True, repository_version=None):
        intents = (
            self.examples(
                queryset=queryset,
                version_default=version_default,
                repository_version=repository_version,
            )
            if queryset
            else self.examples(
                version_default=version_default, repository_version=repository_version
            )
        )
        return list(set(intents.values_list("intent__text", flat=True)))

    def get_formatted_intents(self):
        intents = (
            self.examples()
            .values("intent__text", "intent__pk")
            .order_by("intent__pk")
            .annotate(examples_count=Count("intent__pk"))
        )

        return [
            {
                "value": intent.get("intent__text"),
                "id": intent.get("intent__pk"),
                "examples__count": intent.get("examples_count"),
            }
            for intent in intents
        ]

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
        self,
        language=None,
        queryset=None,
        version_default=True,
        repository_version=None,
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

        if repository_version:
            query = query.filter(
                repository_version_language__repository_version__id=repository_version
            )
        return query

    def evaluations(
        self, language=None, queryset=None, version_default=True
    ):  # pragma: no cover
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
        base_translations_count = RepositoryTranslatedExample.objects.filter(
            original_example__in=base_examples, language=language
        ).count()

        base_examples_count = base_examples.count()
        base_translations_percentage = (
            base_translations_count
            / (base_examples_count if base_examples_count > 0 else 1)
        ) * 100

        return {
            "is_base_language": is_base_language,
            "examples": {
                "count": examples.count(),
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

        if created:
            repository_version.created_by = self.owner
            repository_version.save()

        repository_version_language, created = RepositoryVersionLanguage.objects.get_or_create(
            repository_version=repository_version, language=language
        )
        return repository_version_language

    def last_trained_update(self, language=None):  # pragma: no cover
        language = language or self.language
        version = self.versions.filter(is_default=True).first()

        if version:
            return version.version_languages.filter(
                language=language, training_end_at__isnull=False
            ).first()
        return RepositoryVersionLanguage.objects.none()

    def get_specific_version_language(self, language=None):  # pragma: no cover
        query = RepositoryVersionLanguage.objects.filter(
            repository_version__repository=self
        )
        if language:
            query = query.filter(language=language)
        return query.first()

    def get_specific_version_id(self, repository_version, language=None):
        query = RepositoryVersionLanguage.objects.filter(
            repository_version__repository=self,
            repository_version__pk=repository_version,
        )
        if language:
            query = query.filter(language=language)

        query = query.first()

        if not query:
            query, created = RepositoryVersionLanguage.objects.get_or_create(
                repository_version=RepositoryVersion.objects.get(pk=repository_version),
                language=language,
            )
        return query

    def get_user_authorization(self, user):
        if user.is_anonymous:
            return RepositoryAuthorization(repository=self)
        get, created = RepositoryAuthorization.objects.get_or_create(
            user=user.repository_owner, repository=self
        )
        return get

    def get_absolute_url(self):
        return "{}dashboard/{}/{}/".format(
            settings.BOTHUB_WEBAPP_BASE_URL, self.owner.nickname, self.slug
        )


class RepositoryVersion(models.Model):
    class Meta:
        verbose_name = _("repository version")
        ordering = ["-is_default"]
        indexes = [
            models.Index(
                name="common_repository_version_idx",
                fields=("created_by", "repository"),
            )
        ]

    name = models.CharField(max_length=40, default="master")
    last_update = models.DateTimeField(_("last update"), auto_now_add=True)
    is_default = models.BooleanField(default=True)
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="versions")
    created_by = models.ForeignKey(
        RepositoryOwner, models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    is_deleted = models.BooleanField(_("is deleted"), default=False)

    @property
    def version_languages(self):
        return RepositoryVersionLanguage.objects.filter(repository_version=self)

    def get_version_language(self, language):
        version_language, created = RepositoryVersionLanguage.objects.get_or_create(
            repository_version=self, language=language
        )
        return version_language

    @classmethod
    def get_migration_types(cls):
        """
        Returns the possible types available for classifiers
        :return:
        """
        from bothub.common.migrate_classifiers import TYPES

        return TYPES

    def current_entities(self, queryset=None, version_default=True):
        return self.entities.filter(
            value__in=self.repository.examples(
                queryset=queryset, version_default=version_default
            )
            .exclude(entities__entity__value__isnull=True)
            .values_list("entities__entity__value", flat=True)
            .distinct()
        )

    def entities_list(self, queryset=None, version_default=None):  # pragma: no cover
        return (
            self.current_entities(queryset=queryset, version_default=version_default)
            .values_list("value", flat=True)
            .distinct()
        )

    @property
    def current_groups(self):
        return self.groups.filter(entities__value__in=self.entities_list()).distinct()

    @property
    def groups_list(self):
        return self.current_groups.values_list("value", flat=True).distinct()

    def other_entities(self, queryset=None, version_default=None):
        return self.current_entities(
            queryset=queryset, version_default=version_default
        ).filter(group__isnull=True)

    @property
    def languages_status(self):
        return dict(
            map(
                lambda language: (language, self.language_status(language)),
                settings.SUPPORTED_LANGUAGES.keys(),
            )
        )

    def language_status(self, language):
        is_base_language = self.repository.language == language
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=self
        )
        examples = self.repository.examples(
            language, queryset=queryset, version_default=self.is_default
        )
        base_examples = self.repository.examples(
            self.repository.language, queryset=queryset, version_default=self.is_default
        )
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
        max_length=50,
        choices=Repository.ALGORITHM_CHOICES,
        default=Repository.ALGORITHM_TRANSFORMER_NETWORK_DIET_BERT,
    )
    repository_version = models.ForeignKey(RepositoryVersion, models.CASCADE)
    training_log = models.TextField(_("training log"), blank=True, editable=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"), null=True)
    total_training_end = models.IntegerField(
        _("total training end"), default=0, blank=False, null=False
    )

    @property
    def examples(self):
        examples = self.repository_version.repository.examples(
            version_default=self.repository_version.is_default
        ).filter(
            models.Q(
                repository_version_language__language=self.language,
                repository_version_language=self,
            )
            | models.Q(
                translations__language=self.language,
                translations__repository_version_language=self,
            )
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

        intents = self.examples.values_list("intent__text", flat=True)

        if "" in intents:
            r.append(_("All examples need have a intent."))

        weak_intents = (
            self.examples.values("intent__text")
            .annotate(intent_count=models.Count("id"))
            .order_by()
            .exclude(intent_count__gte=self.MIN_EXAMPLES_PER_INTENT)
        )
        if weak_intents.exists():
            for i in weak_intents:
                r.append(
                    _(
                        'The "{}" intention has only {} sentence\nAdd 1 more sentence to that intention (minimum is {})'
                    ).format(
                        i.get("intent__text"),
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
                    _(
                        'The entity "{}" has only {} sentence\nAdd 1 more sentence to that entity (minimum is {})'
                    ).format(
                        e.get("entities__entity__value"),
                        e.get("entities_count"),
                        self.MIN_EXAMPLES_PER_ENTITY,
                    )
                )

        return r

    @property
    def ready_for_train(self):
        if len(self.requirements_to_train) > 0:
            return False

        if self.training_end_at is not None and self.last_update is not None:
            if self.last_update <= self.training_end_at:
                return False

        if not self.added.exists() and not self.translated_added.exists():
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
                    "You only added 1 intention\nAdd 1 more intention (it is necessary to have at least {} intentions for the algorithm to identify)"
                ).format(self.RECOMMENDED_INTENTS)
            )
        return w

    @property
    def use_language_model_featurizer(self):
        return self.algorithm != Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL

    def __str__(self):
        return "Repository Version Language #{}".format(self.id)  # pragma: no cover

    def validate_init_train(self, by=None, from_nlp=False):
        if (
            self.queues.filter(
                Q(status=RepositoryQueueTask.STATUS_PENDING)
                | Q(status=RepositoryQueueTask.STATUS_PROCESSING)
            ).filter(Q(type_processing=RepositoryQueueTask.TYPE_PROCESSING_TRAINING))
            and not from_nlp
        ):
            raise RepositoryUpdateAlreadyStartedTraining()
        if by:
            authorization = self.repository_version.repository.get_user_authorization(
                by
            )
            if not authorization.can_write:
                raise TrainingNotAllowed()

    def start_training(self, created_by):
        self.validate_init_train(created_by, from_nlp=True)
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

    def create_task(self, id_queue, from_queue, type_processing):
        return RepositoryQueueTask.objects.create(
            repositoryversionlanguage=self,
            id_queue=id_queue,
            from_queue=from_queue,
            type_processing=type_processing,
        )

    def get_trainer(self, rasa_version):
        trainer, created = RepositoryNLPTrain.objects.get_or_create(
            repositoryversionlanguage=self, rasa_version=rasa_version
        )
        return trainer

    def update_trainer(self, bot_data, rasa_version):
        trainer, created = RepositoryNLPTrain.objects.get_or_create(
            repositoryversionlanguage=self, rasa_version=rasa_version
        )
        trainer.bot_data = bot_data
        trainer.save(update_fields=["bot_data"])

    def save_training(self, bot_data, rasa_version):
        last_time = timezone.now()

        self.training_end_at = last_time
        self.last_update = last_time
        self.update_trainer(bot_data, rasa_version=rasa_version)
        self.total_training_end += 1
        self.save(
            update_fields=["total_training_end", "training_end_at", "last_update"]
        )

    @property
    def get_bot_data(self):
        return self.get_trainer(settings.BOTHUB_NLP_RASA_VERSION)

    def train_fail(self):
        self.failed_at = timezone.now()
        self.save(update_fields=["failed_at"])


class RepositoryNLPTrain(models.Model):
    class Meta:
        verbose_name = _("repository nlp train")
        unique_together = ["repositoryversionlanguage", "rasa_version"]

    bot_data = models.TextField(_("bot data"), blank=True)
    repositoryversionlanguage = models.ForeignKey(
        RepositoryVersionLanguage, models.CASCADE, related_name="trainers"
    )
    rasa_version = models.CharField(_("Rasa Version Code"), max_length=20)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)


class RepositoryQueueTask(models.Model):
    class Meta:
        verbose_name = _("repository nlp queue train")

    QUEUE_AIPLATFORM = 0
    QUEUE_CELERY = 1
    QUEUE_CHOICES = [(QUEUE_AIPLATFORM, _("Ai Platform")), (QUEUE_CELERY, _("Celery"))]

    STATUS_PENDING = 0
    STATUS_PROCESSING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_SUCCESS, _("Success")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_FAILED, _("Failed")),
    ]
    TYPE_PROCESSING_TRAINING = 0
    TYPE_PROCESSING_AUTO_TRANSLATE = 1
    TYPE_PROCESSING_EVALUATE_CROSS_VALIDATION = 2
    TYPE_PROCESSING_CHOICES = [
        (TYPE_PROCESSING_TRAINING, _("NLP Tranining")),
        (TYPE_PROCESSING_AUTO_TRANSLATE, _("Repository Auto Translation")),
        (TYPE_PROCESSING_EVALUATE_CROSS_VALIDATION, _("Evaluate Cross Validation")),
    ]

    repositoryversionlanguage = models.ForeignKey(
        RepositoryVersionLanguage, models.CASCADE, related_name="queues"
    )
    id_queue = models.TextField(_("id queue"))
    from_queue = models.PositiveIntegerField(
        _("From Queue NLP"), choices=QUEUE_CHOICES, default=QUEUE_CELERY
    )
    status = models.PositiveIntegerField(
        _("Status Queue NLP"), choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    ml_units = models.FloatField(_("Machine Learning Units AiPlatform"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    end_training = models.DateTimeField(_("end training"), null=True)
    type_processing = models.PositiveIntegerField(
        _("Type Processing"), choices=TYPE_PROCESSING_CHOICES
    )


class RepositoryNLPLog(models.Model):
    class Meta:
        verbose_name = _("repository nlp logs")
        indexes = [
            models.Index(
                name="common_repo_nlp_log_idx",
                fields=("repository_version_language", "user"),
                condition=Q(from_backend=False),
            )
        ]
        ordering = ["-created_at"]

    text = models.TextField(help_text=_("Text"))
    user_agent = models.TextField(help_text=_("User Agent"))
    from_backend = models.BooleanField()
    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        related_name="nlp_logs",
        editable=False,
        null=True,
    )
    nlp_log = models.TextField(help_text=_("NLP Log"), blank=True)
    user = models.ForeignKey(RepositoryOwner, models.CASCADE)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def intents(self, repository_nlp_log):
        return RepositoryNLPLogIntent.objects.filter(
            repository_nlp_log=repository_nlp_log
        ).order_by("-is_default")


class RepositoryNLPLogIntent(models.Model):
    class Meta:
        verbose_name = _("repository nlp logs intent")

    intent = models.TextField(help_text=_("Intent"))
    confidence = models.FloatField(help_text=_("Confidence"))
    is_default = models.BooleanField(help_text=_("is default, intent selected"))
    repository_nlp_log = models.ForeignKey(
        RepositoryNLPLog,
        models.CASCADE,
        editable=False,
        null=True,
        related_name="repository_nlp_log",
    )


class RepositoryReports(models.Model):
    class Meta:
        verbose_name = _("repository report")
        verbose_name_plural = _("repository reports")
        unique_together = ["repository_version_language", "user", "report_date"]

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        editable=False,
        related_name="repository_reports",
    )
    user = models.ForeignKey(RepositoryOwner, models.CASCADE)
    count_reports = models.IntegerField(default=0)
    report_date = models.DateField(_("report date"))


class RepositoryIntent(models.Model):
    class Meta:
        verbose_name = _("repository intent")
        verbose_name_plural = _("repository intents")
        unique_together = ["repository_version", "text"]

    repository_version = models.ForeignKey(
        RepositoryVersion, models.CASCADE, related_name="version_intents"
    )
    text = models.CharField(
        _("intent"),
        max_length=64,
        default="no_intent",
        help_text=_("Example intent reference"),
        validators=[validate_item_key],
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def __str__(self):
        return self.text


class RepositoryExample(models.Model):
    class Meta:
        verbose_name = _("repository example")
        verbose_name_plural = _("repository examples")
        ordering = ["-created_at"]

    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage, models.CASCADE, related_name="added", editable=False
    )
    text = models.TextField(_("text"), help_text=_("Example text"))
    intent = models.ForeignKey(RepositoryIntent, models.CASCADE)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"))
    is_corrected = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()
        self.repository_version_language.last_update = timezone.now()
        self.repository_version_language.save(update_fields=["last_update"])
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

    def delete(self, using=None, keep_parents=False):
        self.repository_version_language.last_update = timezone.now()
        self.repository_version_language.save(update_fields=["last_update"])

        instance = super().delete(using, keep_parents)

        repository_version = self.repository_version_language.repository_version

        RepositoryEntity.objects.exclude(
            pk__in=RepositoryExampleEntity.objects.filter(
                repository_example__repository_version_language__repository_version=repository_version
            ).values("entity")
        ).filter(repository_version=repository_version).delete()

        return instance


class RepositoryTranslatedExampleManager(models.Manager):
    def create(
        self,
        *args,
        original_example=None,
        language=None,
        clone_repository=False,
        **kwargs,
    ):
        if clone_repository:
            return super().create(
                *args, original_example=original_example, language=language, **kwargs
            )

        return super().create(
            *args,
            repository_version_language=original_example.repository_version_language.repository_version.get_version_language(
                language
            ),
            original_example=original_example,
            language=language,
            **kwargs,
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
        null=True,
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

    def save(self, *args, **kwargs):
        self.original_example.last_update = timezone.now()
        self.original_example.save(update_fields=["last_update"])
        self.repository_version_language.last_update = timezone.now()
        self.repository_version_language.save(update_fields=["last_update"])
        super(RepositoryTranslatedExample, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.original_example.last_update = timezone.now()
        self.original_example.save(update_fields=["last_update"])
        self.repository_version_language.last_update = timezone.now()
        self.repository_version_language.save(update_fields=["last_update"])
        super(RepositoryTranslatedExample, self).delete(using, keep_parents)

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


class RepositoryEntityGroup(models.Model):
    class Meta:
        unique_together = ["repository_version", "value"]

    repository_version = models.ForeignKey(
        RepositoryVersion, models.CASCADE, related_name="groups"
    )
    value = models.CharField(
        _("group"),
        max_length=64,
        validators=[validate_item_key, can_t_be_other],
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def examples(self, queryset=None, version_default=None):  # pragma: no cover
        return self.repository_version.repository.examples(
            queryset=queryset, version_default=version_default
        ).filter(entities__entity__group=self)

    def delete(self, using=None, keep_parents=False):
        """
            Before deleting the group it updates all the entities and places
            it as not grouped so that they are not deleted
        """
        self.entities.filter(
            repository_version=self.repository_version, group=self
        ).update(group=None)
        return super().delete(using=using, keep_parents=keep_parents)


class RepositoryEntityQueryset(models.QuerySet):
    """
    Customized QuerySet created on account of evaluate, when creating a test phrase in evaluate, it sends to the model
     entity of evaluate the reference of the entities in the examples, it was done just when there is no entity,
     in evaluate it does not create
    """

    def get(self, create_entity=True, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            if not create_entity:
                raise self.model.DoesNotExist  # pragma: no cover
            return super().get(*args, **kwargs)


class RepositoryEntityManager(models.Manager):
    def get_queryset(self):
        return RepositoryEntityQueryset(self.model, using=self._db)


class RepositoryEntity(models.Model):
    class Meta:
        unique_together = ["repository_version", "value"]

    repository_version = models.ForeignKey(
        RepositoryVersion,
        models.CASCADE,
        related_name="entities",
        null=True,
        blank=True,
    )
    value = models.CharField(
        _("entity"),
        max_length=64,
        help_text=_("Entity name"),
        validators=[validate_item_key],
    )
    group = models.ForeignKey(
        RepositoryEntityGroup,
        on_delete=models.CASCADE,
        related_name="entities",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    objects = RepositoryEntityManager()

    def set_group(self, value):
        if not value:
            self.group = None
        else:
            self.group, created = RepositoryEntityGroup.objects.get_or_create(
                repository_version=self.repository_version, value=value
            )


class EntityBaseQueryset(models.QuerySet):  # pragma: no cover
    def create(self, entity, **kwargs):
        if type(entity) is not RepositoryEntity:
            instance = self.model(**kwargs)
            if "repository_evaluate_id" in instance.__dict__:
                evaluate = instance.repository_evaluate
                repository_version = (
                    evaluate.repository_version_language.repository_version
                )
            elif "evaluate_result_id" in instance.__dict__:
                result = instance.evaluate_result
                repository_version = (
                    result.repository_version_language.repository_version
                )
            else:
                repository_version = (
                    instance.example.repository_version_language.repository_version
                )

            entity, created = RepositoryEntity.objects.get_or_create(
                repository_version=repository_version, value=entity
            )

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
        if self.entity.group is None or self.entity.group == "":
            return {
                "start": self.start,
                "end": self.end,
                "value": self.value,
                "entity": self.entity.value,
            }
        return {
            "start": self.start,
            "end": self.end,
            "value": self.value,
            "entity": self.entity.value,
            "role": self.entity.group.value,
        }

    @property
    def to_dict(self):
        return self.get_rasa_nlu_data()

    def get_example(self):
        pass  # pragma: no cover

    def get_rasa_nlu_data(self, group_as_entity=False):
        return {
            "start": self.start,
            "end": self.end,
            "entity": self.entity.group.value if group_as_entity else self.entity.value,
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
    LEVEL_TRANSLATE = 4

    ROLE_NOT_SETTED = 0
    ROLE_USER = 1
    ROLE_CONTRIBUTOR = 2
    ROLE_ADMIN = 3
    ROLE_TRANSLATE = 4

    ROLE_CHOICES = [
        (ROLE_NOT_SETTED, _("not set")),
        (ROLE_USER, _("user")),
        (ROLE_CONTRIBUTOR, _("contributor")),
        (ROLE_ADMIN, _("admin")),
        (ROLE_TRANSLATE, _("translate")),
    ]

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(RepositoryOwner, models.CASCADE, null=True)
    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="authorizations"
    )
    role = models.PositiveIntegerField(
        _("role"), choices=ROLE_CHOICES, default=ROLE_NOT_SETTED
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_owner:
            self.role = RepositoryAuthorization.ROLE_ADMIN
        super(RepositoryAuthorization, self).save(*args, **kwargs)

    @property
    def get_role(self):
        if self.role < RepositoryAuthorization.ROLE_USER and self.user:
            org = (
                self.user.organization_user_authorization.exclude(
                    role=RepositoryAuthorization.ROLE_NOT_SETTED
                )
                .filter(
                    Q(
                        organization__in=RepositoryAuthorization.objects.filter(
                            repository=self.repository,
                            user__in=self.user.organization_user_authorization.exclude(
                                role=OrganizationAuthorization.ROLE_NOT_SETTED
                            ).values_list("organization", flat=True),
                        )
                        .exclude(role=OrganizationAuthorization.ROLE_NOT_SETTED)
                        .order_by("-role")
                        .values_list("user")
                    )
                )
                .order_by("-role")
            ).first()
            return org.role if org else RepositoryAuthorization.LEVEL_NOTHING
        return self.role

    @property
    def level(self):
        role = self.get_role

        if role == RepositoryAuthorization.ROLE_NOT_SETTED:
            if self.repository.is_private:
                return RepositoryAuthorization.LEVEL_NOTHING
            return RepositoryAuthorization.LEVEL_READER

        if role == RepositoryAuthorization.ROLE_USER:
            return RepositoryAuthorization.LEVEL_READER

        if role == RepositoryAuthorization.ROLE_CONTRIBUTOR:
            return RepositoryAuthorization.LEVEL_CONTRIBUTOR

        if role == RepositoryAuthorization.ROLE_ADMIN:
            return RepositoryAuthorization.LEVEL_ADMIN

        if role == RepositoryAuthorization.ROLE_TRANSLATE:
            return RepositoryAuthorization.LEVEL_TRANSLATE

        return RepositoryAuthorization.LEVEL_NOTHING  # pragma: no cover

    @property
    def can_read(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_READER,
            RepositoryAuthorization.LEVEL_CONTRIBUTOR,
            RepositoryAuthorization.LEVEL_ADMIN,
            RepositoryAuthorization.LEVEL_TRANSLATE,
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
    def can_translate(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_CONTRIBUTOR,
            RepositoryAuthorization.LEVEL_ADMIN,
            RepositoryAuthorization.LEVEL_TRANSLATE,
        ]

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
            [self.user.user.email],
            html_message=render_to_string("common/emails/new_role.html", context),
        )


class RepositoryVote(models.Model):
    class Meta:
        verbose_name = _("repository vote")
        verbose_name_plural = _("repository votes")
        unique_together = ["user", "repository"]

    user = models.ForeignKey(
        RepositoryOwner, models.CASCADE, related_name="repository_votes"
    )
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="votes")
    created = models.DateTimeField(editable=False, default=timezone.now)


class RepositoryMigrate(models.Model):
    class Meta:
        verbose_name = _("repository migrate")
        verbose_name_plural = _("repository migrates")

    user = models.ForeignKey(RepositoryOwner, models.CASCADE)
    repository_version = models.ForeignKey(
        RepositoryVersion, models.DO_NOTHING, related_name="repository_migrate"
    )
    language = models.CharField(
        _("language"), max_length=5, validators=[languages.validate_language]
    )
    auth_token = models.TextField()
    classifier = models.CharField(
        _("classifier"),
        max_length=16,
        validators=[utils.validate_classifier],
        editable=False,
    )
    created = models.DateTimeField(editable=False, auto_now_add=True)


class RequestRepositoryAuthorization(models.Model):
    class Meta:
        unique_together = ["user", "repository"]

    user = models.ForeignKey(RepositoryOwner, models.CASCADE, related_name="requests")
    repository = models.ForeignKey(Repository, models.CASCADE, related_name="requests")
    text = models.CharField(_("text"), max_length=250)
    approved_by = models.ForeignKey(
        RepositoryOwner, models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, editable=False
    )

    def send_new_request_email_to_admins(self):
        try:
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
                    [admin.user.user.email],
                    html_message=render_to_string(
                        "common/emails/new_request.html", context
                    ),
                )
        except AttributeError:
            pass

    def send_request_rejected_email(self):
        try:
            if not settings.SEND_EMAILS:
                return False  # pragma: no cover
            context = {
                "repository_name": self.repository.name,
                "base_url": settings.BASE_URL,
            }
            if not self.user.is_organization:
                send_mail(
                    _("Access denied to {}").format(self.repository.name),
                    render_to_string("common/emails/request_rejected.txt", context),
                    None,
                    [self.user.user.email],
                    html_message=render_to_string(
                        "common/emails/request_rejected.html", context
                    ),
                )
        except AttributeError:
            pass

    def send_request_approved_email(self):
        try:
            if not settings.SEND_EMAILS:
                return False  # pragma: no cover
            context = {
                "base_url": settings.BASE_URL,
                "admin_name": self.approved_by.name,
                "repository_name": self.repository.name,
            }
            if not self.user.is_organization:
                send_mail(
                    _("Authorization Request Approved to {}").format(
                        self.repository.name
                    ),
                    render_to_string("common/emails/request_approved.txt", context),
                    None,
                    [self.user.user.email],
                    html_message=render_to_string(
                        "common/emails/request_approved.html", context
                    ),
                )
        except AttributeError:
            pass


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

    support = models.FloatField(null=True)

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
        null=True,
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

    cross_validation = models.BooleanField(_("cross validation"), default=False)

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


class RepositoryTranslator(models.Model):
    class Meta:
        verbose_name = _("repository translator")
        verbose_name_plural = _("repository translators")

    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4, editable=False
    )
    repository_version_language = models.ForeignKey(
        RepositoryVersionLanguage,
        models.CASCADE,
        related_name="translator",
        editable=False,
    )
    language = models.CharField(
        _("language"),
        max_length=5,
        validators=[languages.validate_language],
        editable=False,
    )
    created_by = models.ForeignKey(RepositoryOwner, models.CASCADE)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)


class RepositoryScore(models.Model):
    class Meta:
        unique_together = ["repository"]
        verbose_name = _("repository score")
        verbose_name_plural = _("repository scores")

    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="repository_score", editable=False
    )
    intents_balance_score = models.FloatField(default=0.0)
    intents_balance_recommended = models.TextField(null=True)
    intents_size_score = models.FloatField(default=0.0)
    intents_size_recommended = models.TextField(null=True)
    evaluate_size_score = models.FloatField(default=0.0)
    evaluate_size_recommended = models.TextField(null=True)


class QAKnowledgeBase(models.Model):
    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="knowledge_bases"
    )
    title = models.CharField(
        _("title"), max_length=64, help_text=_("Knowledge Base title")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"), auto_now=True)


class QAContext(models.Model):
    knowledge_base = models.ForeignKey(
        QAKnowledgeBase, on_delete=models.CASCADE, related_name="contexts"
    )
    text = models.TextField(_("text"), help_text=_("QA context text"), max_length=25000)
    language = models.CharField(
        _("language"),
        max_length=5,
        help_text=_("Knowledge Base language"),
        validators=[languages.validate_language],
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"), auto_now=True)

    class Meta:
        unique_together = ("knowledge_base", "language")


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


@receiver(models.signals.post_save, sender=RepositoryNLPLog)
def save_log_nlp(instance, created, **kwargs):
    if created:
        report, created = RepositoryReports.objects.get_or_create(
            repository_version_language=instance.repository_version_language,
            user=instance.user,
            report_date=timezone.now().date(),
        )
        report.count_reports += 1
        report.save(update_fields=["count_reports"])
