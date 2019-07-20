from django.utils.decorators import method_decorator
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status, mixins
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import User

from .serializers import LoginSerializer
from .serializers import RegisterUserSerializer
from .serializers import ChangePasswordSerializer
from .serializers import RequestResetPasswordSerializer
from .serializers import UserSerializer


@method_decorator(
    name='create',
    decorator=swagger_auto_schema(
        responses={201: '{"token":"TOKEN"}'}
    )
)
class LoginViewSet(mixins.CreateModelMixin, GenericViewSet):

    """
    Login Users
    """

    queryset = User.objects
    serializer_class = LoginSerializer
    lookup_field = ('username', 'password')
    metadata_class = Metadata

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
            },
            status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RegisterUserViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Register new user
    """
    queryset = User.objects
    serializer_class = RegisterUserSerializer
    lookup_field = ('email', 'name', 'nickname', 'password')
    metadata_class = Metadata


class ChangePasswordViewSet(mixins.UpdateModelMixin, GenericViewSet):
    """
    Change current user password.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects
    lookup_field = None
    permission_classes = [
        permissions.IsAuthenticated,
        # ChangePasswordPermission
    ]
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
            self.object.set_password(serializer.data.get('password'))
            self.object.save()
            return Response({}, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Request reset password
    """
    serializer_class = RequestResetPasswordSerializer
    queryset = User.objects
    lookup_field = ['email']
    permission_classes = [permissions.AllowAny]
    metadata_class = Metadata

    def get_object(self):
        return self.queryset.get(email=self.request.data.get('email'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object = self.get_object()
            self.object.send_reset_password_email()
            return Response({})
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    """
    Get user profile
    """
    serializer_class = UserSerializer
    queryset = User.objects
    lookup_field = 'nickname'
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
