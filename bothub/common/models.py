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


class RepositoryUpdate(models.Model):
    class Meta:
        verbose_name = _('repository update')
        verbose_name_plural = _('repository updates')
        ordering = ['-created_at']
    
    repository = models.ForeignKey(
        Repository,
        models.CASCADE,
        related_name='updates')
    bot_data = models.TextField(
        _('bot data'),
        blank=True,
        editable=False)
    by = models.ForeignKey(
        User,
        models.CASCADE)
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True)

class RepositoryUpdateIntent(models.Model):
    # TODO
    pass
