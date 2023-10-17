from django.db import models
from django.contrib.auth import get_user_model

from bothub.common.models import Repository

User = get_user_model()


class ContentBase(models.Model):
    uuid = models.UUIDField()
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="user_content_bases", on_delete=models.SET_NULL, null=True, blank=True)
    repository = models.ForeignKey(Repository, related_name="repository_content_bases", on_delete=models.SET_NULL, null=True, blank=True)


class ContentBaseText(models.Model):
    text = models.TextField()
    content_base = models.ForeignKey(ContentBase, related_name="content_base_text", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ContentBaseFile(models.Model):
    file_url = models.TextField()
    file_extension = models.TextField()
    content_base = models.ForeignKey(ContentBase, related_name="content_base_file", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WeniGPTLog(models.Model):
    content_base = models.ForeignKey(ContentBase, related_name="weni_gpt_log", on_delete=models.SET_NULL, blank=True, null=True)
    weni_gpt_log = models.TextField()
    created_by = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()
