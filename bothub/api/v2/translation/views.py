import openpyxl
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl.drawing.image import Image
from django.db.models import Count, Q
from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework.exceptions import APIException
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions

from bothub import utils, settings
from bothub.api.v2.metadata import Metadata
from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.api.v2.repository.permissions import RepositoryInfoPermission
from bothub.common.models import (
    RepositoryTranslatedExample,
    RepositoryVersion,
    RepositoryTranslatedExampleEntity,
)

from bothub.api.v2.translation.permissions import (
    RepositoryTranslatedExamplePermission,
    RepositoryTranslatedExampleExporterPermission,
)
from bothub.api.v2.translation.serializers import (
    RepositoryTranslatedExampleSerializer,
    RepositoryTranslatedExporterSerializer,
)
from bothub.api.v2.translation.filters import TranslationsFilter
from bothub.common.models import RepositoryExample, RepositoryExampleEntity


class RepositoryTranslatedExampleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Manager example translation.

    list:
    Get example translation data.

    retrieve:
    Get example translation data.

    update:
    Update example translation.

    partial_update:
    Update, partially, example translation.

    delete:
    Delete example translation.
    """

    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        RepositoryTranslatedExamplePermission,
    ]

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = RepositoryTranslatedExample.objects.all()
        self.filter_class = TranslationsFilter
        return super().list(request, *args, **kwargs)


@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "with_translation",
                openapi.IN_QUERY,
                description="Boolean that allows you to download or not all translations",
                type=openapi.TYPE_BOOLEAN,
                default=True,
            ),
            openapi.Parameter(
                "of_the_language",
                openapi.IN_QUERY,
                description="Choose the language to be translated",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "for_the_language",
                openapi.IN_QUERY,
                description="Which language will be translated",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    ),
)
class RepositoryTranslatedExporterViewSet(
    MultipleFieldLookupMixin, mixins.RetrieveModelMixin, GenericViewSet
):

    queryset = RepositoryVersion.objects
    lookup_field = "repository__uuid"
    lookup_fields = ["repository__uuid", "pk"]
    serializer_class = RepositoryTranslatedExporterSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        RepositoryTranslatedExampleExporterPermission,
    ]
    metadata_class = Metadata

    def retrieve(self, request, *args, **kwargs):
        repository_version = self.get_object()
        with_translation = request.query_params.get("with_translation", True)
        of_the_language = request.query_params.get("of_the_language", None)
        for_the_language = request.query_params.get("for_the_language", True)
        if not of_the_language or not for_the_language:
            raise APIException(  # pragma: no cover
                {
                    "detail": "Requires the parameter of_the_language and for_the_language"
                },
                code=400,
            )
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=repository_version
        )

        examples = (
            repository_version.repository.examples(
                queryset=queryset, version_default=repository_version.is_default
            )
            .filter(repository_version_language__language=of_the_language)
            .annotate(
                translation_count=Count(
                    "translations", filter=Q(translations__language=for_the_language)
                )
            )
        )
        if not with_translation:
            examples.filter(translation_count=0)

        workbook = openpyxl.load_workbook(
            f"{settings.STATIC_ROOT}/bothub/exporter/example.xlsx"
        )
        worksheet = workbook.get_sheet_by_name("Translate")

        img = Image(f"{settings.STATIC_ROOT}/bothub/exporter/bothub.png")
        img.width = 210.21
        img.height = 60.69

        worksheet.add_image(img, "B1")

        entities_list = []

        for count, example in enumerate(examples, start=14):
            worksheet.insert_rows(count)
            worksheet.cell(row=count, column=2, value=str(example.pk))
            worksheet.cell(
                row=count,
                column=3,
                value=str(example.repository_version_language.repository_version.pk),
            )
            worksheet.cell(
                row=count,
                column=4,
                value=str(example.repository_version_language.language),
            )

            text = example.text
            entities = RepositoryExampleEntity.objects.filter(
                repository_example=example
            )
            count_entity = 0
            for entity in entities:
                if entity.entity.value not in entities_list:
                    entities_list.append(entity.entity.value)
                    text = utils.format_entity(
                        text=text,
                        entity=entity.entity.value,
                        start=entity.start + count_entity,
                        end=entity.end + count_entity,
                    )
                    count_entity += len(entity.entity.value) + 4
            worksheet.cell(row=count, column=5, value=str(text))

            translated = RepositoryTranslatedExample.objects.filter(
                original_example=example.pk
            )
            if translated:
                translated = translated.first()
                text_translated = translated.text
                entities_translate = RepositoryTranslatedExampleEntity.objects.filter(
                    repository_translated_example=translated
                )
                count_entity = 0
                for entity in entities_translate:
                    text = utils.format_entity(
                        text=text_translated,
                        entity=entity.entity.value,
                        start=entity.start + count_entity,
                        end=entity.end + count_entity,
                    )
                    count_entity += len(entity.entity.value) + 4
                worksheet.cell(row=count, column=6, value=str(text))

        for count, entity in enumerate(entities_list, start=4):
            worksheet.insert_rows(count)
            worksheet.cell(row=count, column=2, value=str(entity))

        response = HttpResponse(
            content=save_virtual_workbook(workbook),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=bothub.xlsx"
        return response
