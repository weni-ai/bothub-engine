import json
from datetime import datetime

from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import parsers
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.authentication.models import RepositoryOwner
from bothub.common.models import (
    Repository,
    RepositoryNLPLog,
    RepositoryEntity,
    RepositoryQueueTask,
    RepositoryIntent,
    OrganizationAuthorization,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryVersion
from bothub.common.models import RepositoryVote
from bothub.common.models import RequestRepositoryAuthorization
from .filters import (
    RepositoriesFilter,
    RepositoryNLPLogFilter,
    RepositoryEntitiesFilter,
    RepositoryQueueTaskFilter,
    RepositoryNLPLogReportsFilter,
)
from .filters import RepositoryAuthorizationFilter
from .filters import RepositoryAuthorizationRequestsFilter
from .permissions import (
    RepositoryAdminManagerAuthorization,
    RepositoryEntityHasPermission,
    RepositoryInfoPermission,
)
from .permissions import RepositoryExamplePermission
from .permissions import RepositoryPermission
from .serializers import (
    AnalyzeTextSerializer,
    TrainSerializer,
    RepositoryNLPLogSerializer,
    DebugParseSerializer,
    WordDistributionSerializer,
    RepositoryEntitySerializer,
    NewRepositorySerializer,
    RasaUploadSerializer,
    RasaSerializer,
    RepositoryQueueTaskSerializer,
    RepositoryPermissionSerializer,
    RepositoryNLPLogReportsSerializer,
)
from .serializers import EvaluateSerializer
from .serializers import RepositoryAuthorizationRoleSerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RepositoryCategorySerializer
from .serializers import RepositoryContributionsSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositorySerializer
from .serializers import RepositoryUpload
from .serializers import RepositoryVotesSerializer
from .serializers import RequestRepositoryAuthorizationSerializer
from .serializers import ShortRepositorySerializer
from ..metadata import Metadata


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
        Evaluate repository using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        serializer = EvaluateSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        if not repository.evaluations(language=request.data.get("language")).count():
            raise APIException(
                detail=_("You need to have at least " + "one registered test phrase")
            )  # pragma: no cover

        if len(repository.intents()) <= 1:
            raise APIException(
                detail=_("You need to have at least " + "two registered intents")
            )  # pragma: no cover

        request = repository.request_nlp_evaluate(  # pragma: no cover
            user_authorization, serializer.data
        )
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": request.status_code}, code=request.status_code
            )
        return Response(request.json())  # pragma: no cover


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


class RepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all public repositories.
    """

    serializer_class = ShortRepositorySerializer
    queryset = Repository.objects.all().publics().order_by_relevance()
    filter_class = RepositoriesFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["$name", "^name", "=name"]


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

    def get_queryset(self, *args, **kwargs):
        try:
            if self.request.query_params.get("nickname", None):
                owner = get_object_or_404(
                    RepositoryOwner,
                    nickname=self.request.query_params.get("nickname", None),
                )
                if owner.is_organization:
                    auth_org = OrganizationAuthorization.objects.filter(
                        organization=owner, user=self.request.user
                    ).first()
                    if auth_org.can_read:
                        return self.queryset.filter(
                            owner__nickname=self.request.query_params.get(
                                "nickname", self.request.user
                            )
                        )
                return self.queryset.filter(
                    owner__nickname=self.request.query_params.get(
                        "nickname", self.request.user
                    ),
                    is_private=False,
                )
            else:
                return self.queryset.filter(owner=self.request.user)
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


class RepositoryNLPLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = RepositoryNLPLog.objects
    serializer_class = RepositoryNLPLogSerializer
    permission_classes = [permissions.IsAuthenticated, RepositoryPermission]
    filter_class = RepositoryNLPLogFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["$text", "^text", "=text"]


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
                intent=example["intent"],
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
    permission_classes = [IsAuthenticated]

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
        x = self.queryset.count_logs(
            start_date=datetime.strptime(
                self.request.query_params.get("start_date", None), "%Y-%m-%d"
            ).replace(hour=0, minute=0),
            end_date=datetime.strptime(
                self.request.query_params.get("end_date", None), "%Y-%m-%d"
            ).replace(hour=23, minute=59),
            authorizations__user=self.request.user,
        ).order_by("-total_count")
        return x
