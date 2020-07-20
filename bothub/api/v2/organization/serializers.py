from rest_framework import serializers

from bothub.common.models import Organization, OrganizationAuthorization


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "nickname", "description", "verificated"]
        ref_name = None

    read_only = ["id", "verificated"]

    name = serializers.CharField(max_length=40, required=True)

    def create(self, validated_data):
        instance = super().create(validated_data)

        OrganizationAuthorization.objects.create(
            user=self.context.get("request").user,
            organization=instance,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )

        return instance
