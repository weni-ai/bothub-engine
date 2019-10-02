from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse

from bothub.common.models import Repository
from bothub.common.models import UserPermissionRepository
from bothub.common.models import UserGroupRepository
from bothub.common.models import PermissionsCode
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryUpdate
from bothub.common.models import RepositoryCategory


class RepositoryUpdateInline(admin.TabularInline):
    model = RepositoryUpdate
    extra = 0
    can_delete = False

    fields = [
        "language",
        "algorithm",
        "use_competing_intents",
        "use_name_entities",
        "created_at",
        "by",
        "training_started_at",
        "trained_at",
        "failed_at",
        "training_log",
        "download_bot_data",
    ]
    readonly_fields = fields

    def download_bot_data(self, obj):  # pragma: no cover
        if not obj.trained_at:
            return "-"
        return format_html(
            """
<a href="{}">Download Bot Data</a>
""".format(
                reverse("download_bot_data", kwargs={"update_id": obj.id})
            )
        )


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "uuid", "language", "is_private", "created_at"]
    search_fields = ["name", "uuid", "language", "owner__nickname", "slug"]
    list_filter = ["is_private", "language", "categories"]
    inlines = [RepositoryUpdateInline]


@admin.register(RepositoryCategory)
class RepositoryCategoryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "icon"]


@admin.register(UserPermissionRepository)
class UserPermissionRepositoryAdmin(admin.ModelAdmin):
    list_display = ["uuid", "codename", "usergrouprepository"]


@admin.register(UserGroupRepository)
class UserGroupRepositoryAdmin(admin.ModelAdmin):
    list_display = ["uuid", "repository", "name"]


@admin.register(PermissionsCode)
class PermissionsCodeAdmin(admin.ModelAdmin):
    list_display = ["uuid", "codename", "name"]


@admin.register(RepositoryAuthorization)
class RepositoryAuthorizationAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "repository", "usergrouprepository"]
