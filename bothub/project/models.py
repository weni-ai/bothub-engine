import uuid
from timezone_field import TimeZoneField

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bothub.common.models import Organization, Repository


User = get_user_model()


class TemplateType(models.Model):
    uuid = models.UUIDField(
        _("UUID"), null=True, blank=True
    )
    name = models.CharField(max_length=255)
    setup = models.JSONField(default=dict)


class Project(models.Model):

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="projects",
        blank=True,
        null=True,
    )
    date_format = models.CharField(
        verbose_name=_("Date Format"),
        max_length=1
    )
    is_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    name = models.TextField(_("name"))
    template_type = models.ForeignKey(TemplateType, models.SET_NULL, null=True, related_name="template_type")
    timezone = TimeZoneField(verbose_name=_("Timezone"))
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        null=True,
        related_name="projects",
    )
    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4
    )


class ProjectIntelligence(models.Model):
    uuid = models.UUIDField(
        _("UUID"), primary_key=True, default=uuid.uuid4
    )
    project = models.ForeignKey(Project, related_name="intelligences", on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, related_name="project_intelligences", on_delete=models.CASCADE, blank=True, null=True)
    access_token = models.CharField(verbose_name="Access token", max_length=255, null=True, blank=True)
    name = models.TextField(_("name"))
    integrated_at = models.DateTimeField(_("created at"), auto_now_add=True)
    integrated_by = models.ForeignKey(User, related_name="project_intelligences", on_delete=models.SET_NULL, blank=True, null=True)
