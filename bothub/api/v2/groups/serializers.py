from rest_framework import serializers

from bothub.common.models import (
    RepositoryEntityGroup,
)


class RepositoryEntityGroupSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntityGroup
        fields = [
            "id",
        ]
        ref_name = None

        # read_only = ["is_default", "created_by", "last_update"]

    # is_default = serializers.BooleanField(default=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.validators.append(VersionNameNotExistValidator())
