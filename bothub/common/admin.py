from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse

from bothub.common.models import Repository, Organization
from bothub.common.models import RepositoryVersion
from bothub.common.models import RepositoryCategory


class RepositoryVersionInline(admin.TabularInline):
    model = RepositoryVersion
    extra = 0
    can_delete = False

    fields = [
        "name",
        "last_update",
        "repository",
        "created_by",
        "created_at",
        "is_deleted",
        "download_bot_data",
    ]
    readonly_fields = fields

    def download_bot_data(self, obj):  # pragma: no cover
        trainers = []
        if obj:
            for version in obj.version_languages:
                if (
                    version.get_bot_data.bot_data != ""
                    and version.get_bot_data.bot_data is not None
                ):
                    trainers.append(
                        f"<a href='{reverse('download_bot_data', kwargs={'update_id': version.get_bot_data.pk})}'>{version.language.upper()}</a>"
                    )
        if not trainers:
            return "-"
        return format_html(f"Download Bot Data {' - '.join(trainers)}")


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "uuid",
        "language",
        "is_private",
        "allow_search_examples",
        "created_at",
    ]
    search_fields = ["name", "uuid", "language", "owner__nickname", "slug"]
    list_filter = ["is_private", "language", "categories", "allow_search_examples"]
    inlines = [RepositoryVersionInline]


@admin.register(RepositoryCategory)
class RepositoryCategoryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "icon"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "pk", "nickname", "created_at"]
    search_fields = ["name", "pk", "nickname"]
    list_filter = ["verificated"]
