import uuid
from timezone_field import TimeZoneField

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bothub.common.models import Organization


User = get_user_model()

class Project(models.Model):
    
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="projects",
        blank=True,
        null=True,
    )
    date_fomat = models.CharField(
        verbose_name=_("Date Format"),
        max_length=1
    )
    is_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    name = models.TextField(_("name"))
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
