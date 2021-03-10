from django.db.models import F
from django_grpc_framework import proto_serializers
from rest_framework import serializers

from bothub.authentication.models import User
from bothub.common.models import Organization, OrganizationAuthorization
from bothub.protos import organization_pb2


class SerializerUtils(object):
    @classmethod
    def get_object(cls, model, pk: int):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise proto_serializers.ValidationError(
                f"{model.__name__}: {pk} not found!"
            )

    @classmethod
    def get_user_object(cls, model, email: str):
        try:
            return model.objects.get(email=email)
        except model.DoesNotExist:
            raise proto_serializers.ValidationError(
                f"{model.__name__}: {email} not found!"
            )


class OrgProtoSerializer(proto_serializers.ModelProtoSerializer):

    users = serializers.SerializerMethodField()

    def get_users(self, org: Organization):
        return list(
            org.organization_authorizations.exclude(
                role=OrganizationAuthorization.LEVEL_NOTHING
            )
            .annotate(
                org_user_id=F("user__user_owner__pk"),
                org_user_email=F("user__user_owner__email"),
                org_user_nickname=F("user__user_owner__nickname"),
                org_user_name=F("user__user_owner__name"),
            )
            .values(
                "org_user_id", "org_user_email", "org_user_nickname", "org_user_name"
            )
        )

    class Meta:
        model = Organization
        proto_class = organization_pb2.Org
        fields = ["id", "name", "users"]


class OrgCreateProtoSerializer(proto_serializers.ModelProtoSerializer):

    user_email = serializers.CharField()

    def validate_user_email(self, value: str) -> str:
        SerializerUtils.get_user_object(User, value)

        return value

    class Meta:
        model = Organization
        proto_class = organization_pb2.Org
        fields = ["name", "user_email"]


class OrgUpdateProtoSerializer(proto_serializers.ModelProtoSerializer):

    id = serializers.IntegerField()
    user_email = serializers.CharField()
    name = serializers.CharField(required=False)

    def validate_id(self, value):
        SerializerUtils.get_object(Organization, value)

        return value

    def validate_user_email(self, value):
        SerializerUtils.get_user_object(User, value)

        return value

    def save(self):
        data = dict(self.validated_data)

        org = Organization.objects.get(pk=data.get("id"))
        user = SerializerUtils.get_user_object(User, data.get("user_email"))

        if not self._user_has_permisson(user, org):
            raise proto_serializers.ValidationError(
                f"User: {user.pk} has no permission to update Org: {org.pk}"
            )

        updated_fields = self.get_updated_fields(data)

        if updated_fields:
            org.__dict__.update(**updated_fields)

    def get_updated_fields(self, data):
        return {
            key: value for key, value in data.items() if key not in ["id", "user_email"]
        }

    def _user_has_permisson(self, user: User, org: Organization) -> bool:
        return (
            org.organization_authorizations.exclude(
                role=OrganizationAuthorization.LEVEL_NOTHING
            )
            .get(user=user)
            .is_admin
        )

    class Meta:
        model = Organization
        proto_class = organization_pb2.Org
        fields = ["id", "user_email", "name"]
