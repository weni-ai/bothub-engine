from rest_framework import serializers

from bothub.project.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "is_template",
            "name",
            "uuid",
            "timezone",
        ]
        ref_name = None
