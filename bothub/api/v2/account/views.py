
import requests

from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import User, RepositoryOwner
from bothub.common.models import Repository, RepositoryVersion
from .serializers import ChangePasswordSerializer
from .serializers import LoginSerializer
from .serializers import RegisterUserSerializer
from .serializers import RequestResetPasswordSerializer
from .serializers import ResetPasswordSerializer
from .serializers import UserSerializer


@method_decorator(
    name="create", decorator=swagger_auto_schema(responses={201: '{"token":"TOKEN"}'})
)
class LoginViewSet(mixins.CreateModelMixin, GenericViewSet):

    """
    Login Users
    """

    queryset = User.objects
    serializer_class = LoginSerializer
    lookup_field = ("username", "password")
    metadata_class = Metadata

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
        except:
            response = requests.get(
                url=settings.OIDC_OP_USER_ENDPOINT,
                body={
                    "grant_type": "password",
                    "username": request.data.email,
                    "password": request.data.password,
                    "client_id": settings.OIDC_RP_CLIENT_ID,
                }
            )
            if response.status_code == 200:
                user = User.objects.create(request.data.email, nickname=request.data.email)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, message="user not found")

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key},
            status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RegisterUserViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Register new user
    """

    queryset = User.objects
    serializer_class = RegisterUserSerializer
    lookup_field = ("email", "name", "nickname", "password")
    metadata_class = Metadata


class ChangePasswordViewSet(mixins.UpdateModelMixin, GenericViewSet):
    """
    Change current user password.
    """

    serializer_class = ChangePasswordSerializer
    queryset = User.objects
    lookup_field = None
    permission_classes = [permissions.IsAuthenticated]
    metadata_class = Metadata

    def get_object(self, *args, **kwargs):
        request = self.request
        user = request.user

        # May raise a permission denied
        self.check_object_permissions(self.request, user)

        return user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("password"))
            self.object.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Request reset password
    """

    serializer_class = RequestResetPasswordSerializer
    queryset = User.objects
    lookup_field = ["email"]
    permission_classes = [permissions.AllowAny]
    metadata_class = Metadata

    def get_object(self):
        return self.queryset.get(email=self.request.data.get("email"))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object = self.get_object()
            self.object.send_reset_password_email()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyUserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Manager current user profile.
    retrieve:
    Get current user profile
    update:
    Update current user profile.
    partial_update:
    Update, partially, current user profile.
    """

    serializer_class = UserSerializer
    queryset = User.objects
    lookup_field = None
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, *args, **kwargs):
        request = self.request
        user = request.user

        # May raise a permission denied
        self.check_object_permissions(self.request, user)

        return user

    def destroy(self, request, *args, **kwargs):
        repositories = Repository.objects.filter(owner=self.request.user)
        repository_version = RepositoryVersion.objects.filter(
            created_by=self.request.user
        )
        user = User.generate_repository_user_bot()

        if repositories.count() > 0:
            repositories.update(owner_id=user)
        if repository_version.count() > 0:
            repository_version.update(created_by=user)
        return super().destroy(request, *args, **kwargs)


class UserProfileViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """
    Get user profile
    """

    serializer_class = UserSerializer
    queryset = User.objects
    lookup_field = "nickname"


class SearchUserViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = RepositoryOwner.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["=name", "^name", "$name", "=nickname", "^nickname", "$nickname"]
    pagination_class = None
    limit = 5

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())[: self.limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ResetPasswordViewSet(mixins.UpdateModelMixin, GenericViewSet):
    """
    Reset password
    """

    serializer_class = ResetPasswordSerializer
    queryset = User.objects
    lookup_field = "nickname"

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get("password"))
            self.object.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
