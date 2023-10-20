from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bothub.authentication.models import User
from bothub.common.models import Organization, OrganizationAuthorization, QAKnowledgeBase, Repository


class OrganizationSerializer(serializers.ModelSerializer):

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
        fields = ["id", "name", "users"]


class OrgCreateSerializer(serializers.ModelSerializer):

    organization_name = serializers.CharField()
    user_email = serializers.CharField()

    def validate_user_email(self, value: str) -> str:
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError(_("{} not found!").format(value))

        return value

    class Meta:
        model = Organization
        fields = ["organization_name", "user_email"]


class OrgUpdateSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    name = serializers.CharField(required=False)

    def validate_id(self, value):
        try:
            Organization.objects.get(pk=value)
        except Organization.DoesNotExist:
            raise ValidationError(f"{value} not found!")

        return value

    def save(self):
        data = dict(self.validated_data)

        org = Organization.objects.get(pk=data.get("id"))

        updated_fields = self.get_updated_fields(data)

        if updated_fields:
            org.__dict__.update(**updated_fields)
        org.save()

    def get_updated_fields(self, data):
        return {key: value for key, value in data.items() if key not in ["id"]}

    class Meta:
        model = Organization
        fields = ["id", "name"]


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAKnowledgeBase
        fields = ["knowledge_base_id", "knowledge_base_title", "texts", "intelligence_name", "intelligence_uuid"]
    
    knowledge_base_id = serializers.SerializerMethodField()
    knowledge_base_title = serializers.SerializerMethodField()
    texts = serializers.SerializerMethodField()
    intelligence_name = serializers.SerializerMethodField()
    intelligence_uuid = serializers.SerializerMethodField()

    def get_knowledge_base_id(self, knowledge_base: QAKnowledgeBase):
        return knowledge_base.id

    def get_knowledge_base_title(self, knowledge_base: QAKnowledgeBase):
        return knowledge_base.title

    def get_texts(self, knowledge_base: QAKnowledgeBase):
        return [{"text": text.text, "language": text.language} for text in knowledge_base.texts.all()]

    def get_intelligence_name(self, knowledge_base: QAKnowledgeBase): 
        return knowledge_base.repository.name,

    def get_intelligence_uuid(self, knowledge_base: QAKnowledgeBase):
        return str(knowledge_base.repository.uuid)
