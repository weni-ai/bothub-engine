import uuid
import base64
import requests

from functools import reduce

from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator, _lazy_re_compile

from bothub.authentication.models import User

from . import languages
from .exceptions import RepositoryUpdateAlreadyStartedTraining
from .exceptions import RepositoryUpdateAlreadyTrained
from .exceptions import TrainingNotAllowed
from .exceptions import DoesNotHaveTranslation


entity_and_intent_regex = _lazy_re_compile(r'^[-a-z0-9_]+\Z')
validate_entity_and_intent = RegexValidator(
    entity_and_intent_regex,
    _('Enter a valid value consisting of lowercase letters, numbers, ' +
        'underscores or hyphens.'),
    'invalid'
)


class RepositoryCategory(models.Model):
    class Meta:
        verbose_name = _('repository category')
        verbose_name_plural = _('repository categories')

    name = models.CharField(
        _('name'),
        max_length=32)

    def __str__(self):
        return self.name  # pragma: no cover


class RepositoryQuerySet(models.QuerySet):
    def publics(self):
        return self.filter(is_private=False)

    def order_by_relevance(self):
        return self \
            .annotate(votes_summ=models.Sum('votes__vote')) \
            .annotate(examples_sum=models.Sum('updates__added')) \
            .order_by('-votes_summ', '-examples_sum', '-created_at')


class RepositoryManager(models.Manager):
    def get_queryset(self):
        return RepositoryQuerySet(self.model, using=self._db)


class Repository(models.Model):
    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')
        unique_together = ['owner', 'slug']

    CATEGORIES_HELP_TEXT = _('Categories for approaching repositories with ' +
                             'the same purpose')
    DESCRIPTION_HELP_TEXT = _('Tell what your bot do!')

    uuid = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    owner = models.ForeignKey(
        User,
        models.CASCADE)
    name = models.CharField(
        _('name'),
        max_length=64,
        help_text=_('Repository display name'))
    slug = models.SlugField(
        _('slug'),
        max_length=32,
        help_text=_('Easy way to found and share repositories'))
    language = models.CharField(
        _('language'),
        choices=languages.LANGUAGE_CHOICES,
        max_length=2,
        help_text=_('Repository\'s examples language. The examples can be ' +
                    'translated to other languages.'))
    categories = models.ManyToManyField(
        RepositoryCategory,
        help_text=CATEGORIES_HELP_TEXT)
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=DESCRIPTION_HELP_TEXT)
    is_private = models.BooleanField(
        _('private'),
        default=False,
        help_text=_('Your repository can be private, only you can see and' +
                    ' use, or can be public and all community can see and ' +
                    'use.'))
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

    objects = RepositoryManager()

    nlp_train_url = '{}train/'.format(settings.BOTHUB_NLP_BASE_URL)
    nlp_analyze_url = '{}parse/'.format(settings.BOTHUB_NLP_BASE_URL)

    @classmethod
    def request_nlp_train(cls, user_authorization):
        r = requests.post(  # pragma: no cover
            cls.nlp_train_url,
            data={},
            headers={'Authorization': 'Bearer {}'.format(
                user_authorization.uuid)})
        return r  # pragma: no cover

    @classmethod
    def request_nlp_analyze(cls, user_authorization, data):
        r = requests.post(  # pragma: no cover
            cls.nlp_analyze_url,
            data={
                'text': data.get('text'),
                'language': data.get('language'),
            },
            headers={'Authorization': 'Bearer {}'.format(
                user_authorization.uuid)})
        return r  # pragma: no cover

    @property
    def available_languages(self):
        examples = self.examples()
        examples_languages = examples.values_list(
            'repository_update__language',
            flat=True)
        translations_languages = examples.annotate(
            translations_count=models.Count('translations')).filter(
                translations_count__gt=0).values_list(
                    'translations__language',
                    flat=True)
        return list(set(
            [self.language] +
            list(examples_languages) +
            list(translations_languages)))

    @property
    def languages_status(self):
        return dict(
            map(
                lambda language: (
                    language,
                    self.language_status(language)),
                languages.SUPPORTED_LANGUAGES,
            ))

    @property
    def ready_for_train(self):
        updates = self.updates.filter(training_started_at=None)

        if RepositoryExample.objects.filter(
                models.Q(repository_update__in=updates) |
                models.Q(deleted_in__in=updates)).exists():
            return True

        if RepositoryTranslatedExample.objects.filter(
                repository_update__in=updates).exists():
            return True

        return False

    @property
    def votes_sum(self):
        return self.votes.aggregate(
            votes_sum=models.Sum('vote')).get('votes_sum')

    def examples(self, language=None, deleted=True, queryset=None):
        if queryset is None:
            queryset = RepositoryExample.objects
        query = queryset.filter(
            repository_update__repository=self)
        if language:
            query = query.filter(
                repository_update__language=language)
        if deleted:
            return query.exclude(deleted_in__isnull=False)
        return query

    def language_status(self, language):
        is_base_language = self.language == language
        examples = self.examples(language)
        base_examples = self.examples(self.language)
        base_translations = RepositoryTranslatedExample.objects.filter(
            original_example__in=base_examples,
            language=language)

        examples_count = examples.count()
        base_examples_count = base_examples.count()
        base_translations_count = base_translations.count()
        base_translations_percentage = (
            base_translations_count / (
                base_examples_count if base_examples_count > 0 else 1)) * 100

        return {
            'is_base_language': is_base_language,
            'examples': {
                'count': examples_count,
                'entities': list(
                    set(
                        filter(
                            lambda x: x,
                            examples.values_list(
                                'entities__entity',
                                flat=True).distinct()))),
            },
            'base_translations': {
                'count': base_translations_count,
                'percentage': base_translations_percentage,
            },
        }

    def current_update(self, language=None):
        language = language or self.language
        repository_update, created = self.updates.get_or_create(
            language=language,
            training_started_at=None)
        return repository_update

    def last_trained_update(self, language=None):
        language = language or self.language
        return self.updates.filter(
            language=language,
            by__isnull=False).first()

    def get_user_authorization(self, user):
        if user.is_anonymous:
            return RepositoryAuthorization(repository=self)
        get, created = RepositoryAuthorization.objects.get_or_create(
            user=user,
            repository=self)
        return get


class RepositoryUpdate(models.Model):
    class Meta:
        verbose_name = _('repository update')
        verbose_name_plural = _('repository updates')
        ordering = ['-created_at']

    repository = models.ForeignKey(
        Repository,
        models.CASCADE,
        related_name='updates')
    language = models.CharField(
        _('language'),
        choices=languages.LANGUAGE_CHOICES,
        max_length=2)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)
    bot_data = models.TextField(
        _('bot data'),
        blank=True,
        editable=False)
    by = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True)
    training_started_at = models.DateTimeField(
        _('training started at'),
        blank=True,
        null=True)
    trained_at = models.DateTimeField(
        _('trained at'),
        blank=True,
        null=True)
    failed_at = models.DateTimeField(
        _('failed at'),
        blank=True,
        null=True)

    @property
    def examples(self):
        examples = self.repository.examples(deleted=False).filter(
            models.Q(repository_update__language=self.language) |
            models.Q(translations__language=self.language))
        if self.training_started_at:
            t_started_at = self.training_started_at
            examples = examples.exclude(
                models.Q(repository_update__created_at__gt=t_started_at) |
                models.Q(deleted_in=self) |
                models.Q(deleted_in__training_started_at__lt=t_started_at))
        else:
            examples = examples.exclude(deleted_in=self)
        return examples

    @property
    def ready_for_train(self):
        if self.added.exists():
            return True
        if self.translated_added.exists():
            return True
        if self.deleted.exists():
            return True
        return False

    def start_training(self, by):
        if self.trained_at:
            raise RepositoryUpdateAlreadyTrained()
        if self.training_started_at:
            raise RepositoryUpdateAlreadyStartedTraining()

        authorization = self.repository.get_user_authorization(by)
        if not authorization.can_write:
            raise TrainingNotAllowed()

        self.by = by
        self.training_started_at = timezone.now()
        self.save(
            update_fields=[
                'by',
                'training_started_at',
            ])

    def save_training(self, bot_data):
        if self.trained_at:
            raise RepositoryUpdateAlreadyTrained()

        self.trained_at = timezone.now()
        self.bot_data = base64.b64encode(bot_data).decode('utf8')
        self.save(
            update_fields=[
                'trained_at',
                'bot_data',
            ])

    def get_bot_data(self):
        return base64.b64decode(self.bot_data)

    def train_fail(self):
        self.failed_at = timezone.now()  # pragma: no cover
        self.save(  # pragma: no cover
            update_fields=[
                'failed_at',
            ])


class RepositoryExample(models.Model):
    class Meta:
        verbose_name = _('repository example')
        verbose_name_plural = _('repository examples')
        ordering = ['-created_at']

    repository_update = models.ForeignKey(
        RepositoryUpdate,
        models.CASCADE,
        related_name='added',
        editable=False)
    deleted_in = models.ForeignKey(
        RepositoryUpdate,
        models.CASCADE,
        related_name='deleted',
        blank=True,
        null=True)
    text = models.TextField(
        _('text'),
        help_text=_('Example text'))
    intent = models.CharField(
        _('intent'),
        max_length=64,
        blank=True,
        help_text=_('Example intent reference'),
        validators=[validate_entity_and_intent])
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

    @property
    def language(self):
        return self.repository_update.language

    def has_valid_entities(self, language=None):
        if not language or language == self.repository_update.language:
            return True
        return self.get_translation(language).has_valid_entities

    def get_translation(self, language):
        try:
            return self.translations.get(language=language)
        except RepositoryTranslatedExample.DoesNotExist:
            raise DoesNotHaveTranslation()

    def get_text(self, language=None):
        if not language or language == self.repository_update.language:
            return self.text
        return self.get_translation(language).text

    def get_entities(self, language):
        if not language or language == self.repository_update.language:
            return self.entities.all()
        return self.get_translation(language).entities.all()

    def rasa_nlu_data(self, language):
        return {
            'text': self.get_text(language),
            'intent': self.intent,
            'entities': [
                entity.rasa_nlu_data for entity in self.get_entities(
                    language)],
        }

    def delete(self):
        self.deleted_in = self.repository_update.repository.current_update(
            self.repository_update.language)
        self.save(update_fields=['deleted_in'])


class RepositoryTranslatedExampleManager(models.Manager):
    def create(self, *args, original_example=None, language=None, **kwargs):
        repository = original_example.repository_update.repository
        return super().create(
            *args,
            repository_update=repository.current_update(language),
            original_example=original_example,
            language=language,
            **kwargs)


class RepositoryTranslatedExample(models.Model):
    class Meta:
        verbose_name = _('repository translated example')
        verbose_name_plural = _('repository translated examples')
        unique_together = ['original_example', 'language']
        ordering = ['-created_at']

    repository_update = models.ForeignKey(
        RepositoryUpdate,
        models.CASCADE,
        related_name='translated_added',
        editable=False)
    original_example = models.ForeignKey(
        RepositoryExample,
        models.CASCADE,
        related_name='translations',
        editable=False,
        help_text=_('Example object'))
    language = models.CharField(
        _('language'),
        choices=languages.LANGUAGE_CHOICES,
        max_length=2,
        help_text=_('Translation language'))
    text = models.TextField(
        _('text'),
        help_text=_('Translation text'))
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

    objects = RepositoryTranslatedExampleManager()

    def entities_list_lambda_sort(item):
        return item.get('entity')

    @classmethod
    def same_entities_validator(cls, a, b):
        a_len = len(a)
        if a_len != len(b):
            return False
        a_sorted = sorted(
            a,
            key=cls.entities_list_lambda_sort)
        b_sorted = sorted(
            b,
            key=cls.entities_list_lambda_sort)
        for i in range(a_len):
            if a_sorted[i].get('entity') != b_sorted[i].get('entity'):
                return False
        return True

    @classmethod
    def count_entities(cls, entities_list, to_str=False):
        r = {}
        reduce(
            lambda current, next: current.update({
                next.get('entity'): current.get('entity', 0) + 1,
            }),
            entities_list,
            r)
        if to_str:
            r = ', '.join(map(
                lambda x: '{} {}'.format(x[1], x[0]),
                r.items())) if entities_list else 'no entities'
        return r

    @property
    def has_valid_entities(self):
        original_entities = self.original_example.entities.all()
        my_entities = self.entities.all()
        return RepositoryTranslatedExample.same_entities_validator(
            list(map(lambda x: x.to_dict, original_entities)),
            list(map(lambda x: x.to_dict, my_entities)))


class EntityBase(models.Model):
    class Meta:
        verbose_name = _('repository example entity')
        verbose_name_plural = _('repository example entities')
        abstract = True

    start = models.PositiveIntegerField(
        _('start'),
        help_text=_('Start index of entity value in example text'))
    end = models.PositiveIntegerField(
        _('end'),
        help_text=_('End index of entity value in example text'))
    entity = models.CharField(
        _('entity'),
        max_length=64,
        help_text=_('Entity name'),
        validators=[validate_entity_and_intent])
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

    @property
    def value(self):
        return self.get_example().text[self.start:self.end]

    @property
    def rasa_nlu_data(self):
        return {
            'start': self.start,
            'end': self.end,
            'value': self.value,
            'entity': self.entity,
        }

    @property
    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'entity': self.entity,
        }

    def get_example(self):
        pass  # pragma: no cover


class RepositoryExampleEntity(EntityBase):
    repository_example = models.ForeignKey(
        RepositoryExample,
        models.CASCADE,
        related_name='entities',
        editable=False,
        help_text=_('Example object'))

    def get_example(self):
        return self.repository_example


class RepositoryTranslatedExampleEntity(EntityBase):
    repository_translated_example = models.ForeignKey(
        RepositoryTranslatedExample,
        models.CASCADE,
        related_name='entities',
        editable=False,
        help_text=_('Translated example object'))

    def get_example(self):
        return self.repository_translated_example


class RepositoryAuthorization(models.Model):
    class Meta:
        verbose_name = _('repository authorization')
        verbose_name_plural = _('repository authorizations')
        unique_together = ['user', 'repository']

    LEVEL_NOTHING = 0
    LEVEL_READER = 1
    LEVEL_ADMIN = 2

    uuid = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    user = models.ForeignKey(
        User,
        models.CASCADE)
    repository = models.ForeignKey(
        Repository,
        models.CASCADE)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

    @property
    def level(self):
        try:
            user = self.user
        except User.DoesNotExist:
            user = None

        if user and self.repository.owner == user:
            return RepositoryAuthorization.LEVEL_ADMIN
        if self.repository.is_private:
            return RepositoryAuthorization.LEVEL_NOTHING
        return RepositoryAuthorization.LEVEL_READER

    @property
    def can_read(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_READER,
            RepositoryAuthorization.LEVEL_ADMIN,
        ]

    @property
    def can_contribute(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_ADMIN,
        ]

    @property
    def can_write(self):
        return self.level in [
            RepositoryAuthorization.LEVEL_ADMIN,
        ]

    @property
    def is_admin(self):
        return self.level == RepositoryAuthorization.LEVEL_ADMIN


class RepositoryVote(models.Model):
    UP_VOTE = 1
    DOWN_VOTE = -1
    NEUTRAL_VOTE = 0
    VOTE_CHOICES = [
        (UP_VOTE, _('Up'),),
        (DOWN_VOTE, _('Down')),
        (NEUTRAL_VOTE, _('Neutral')),
    ]

    class Meta:
        verbose_name = _('repository vote')
        verbose_name_plural = _('repository votes')
        unique_together = [
            'user',
            'repository',
        ]

    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='repository_votes')
    repository = models.ForeignKey(
        Repository,
        models.CASCADE,
        related_name='votes')
    vote = models.IntegerField(
        _('vote'),
        choices=VOTE_CHOICES)
