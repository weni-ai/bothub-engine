from django.utils.decorators import method_decorator
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status, mixins
from drf_yasg.utils import swagger_auto_schema
from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import User

from .serializers import LoginSerializer
from .serializers import RegisterUserSerializer


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
