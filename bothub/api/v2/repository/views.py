import json

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django_elasticsearch_dsl_drf.constants import LOOKUP_QUERY_GTE, LOOKUP_QUERY_LTE
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import mixins, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    APIException,
    PermissionDenied,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.authentication.authorization import TranslatorAuthentication
from bothub.authentication.models import RepositoryOwner
from bothub.celery import app as celery_app
from bothub.common import languages
from bothub.common.documents.repositorynlplog import RepositoryNLPLogDocument
from bothub.common.documents.repositoryqanlplog import RepositoryQANLPLogDocument
from bothub.common.models import (
    OrganizationAuthorization,
    Repository,
    RepositoryAuthorization,
    RepositoryCategory,
    RepositoryEntity,
    RepositoryExample,
    RepositoryIntent,
    RepositoryMigrate,
    RepositoryQueueTask,
    RepositoryTranslator,
    RepositoryVersion,
    RepositoryVote,
    RequestRepositoryAuthorization,
    RepositoryVersionLanguage,
    Organization,
)

from ..metadata import Metadata
from .filters import (
    RepositoriesFilter,
    RepositoryAuthorizationFilter,
    RepositoryAuthorizationRequestsFilter,
    RepositoryEntitiesFilter,
    RepositoryIntentFilter,
    RepositoryNLPLogFilter,
    RepositoryNLPLogReportsFilter,
    RepositoryQueueTaskFilter,
)
from .permissions import (
    RepositoryAdminManagerAuthorization,
    RepositoryEntityHasPermission,
    RepositoryExamplePermission,
    RepositoryInfoPermission,
    RepositoryIntentPermission,
    RepositoryLogPermission,
    RepositoryMigratePermission,
    RepositoryPermission,
    RepositoryQALogPermission,
    RepositoryTrainInfoPermission,
)
from .serializers import (
    AnalyzeQuestionSerializer,
    AnalyzeTextSerializer,
    DebugParseSerializer,
    EvaluateSerializer,
    NewRepositorySerializer,
    RasaSerializer,
    RasaUploadSerializer,
    RepositoryAuthorizationRoleSerializer,
    RepositoryAuthorizationSerializer,
    RepositoryAutoTranslationSerializer,
    RepositoryCategorySerializer,
    RepositoryContributionsSerializer,
    RepositoryEntitySerializer,
    RepositoryExampleSerializer,
    RepositoryIntentSerializer,
    RepositoryMigrateSerializer,
    RepositoryNLPLogReportsSerializer,
    RepositoryNLPLogSerializer,
    RepositoryPermissionSerializer,
    RepositoryQANLPLogSerializer,
    RepositoryQueueTaskSerializer,
    RepositorySerializer,
    RepositoryTrainInfoSerializer,
    RepositoryTranslatorInfoSerializer,
    RepositoryUpload,
    RepositoryVotesSerializer,
    RequestRepositoryAuthorizationSerializer,
    RepositoryExampleSuggestionSerializer,
    ShortRepositorySerializer,
    TrainSerializer,
    WordDistributionSerializer,
    RemoveRepositoryProject,
    AddRepositoryProjectSerializer,
)


class NewRepositoryViewSet(
    MultipleFieldLookupMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    """
    Manager repository (bot).
    """

    queryset = RepositoryVersion.objects
    lookup_field = "repository__uuid"
    lookup_fields = ["repository__uuid", "pk"]
    serializer_class = NewRepositorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, RepositoryInfoPermission]
    metadata_class = Metadata

    @action(
        detail=True,
        methods=["GET"],
        url_name="repository-languages-status",
        lookup_fields=["repository__uuid", "pk"],
    )
    def languagesstatus(self, request, **kwargs):
        """
        Get current language status.
        """
        if self.lookup_field not in kwargs:
            return Response(status=405)

        repository_version = self.get_object()
        return Response({"languages_status": repository_version.languages_status})

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-auto-translation",
        permission_classes=[],
        lookup_fields=["repository__uuid", "pk"],
        serializer_class=RepositoryAutoTranslationSerializer,
    )
    def auto_translation(self, request, **kwargs):
        repository_version = self.get_object()
        user_authorization = repository_version.repository.get_user_authorization(
            request.user
        )

        if not user_authorization.can_translate:
            raise PermissionDenied()

        serializer = RepositoryAutoTranslationSerializer(
            data=request.data
        )  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        target_language = serializer.data.get("target_language")

        # Validates if the language is available
        languages.validate_language(value=target_language)

        if target_language not in languages.GOOGLE_API_TRANSLATION_LANGUAGES_SUPPORTED:
            raise APIException(  # pragma: no cover
                detail=_("This language is not available in machine translation")
            )

        if repository_version.repository.language == target_language:
            raise APIException(  # pragma: no cover
                detail=_(
                    "It is not possible to translate the base language into your own language"
                )
            )

        queue_running = (
            repository_version.get_version_language(language=target_language)
            .queues.filter(
                Q(status=RepositoryQueueTask.STATUS_PENDING)
                | Q(status=RepositoryQueueTask.STATUS_PROCESSING)
            )
            .filter(
                Q(type_processing=RepositoryQueueTask.TYPE_PROCESSING_AUTO_TRANSLATE)
            )
        )

        if queue_running:
            raise APIException(  # pragma: no cover
                detail=_(
                    "It is only possible to perform an automatic translation per language, a translation is already running"
                )
            )

        task = celery_app.send_task(
            "auto_translation",
            args=[
                repository_version.pk,
                repository_version.repository.language,
                target_language,
            ],
        )

        return Response({"id_queue": task.task_id})

    @action(
        detail=True,
        methods=["GET"],
        url_name="project-repository",
        lookup_fields=["repository__uuid", "pk"],
        permission_classes=[IsAuthenticated],
    )
    def projectrepository(self, request, **kwargs):
        repository = self.get_object().repository

        project_uuid = request.query_params.get("project_uuid")
        organization_pk = request.query_params.get("organization")

        try:
            organization = (
                Organization.objects.get(pk=organization_pk)
                if organization_pk
                else None
            )
        except Organization.DoesNotExist:
            raise ValidationError(_("Organization not found"))

        if not project_uuid:
            raise ValidationError(_("Need to pass 'project_uuid' in query params"))

        authorization = organization.get_organization_authorization(request.user)

        if not authorization.can_contribute:
            raise PermissionDenied()

        task = celery_app.send_task(
            name="get_project_organization", args=[project_uuid]
        )
        task.wait()

        repositories = repository.authorizations.filter(uuid__in=task.result)

        data = dict(in_project=repositories.exists())

        if organization:

            organization_authorization = (
                organization.organization_authorizations.filter(uuid__in=task.result)
            )
            data["in_project"] = (
                data["in_project"] or organization_authorization.exists()
            )

        return Response(data)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[RepositoryAdminManagerAuthorization],
        url_name="remove-repository-project",
        serializer_class=RemoveRepositoryProject,
    )
    def remove_repository_project(self, request, **kwargs):

        repository_version = self.get_object()
        repository = repository_version.repository

        project_uuid = request.data.get("project_uuid")
        organization_pk = request.data.get("organization")

        if not project_uuid:
            raise ValidationError(_("Need to pass 'project_uuid' in query params"))

        try:
            organization = (
                Organization.objects.get(pk=organization_pk)
                if organization_pk
                else None
            )
        except Organization.DoesNotExist:
            raise ValidationError(_("Organization not found"))

        user_authorization = organization.get_organization_authorization(request.user)

        if not user_authorization.is_admin:
            raise PermissionDenied()

        project_organization = celery_app.send_task(
            name="get_project_organization", args=[project_uuid]
        )
        project_organization.wait()

        authorizations = list(
            repository.authorizations.filter(
                uuid__in=project_organization.result
            ).values_list("uuid", flat=True)
        )

        if organization:
            organization_authorization = organization.get_organization_authorization(
                request.user
            )
            if not organization_authorization.is_admin:
                raise PermissionDenied()

            authorizations += list(
                organization.organization_authorizations.filter(
                    uuid__in=project_organization.result
                ).values_list("uuid", flat=True)
            )

        if not len(authorizations):
            raise ValidationError(
                _("Repository or organization is not be included on project")
            )

        authorizations_uuids = map(
            lambda authorization: str(authorization), authorizations
        )

        task = celery_app.send_task(
            name="remove_authorizations_project",
            args=[project_uuid, list(authorizations_uuids)],
        )
        task.wait()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        url_name="add-repository-project",
        serializer_class=AddRepositoryProjectSerializer,
        permission_classes=[IsAuthenticated],
    )
    def add_repository_project(self, request, **kwargs):

        repository = self.get_object().repository
        organization_pk = request.data.get("organization")

        try:
            organization = Organization.objects.get(pk=organization_pk)
        except Organization.DoesNotExist:
            raise ValidationError(_("Organization not found"))

        organization_authorization = organization.get_organization_authorization(
            request.user
        )

        if not organization_authorization.can_contribute:
            raise PermissionDenied()

        serializer_data = dict(
            user=request.user.email,
            access_token=str(
                repository.get_user_authorization(
                    organization_authorization.organization
                ).uuid
            ),
            **request.data,
        )

        serializer = AddRepositoryProjectSerializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)

        project_uuid = serializer.validated_data.get("project_uuid")

        task = celery_app.send_task(
            name="get_project_organization", args=[project_uuid]
        )
        task.wait()

        organization_authorization = organization.organization_authorizations.filter(
            uuid__in=task.result
        )

        if organization_authorization.exists():
            raise ValidationError(_("Repository already added"))

        data = serializer.save()

        return Response(data)


class RepositoryTrainInfoViewSet(
    MultipleFieldLookupMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    """
    Manager repository (bot).
    """

    queryset = RepositoryVersionLanguage.objects
    lookup_field = "repository__uuid"
    lookup_fields = [
        "repository_version__repository__uuid",
        "repository_version__pk",
        "language",
    ]
    serializer_class = RepositoryTrainInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, RepositoryTrainInfoPermission]
    metadata_class = Metadata


class RepositoryTranslatorInfoViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryTranslator.objects
    lookup_field = "uuid"
    serializer_class = RepositoryTranslatorInfoSerializer
    authentication_classes = [TranslatorAuthentication]
    metadata_class = Metadata


class RepositoryViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Manager repository (bot).
    """

    queryset = Repository.objects
    lookup_field = "uuid"
    lookup_fields = ["uuid"]
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, RepositoryPermission]
    metadata_class = Metadata

    @method_decorator(name="list", decorator=swagger_auto_schema(deprecated=True))
    @action(
        detail=True,
        methods=["GET"],
        url_name="repository-languages-status",
        lookup_fields=["uuid"],
    )
    def languagesstatus(self, request, **kwargs):
        """
        Get current language status.
        """
        if self.lookup_field not in kwargs:
            return Response(status=405)

        repository = self.get_object()
        return Response({"languages_status": repository.languages_status})

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-train",
        lookup_fields=["uuid"],
        serializer_class=TrainSerializer,
    )
    def train(self, request, **kwargs):
        """
        Train current update using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = TrainSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        if not user_authorization.can_write:
            raise PermissionDenied()
        request = repository.request_nlp_train(
            user_authorization, serializer.data
        )  # pragma: no cover
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": request.status_code}, code=request.status_code
            )
        return Response(request.json())  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-analyze",
        permission_classes=[],
        lookup_fields=["uuid"],
        serializer_class=AnalyzeTextSerializer,
    )
    def analyze(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = AnalyzeTextSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = repository.request_nlp_analyze(
            user_authorization, serializer.data
        )  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_(
                    "Something unexpected happened! " + "We couldn't analyze your text."
                )
            )
        error = response.get("error")  # pragma: no cover
        message = error.get("message")  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-question-answering",
        permission_classes=[],
        lookup_fields=["uuid"],
        serializer_class=AnalyzeQuestionSerializer,
    )
    def question(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = AnalyzeQuestionSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = repository.request_nlp_qa(
            user_authorization, serializer.data
        )  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_(
                    "Something unexpected happened! " + "We couldn't analyze your text."
                )
            )
        error = response.get("error")  # pragma: no cover
        message = error.get("message")  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-debug-parse",
        permission_classes=[],
        lookup_fields=["uuid"],
        serializer_class=DebugParseSerializer,
    )
    def debug_parse(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = DebugParseSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = repository.request_nlp_debug_parse(
            user_authorization, serializer.data
        )  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_(
                    "Something unexpected happened! " + "We couldn't debug your text."
                )
            )
        error = response.get("error")  # pragma: no cover
        message = error.get("message")  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-words-distribution",
        permission_classes=[],
        lookup_fields=["uuid"],
        serializer_class=WordDistributionSerializer,
    )
    def words_distribution(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = WordDistributionSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = repository.request_nlp_words_distribution(
            user_authorization, serializer.data
        )  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_(
                    "Something unexpected happened! " + "We couldn't debug your text."
                )
            )
        error = response.get("error")  # pragma: no cover
        message = error.get("message")  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-evaluate",
        lookup_fields=["uuid"],
        serializer_class=EvaluateSerializer,
    )
    def evaluate(self, request, **kwargs):
        """
        Manual evaluate repository using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        serializer = EvaluateSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        try:
            request = repository.request_nlp_manual_evaluate(  # pragma: no cover
                user_authorization, serializer.data
            )
        except DjangoValidationError as e:
            raise APIException(e.message, code=400)

        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(
                {"status_code": request.status_code}, code=request.status_code
            )  # pragma: no cover
        return Response(request.json())  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-automatic-evaluate",
        lookup_fields=["uuid"],
        serializer_class=EvaluateSerializer,
    )
    def automatic_evaluate(self, request, **kwargs):
        """
        Automatic evaluate repository using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        serializer = EvaluateSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        try:
            request = repository.request_nlp_automatic_evaluate(  # pragma: no cover
                user_authorization, serializer.data
            )
        except DjangoValidationError as e:
            raise APIException(e.message, code=400)

        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(
                {"status_code": request.status_code}, code=request.status_code
            )  # pragma: no cover
        return Response(request.json())  # pragma: no cover

    @action(
        detail=True,
        methods=["GET"],
        url_name="check-can-repository-automatic-evaluate",
        lookup_fields=["uuid"],
    )
    def check_can_automatic_evaluate(self, request, **kwargs):
        """
        Check if repository can run automatic evaluate.
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()

        language = request.query_params.get("language")
        if not language:
            raise ValidationError(_("Need to pass 'language' in query params"))

        try:
            repository.validate_if_can_run_automatic_evaluate(language=language)
            response = {"can_run_evaluate_automatic": True, "messages": []}
        except DjangoValidationError as e:
            response = {"can_run_evaluate_automatic": False, "messages": e}
        return Response(response)  # pragma: no cover


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user",
                openapi.IN_QUERY,
                description="Nickname User to find repositories votes",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "repository",
                openapi.IN_QUERY,
                description="Repository UUID, returns a list of "
                "users who voted for this repository",
                type=openapi.TYPE_STRING,
            ),
        ]
    ),
)
class RepositoryVotesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Manager repository votes (bot).
    """

    queryset = RepositoryVote.objects.all()
    lookup_field = "repository"
    lookup_fields = ["repository"]
    serializer_class = RepositoryVotesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    metadata_class = Metadata

    def get_queryset(self, *args, **kwargs):
        if self.request.query_params.get("repository", None):
            return self.queryset.filter(
                repository=self.request.query_params.get("repository", None)
            )
        elif self.request.query_params.get("user", None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get("user", None)
            )
        else:
            return self.queryset.all()

    def destroy(self, request, *args, **kwargs):
        self.queryset.filter(
            repository=self.request.query_params.get("repository", None),
            user=self.request.user,
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoryMigrateViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Repository migrate all senteces wit.
    """

    queryset = RepositoryMigrate.objects
    serializer_class = RepositoryMigrateSerializer
    permission_classes = [IsAuthenticated, RepositoryMigratePermission]
    metadata_class = Metadata


class RepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all public repositories.
    """

    serializer_class = ShortRepositorySerializer
    queryset = Repository.objects.all().publics().order_by_relevance()
    filter_class = RepositoriesFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["$name", "^name", "=name"]

    @action(detail=True, methods=["GET"], url_name="list-project-organizatiton")
    def list_project_organizatiton(self, request, **kwargs):
        project_uuid = request.query_params.get("project_uuid")

        if not project_uuid:
            raise ValidationError(_("Need to pass 'project_uuid' in query params"))

        task = celery_app.send_task(
            name="get_project_organization", args=[project_uuid]
        )
        task.wait()

        repositories = Repository.objects.filter(authorizations__uuid__in=task.result)

        serialized_data = ShortRepositorySerializer(repositories, many=True)
        return Response(serialized_data.data)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="Nickname User",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
class RepositoriesContributionsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List Repositories Contributions by user.
    """

    serializer_class = RepositoryContributionsSerializer
    queryset = RepositoryAuthorization.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "nickname"

    def get_queryset(self):
        if self.request.query_params.get("nickname", None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get("nickname", None)
            )
        else:
            return self.queryset.none()


class RepositoryCategoriesView(mixins.ListModelMixin, GenericViewSet):
    """
    List all categories.
    """

    serializer_class = RepositoryCategorySerializer
    queryset = RepositoryCategory.objects.all()
    pagination_class = None


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="Nickname User to find repositories",
                type=openapi.TYPE_STRING,
            )
        ]
    ),
)
class SearchRepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all user's repositories
    """

    queryset = Repository.objects
    serializer_class = RepositorySerializer
    lookup_field = "nickname"
    filter_class = RepositoriesFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["$name", "^name", "=name"]

    def get_queryset(self, *args, **kwargs):
        try:
            if not self.request.query_params.get(
                "nickname", None
            ) and not self.request.query_params.get("owner_id", None):
                return self.queryset.filter(owner=self.request.user).distinct()
            return super().get_queryset()
        except TypeError:
            return self.queryset.none()


class RepositoriesPermissionsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all user's repositories permissions
    """

    queryset = RepositoryAuthorization.objects
    serializer_class = RepositoryPermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return RepositoryAuthorization.objects.none()
        return (
            self.queryset.exclude(repository__owner=self.request.user)
            .exclude(role=RepositoryAuthorization.ROLE_NOT_SETTED)
            .filter(user=self.request.user)
        )


class RepositoryAuthorizationViewSet(
    MultipleFieldLookupMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = RepositoryAuthorization.objects.exclude(
        role=RepositoryAuthorization.ROLE_NOT_SETTED
    )
    serializer_class = RepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationFilter
    lookup_fields = ["repository__uuid", "user__nickname"]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        repository_uuid = self.kwargs.get("repository__uuid")
        user_nickname = self.kwargs.get("user__nickname")

        repository = get_object_or_404(Repository, uuid=repository_uuid)
        user = get_object_or_404(RepositoryOwner, nickname=user_nickname)
        obj = repository.get_user_authorization(user)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, *args, **kwargs):
        self.lookup_field = "user__nickname"

        self.filter_class = None
        self.serializer_class = RepositoryAuthorizationRoleSerializer
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]
        response = super().update(*args, **kwargs)
        instance = self.get_object()
        if instance.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            if (
                RequestRepositoryAuthorization.objects.filter(
                    user=instance.user, repository=instance.repository
                ).count()
                == 0
            ):
                RequestRepositoryAuthorization.objects.create(
                    user=instance.user,
                    repository=instance.repository,
                    approved_by=self.request.user,
                )
            if not instance.user.is_organization:
                instance.send_new_role_email(self.request.user)
        return response

    def list(self, request, *args, **kwargs):
        self.lookup_fields = []
        return super().list(request, *args, **kwargs)


class RepositoryAuthorizationRequestsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    List of all authorization requests for a repository
    """

    queryset = RequestRepositoryAuthorization.objects.exclude(approved_by__isnull=False)
    serializer_class = RequestRepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationRequestsFilter
    permission_classes = [IsAuthenticated]
    metadata_class = Metadata

    def create(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]

        update_id = self.kwargs.get("pk")
        repository = self.request.data.get("repository")

        req_auth = RequestRepositoryAuthorization.objects.filter(pk=update_id)
        if req_auth:
            req_auth = req_auth.first()
            auth = RepositoryAuthorization.objects.filter(
                user=req_auth.user, repository=repository
            )
            if auth:
                req_auth.approved_by = self.request.user
                req_auth.save(update_fields=["approved_by"])
                return Response({"role": auth.first().role})

        try:
            return super().update(request, *args, **kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.message)

    def destroy(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]
        return super().destroy(request, *args, **kwargs)


class RepositoryExampleViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    Manager repository example.

    retrieve:
    Get repository example data.

    delete:
    Delete repository example.

    update:
    Update repository example.

    """

    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [RepositoryExamplePermission]

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().create(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-upload-examples",
        parser_classes=[parsers.MultiPartParser],
        serializer_class=RepositoryUpload,
    )
    def upload_examples(self, request, **kwargs):
        try:
            repository = get_object_or_404(
                Repository, pk=request.data.get("repository")
            )
        except DjangoValidationError:
            raise PermissionDenied()

        try:
            repository_version = get_object_or_404(
                RepositoryVersion, pk=request.data.get("repository_version")
            )
        except DjangoValidationError:
            raise PermissionDenied()

        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()

        f = request.FILES.get("file")
        try:
            json_data = json.loads(f.read().decode())
        except json.decoder.JSONDecodeError:
            raise UnsupportedMediaType("json")

        count_added = 0
        not_added = []

        for data in json_data:
            response_data = data
            response_data["repository"] = request.data.get("repository")
            response_data["repository_version"] = repository_version.pk

            intent, created = RepositoryIntent.objects.get_or_create(
                text=response_data.get("intent"), repository_version=repository_version
            )

            response_data.update({"intent": intent.pk})

            serializer = RepositoryExampleSerializer(
                data=response_data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                count_added += 1
            else:
                not_added.append(data)

        return Response({"added": count_added, "not_added": not_added})

    @action(
        detail=True,
        methods=["GET"],
        url_name="word-suggestions",
        serializer_class=RepositoryExampleSuggestionSerializer,
    )
    def word_suggestions(self, request, **kwargs):
        """
        Get four suggestions for words on a example on same language
        """
        self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        example = self.get_object()

        authorization = example.repository_version_language.repository_version.repository.get_user_authorization(
            request.user
        )
        if not authorization.can_read:
            raise PermissionDenied()

        task = celery_app.send_task(
            name="word_suggestions", args=[example.pk, str(authorization)]
        )
        task.wait()
        suggestions = task.result

        return Response({"suggestions": suggestions})


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "confidence__gte",
                openapi.IN_QUERY,
                description="Specify the entire percentage of the minimum confidentiality",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "confidence__lte",
                openapi.IN_QUERY,
                description="Specify the entire percentage of the maximum confidentiality",
                type=openapi.TYPE_INTEGER,
            ),
        ]
    ),
)
class RepositoryNLPLogViewSet(DocumentViewSet):
    document = RepositoryNLPLogDocument
    serializer_class = RepositoryNLPLogSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticated, RepositoryLogPermission]
    filter_backends = [CompoundSearchFilterBackend, FilteringFilterBackend]
    pagination_class = LimitOffsetPagination
    limit = settings.REPOSITORY_NLP_LOG_LIMIT
    search_fields = ["text"]
    filter_fields = {
        "repository_uuid": "repository_uuid",
        "language": "language",
        "repository_version": "repository_version",
        "repository_version_language": "repository_version_language",
        "intent": "log_intent.intent",
        "confidence": {
            "field": "log_intent.confidence",
            "lookups": [LOOKUP_QUERY_LTE, LOOKUP_QUERY_GTE],
        },
    }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset[: self.limit]

    def get_queryset(self):
        params = {
            "repository_uuid": self.request.query_params.get("repository_uuid", None),
            "repository_version": self.request.query_params.get(
                "repository_version", None
            ),
            "repository_version_language": self.request.query_params.get(
                "repository_version_language", None
            ),
        }
        RepositoryNLPLogFilter(params=params, user=self.request.user)
        return super().get_queryset().sort("-created_at")


class RepositoryQANLPLogViewSet(DocumentViewSet):
    document = RepositoryQANLPLogDocument
    serializer_class = RepositoryQANLPLogSerializer
    lookup_field = "pk"
    permission_classes = [permissions.IsAuthenticated, RepositoryQALogPermission]
    filter_backends = [CompoundSearchFilterBackend, FilteringFilterBackend]
    pagination_class = LimitOffsetPagination
    limit = settings.REPOSITORY_NLP_LOG_LIMIT
    search_fields = ["question"]
    filter_fields = {
        "text": "text",
        "language": "language",
        "knowledge_base": "knowledge_base",
        "repository_uuid": "repository_uuid",
    }

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset[: self.limit]

    def get_queryset(self):
        params = {
            "repository_uuid": self.request.query_params.get("repository_uuid", None),
            "context": self.request.query_params.get("context", None),
            "knowledge_base": self.request.query_params.get("knowledge_base", None),
        }
        RepositoryNLPLogFilter(params=params, user=self.request.user)
        return super().get_queryset().sort("-created_at")


class RepositoryEntitiesViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = RepositoryEntity.objects
    serializer_class = RepositoryEntitySerializer
    permission_classes = [IsAuthenticated, RepositoryEntityHasPermission]

    def list(self, request, *args, **kwargs):
        self.queryset = RepositoryEntity.objects.all()
        self.filter_class = RepositoryEntitiesFilter
        return super().list(request, *args, **kwargs)


class RasaUploadViewSet(
    MultipleFieldLookupMixin, mixins.UpdateModelMixin, GenericViewSet
):
    queryset = RepositoryVersion.objects
    lookup_field = "repository__uuid"
    lookup_fields = ["repository__uuid", "pk"]
    permission_classes = [IsAuthenticated, RepositoryInfoPermission]
    serializer_class = RasaUploadSerializer
    parser_classes = (MultiPartParser,)
    metadata_class = Metadata

    def update(self, request, *args, **kwargs):  # pragma: no cover
        serializer = RasaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer_rasa = RasaSerializer(data=json.load(request.data.get("file")))
        serializer_rasa.is_valid(raise_exception=True)

        for example in serializer_rasa.data.get("rasa_nlu_data", {}).get(
            "common_examples", []
        ):
            if RepositoryExample.objects.filter(
                repository_version_language__repository_version=kwargs.get("pk"),
                text=example["text"],
                intent__text=example["intent"],
                repository_version_language__language=serializer.data.get("language"),
            ).count():
                continue

            example["repository"] = kwargs.get("repository__uuid")
            example["repository_version"] = kwargs.get("pk")
            example["language"] = serializer.data.get("language")

            serializer_example = RepositoryExampleSerializer(
                data=example, context={"request": request}
            )
            if serializer_example.is_valid():
                serializer_example.save()

        return Response(202)


class RepositoryTaskQueueViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = RepositoryQueueTask.objects
    serializer_class = RepositoryQueueTaskSerializer
    filter_class = RepositoryQueueTaskFilter
    permission_classes = []

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RepositoryNLPLogReportsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all public repositories.
    """

    serializer_class = RepositoryNLPLogReportsSerializer
    queryset = Repository.objects.all()
    filter_class = RepositoryNLPLogReportsFilter
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return Repository.objects.none()
        user = self.request.user
        if self.request.query_params.get("organization_nickname", None):
            owner = get_object_or_404(
                RepositoryOwner,
                nickname=self.request.query_params.get("organization_nickname", None),
            )
            if owner.is_organization:
                auth_org = OrganizationAuthorization.objects.filter(
                    organization=owner, user=self.request.user
                ).first()
                if auth_org.can_read:
                    user = owner
        return (
            self.queryset.count_logs(
                start_date=self.request.query_params.get("start_date", None),
                end_date=self.request.query_params.get("end_date", None),
                user=user,
            )
            .exclude(total_count=0)
            .order_by("-total_count")
        )


class RepositoryIntentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = RepositoryIntent.objects
    filter_class = RepositoryIntentFilter
    serializer_class = RepositoryIntentSerializer
    permission_classes = [RepositoryIntentPermission]

    def retrieve(self, request, *args, **kwargs):
        self.filter_class = None
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.filter_class = None
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.filter_class = None
        return super().update(request, *args, **kwargs)

    @method_decorator(
        decorator=swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "language",
                    openapi.IN_QUERY,
                    description="Repository version language to suggest, "
                    "if none, Repository language will be used",
                    type=openapi.TYPE_STRING,
                )
            ]
        )
    )
    @action(
        detail=True,
        methods=["GET"],
        url_name="intent-suggestions",
        serializer_class=RepositoryIntentSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def intent_suggestions(self, request, **kwargs):
        """
        Get 10 suggestions for intent on your self language
        """
        self.filter_class = None
        intent = self.get_object()
        language = self.request.query_params.get("language")

        authorization = intent.repository_version.repository.get_user_authorization(
            request.user
        )

        if not authorization.can_read:
            raise PermissionDenied()

        task = celery_app.send_task(
            name="intent_suggestions", args=[intent.pk, language, str(authorization.pk)]
        )
        task.wait()
        suggestions = task.result

        return Response({"suggestions": suggestions})


class RepositoryExamplesBulkViewSet(mixins.CreateModelMixin, GenericViewSet):
    """Allows bulk creation of Examples inside an array."""

    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super().get_serializer(*args, **kwargs)
