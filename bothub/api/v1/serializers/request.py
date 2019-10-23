from rest_framework import serializers
from django.utils.translation import gettext as _

from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import Repository
from ..fields import TextField


class NewRequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = ["user", "repository", "text"]
        ref_name = None

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects, style={"show": False}
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), style={"show": False}
    )
    text = TextField(
        label=_("Leave a message for repository administrators"),
        min_length=5,
        max_length=RequestRepositoryAuthorization._meta.get_field("text").max_length,
    )


class RequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            "id",
            "user",
            "user__nickname",
            "repository",
            "text",
            "approved_by",
            "approved_by__nickname",
            "created_at",
        ]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )
    approved_by__nickname = serializers.SlugRelatedField(
        source="approved_by", slug_field="nickname", read_only=True
    )


class ReviewAuthorizationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = ["approved_by"]
        ref_name = None

    approved_by = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}
    )

    def update(self, instance, validated_data):
        validated_data.update({"approved_by": self.context["request"].user})
        return super().update(instance, validated_data)
