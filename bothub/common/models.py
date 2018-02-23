import uuid

from django.db import models
from django.utils.translation import gettext as _

from bothub.authentication.models import User


class Repository(models.Model):
    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')

    uuid = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    owner = models.ForeignKey(
        User,
        models.CASCADE)
    slug = models.CharField(
        _('slug'),
        unique=True,
        max_length=32)
    is_private = models.BooleanField(
        _('private'),
        default=False)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)
    
    @property
    def current_update(self):
        repository_update, created = self.updates.get_or_create(training_started_at=None)
        return repository_update


class RepositoryUpdate(models.Model):
    class Meta:
        verbose_name = _('repository update')
        verbose_name_plural = _('repository updates')
        ordering = ['-created_at']
    
    repository = models.ForeignKey(
        Repository,
        models.CASCADE,
        related_name='updates')
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


class RepositoryExample(models.Model):
    class Meta:
        verbose_name = _('repository example')
        verbose_name_plural = _('repository examples')
    
    repository_update = models.ForeignKey(
        RepositoryUpdate,
        models.CASCADE,
        related_name='added',
        blank=True,
        null=True,
        editable=False)
    deleted_in = models.ForeignKey(
        RepositoryUpdate,
        models.CASCADE,
        related_name='deleted',
        blank=True,
        null=True,
        editable=False)
    text = models.TextField(
        _('text'),
        editable=False)
    intent = models.CharField(
        _('intent'),
        max_length=64,
        blank=True,
        editable=False)


class RepositoryExampleEntity(models.Model):
    class Meta:
        verbose_name = _('repository example entity')
        verbose_name_plural = _('repository example entities')
    
    repository_example = models.ForeignKey(
        RepositoryExample,
        models.CASCADE,
        related_name='entities',
        editable=False)
    start = models.PositiveIntegerField(
        _('start'),
        editable=False)
    end = models.PositiveIntegerField(
        _('end'),
        editable=False)
    entity = models.CharField(
        _('entity'),
        max_length=64,
        editable=False)

    @property
    def value(self):
        return self.repository_example.text[self.start:self.end]
