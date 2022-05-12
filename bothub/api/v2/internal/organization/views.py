from django.utils.translation import ugettext_lazy as _
from django.db import models
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import User
from bothub.common.models import Organization, OrganizationAuthorization, Repository, RepositoryAuthorization
from bothub.api.v2.internal.organization.serializers import OrganizationSerializer, OrgCreateSerializer, OrgUpdateSerializer
from bothub import utils


class InternalOrganizationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = "pk"
    metadata_class = Metadata

    def list(self, request, *args, **kwargs):
        user = utils.get_user(request.query_params.get("user_email"))
        serializer = OrganizationSerializer(user.get_user_organizations, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user, created = User.objects.get_or_create(
            email=request.data.get('user_email', None), defaults={"nickname": request.data.get('user_email', None)}
        )

        serializer = OrgCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = {
            "name": serializer.validated_data.get("organization_name"),
            "nickname": utils.organization_unique_slug_generator(
                serializer.validated_data.get("organization_name")
            ),
            "description": "",
            "locale": "",
        }

        org = Organization.objects.create(**validated_data)

        org.organization_authorizations.create(
            user=user, role=OrganizationAuthorization.ROLE_ADMIN
        )
        org_serializer = OrganizationSerializer(org)

        return Response(org_serializer.data)

    def destroy(self, request, *args, **kwargs):
        org = Organization.objects.get(pk=request.data.get("id", None))
        user, created = User.objects.get_or_create(
            email=request.query_params.get("user_email"), defaults={"nickname": request.query_params.get("user_email")}
        )

        perm = org.organization_authorizations.get(user=user)
        if perm.is_admin:
            org.delete()
            return Response({_("Organization deleted with success")})
        raise PermissionDenied

    def update(self, request, *args, **kwargs):
        serializer = OrgUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        org = Organization.objects.get(pk=request.query_params.get("org_id", None))

        auths = (
            RepositoryAuthorization.objects.exclude(repository__owner=org)
            .exclude(role=RepositoryAuthorization.ROLE_NOT_SETTED)
            .filter(user=org)
        )

        response = {
            "repositories_count": int(
                Repository.objects.filter(
                    models.Q(uuid__in=auths) | models.Q(owner=org)
                ).count()
            )
        }

        return Response(response)
