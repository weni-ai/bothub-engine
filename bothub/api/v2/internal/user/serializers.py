from rest_framework import serializers

from bothub.authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "language",
            "joined_at",
            "is_active",
            "is_superuser",
        ]


class UserPermissionSerializer(serializers.Serializer):
    role = serializers.IntegerField()


class UserLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["language"]
        read_only = [
            "id",
            "email",
            "nickname",
            "name",
            "joined_at",
            "is_active",
            "is_superuser",
        ]
