from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueValidator

from bothub.api.v2.organization.validators import OrganizationNotExistValidator
from bothub.common.models import Organization, OrganizationAuthorization


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "nickname",
            "description",
            "locale",
            "verificated",
            "count_repositories",
            "count_members",
            "authorization",
        ]
        ref_name = None

    read_only = ["id", "verificated"]

    id = serializers.PrimaryKeyRelatedField(style={"show": False}, read_only=True)
    name = serializers.CharField(max_length=40, required=True)
    nickname = serializers.SlugField(
        required=True,
        validators=[
            UniqueValidator(queryset=Organization.objects.all(), lookup="iexact")
        ],
        max_length=16
    )
    verificated = serializers.BooleanField(style={"show": False}, read_only=True)
    count_repositories = serializers.SerializerMethodField(style={"show": False})
    count_members = serializers.SerializerMethodField(style={"show": False})
    authorization = serializers.SerializerMethodField(style={"show": False})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(OrganizationNotExistValidator())

    def validate_nickname(self, value):
        return value.lower()

    def create(self, validated_data):
        instance = super().create(validated_data)

        OrganizationAuthorization.objects.create(
            user=self.context.get("request").user,
            organization=instance,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )

        return instance

    def get_count_repositories(self, obj):
        return obj.repository_owner.repositories.count()

    def get_count_members(self, obj):
        auths = OrganizationAuthorization.objects.filter(organization=obj).exclude(
            role=OrganizationAuthorization.LEVEL_NOTHING
        )
        return auths.count()

    def get_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        data = OrganizationAuthorizationSerializer(
            obj.get_organization_authorization(request.user)
        ).data
        return data


class OrganizationAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAuthorization
        fields = [
            "uuid",
            "user",
            "user__nickname",
            "organization",
            "organization__nickname",
            "role",
            "level",
            "can_read",
            "can_contribute",
            "can_write",
            "can_translate",
            "is_admin",
            "created_at",
            "user__is_organization",
        ]
        read_only = [
            "user",
            "user__nickname",
            "organization",
            "organization__nickname",
            "role",
            "created_at",
        ]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )
    organization__nickname = serializers.SlugRelatedField(
        source="organization", slug_field="nickname", read_only=True
    )
    user__is_organization = serializers.SlugRelatedField(
        source="user", slug_field="is_organization", read_only=True
    )


class OrganizationAuthorizationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAuthorization
        fields = ["role"]
        ref_name = None

    def validate(self, data):
        if self.instance.user == self.context.get("request").user.repository_owner:
            raise PermissionDenied(_("You cannot change your own role"))
        if data.get("role") == OrganizationAuthorization.LEVEL_NOTHING:
            raise PermissionDenied(_("You cannot set user role 0"))
        return data
