import json

from django.test import TestCase
from django.test import RequestFactory
from django.test.utils import tag
from rest_framework import status

from bothub.api.v2.knowledge_base.views import QAKnowledgeBaseViewSet, QAtextViewSet
from bothub.common.models import (
    Repository,
    QAKnowledgeBase,
    QAtext,
    RepositoryAuthorization,
)
from bothub.common import languages

from bothub.api.v2.tests.utils import create_user_and_token


class DefaultSetUpKnowledgeBaseMixin:
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Repository 1",
            slug="repo",
            language=languages.LANGUAGE_EN,
        )

        self.repository_2 = Repository.objects.create(
            owner=self.owner,
            name="Repository 2",
            slug="repo2",
            language=languages.LANGUAGE_EN,
        )

        self.knowledge_base_1 = QAKnowledgeBase.objects.create(
            repository=self.repository, title="Testando knowledge"
        )

        self.knowledge_base_2 = QAKnowledgeBase.objects.create(
            repository=self.repository_2, title="Testando knowledge"
        )

        self.context_1 = QAtext.objects.create(
            knowledge_base=self.knowledge_base_1,
            text="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            language=languages.LANGUAGE_PT_BR,
        )

        self.context_2 = QAtext.objects.create(
            knowledge_base=self.knowledge_base_1,
            text="teste 2",
            language=languages.LANGUAGE_EN,
        )

        self.context_3 = QAtext.objects.create(
            knowledge_base=self.knowledge_base_2,
            text="teste 3",
            language=languages.LANGUAGE_PT_BR,
        )
        self.repository_auth = RepositoryAuthorization.objects.create(
            user=self.owner, repository=self.repository, role=3
        )


class ListQAKnowledgeBaseAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/qa/knowledge-base/", data, **authorization_header
        )

        response = QAKnowledgeBaseViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.owner_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

        response, content_data = self.request(
            {"repository_uuid": self.repository_2.uuid}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_deleted(self):
        self.knowledge_base_1.delete()
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 0)

    def test_withuout_repository_uuid(self):
        response, content_data = self.request(token=self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_title(self):
        response, content_data = self.request(
            {
                "repository_uuid": self.repository.uuid,
                "title": self.knowledge_base_1.title,
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)
        self.assertEqual(
            content_data.get("results")[0].get("id"), self.knowledge_base_1.pk
        )


class DestroyQAKnowledgeBaseAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.delete(
            "/v2/repository/qa/knowledge-base/{}/?repository_uuid={}".format(
                self.knowledge_base_1.id, self.repository.uuid
            ),
            **authorization_header,
        )
        response = QAKnowledgeBaseViewSet.as_view({"delete": "destroy"})(
            request, pk=self.knowledge_base_1.id, repository_uuid=self.repository.uuid
        )
        return response

    def test_okay(self):
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.knowledge_base_1.delete()
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateKnowledgeBaseAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.put(
            "/v2/repository/qa/knowledge-base/{}/?repository_uuid={}".format(
                self.knowledge_base_1.id, self.repository.uuid
            ),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = QAKnowledgeBaseViewSet.as_view({"put": "update"})(
            request, pk=self.knowledge_base_1.id, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)

        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository": str(self.repository.uuid), "title": "testing"},
            self.owner_token,
        )
        self.assertEqual(content_data.get("title"), "testing")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_okay(self):
        response, content_data = self.request(
            {"repository": str(self.repository.uuid), "title": "testing"},
            self.user_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateQAKnowledgeBaseAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.post(
            "/v2/repository/qa/knowledge-base/", data, **authorization_header
        )

        response = QAKnowledgeBaseViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository": str(self.repository.uuid), "title": "testing"},
            self.owner_token,
        )
        self.assertEqual(content_data.get("title"), "testing")
        self.assertEqual(content_data.get("user_name"), self.owner.nickname)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_data(self):
        response, content_data = self.request({}, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@tag("desc")
class DetailQAKnowledgeBaseAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/qa/knowledge-base/{}/?repository_uuid={}".format(
                self.knowledge_base_1.pk, self.repository.uuid
            ),
            **authorization_header,
        )

        response = QAKnowledgeBaseViewSet.as_view({"get": "retrieve"})(
            request, repository_uuid=self.repository.uuid, pk=self.knowledge_base_1.pk
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.repository, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("title"), self.knowledge_base_1.title)
        self.assertEqual(content_data.get("description"), self.context_1.text[:150])


class ListQAtextAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/qa/text/", data, **authorization_header
        )

        response = QAtextViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.owner_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 2)

        response, content_data = self.request(
            {"repository_uuid": self.repository_2.uuid}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_deleted(self):
        self.context_3.delete()
        response, content_data = self.request(
            {"repository_uuid": self.repository_2.uuid}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 0)

    def test_withuout_repository_uuid(self):
        response, content_data = self.request(token=self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_knowledge_base_id(self):
        response, content_data = self.request(
            {
                "repository_uuid": self.repository.uuid,
                "knowledge_base_id": self.knowledge_base_1.pk,
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 2)
        self.assertEqual(content_data.get("results")[0].get("id"), self.context_1.pk)


class DestroyQAtextAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.delete(
            "/v2/repository/qa/text/{}/?repository_uuid={}".format(
                self.context_1.pk, self.repository.uuid
            ),
            **authorization_header,
        )
        response = QAtextViewSet.as_view({"delete": "destroy"})(
            request, pk=self.context_1.pk, repository_uuid=self.repository.uuid
        )
        return response

    def test_okay(self):
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.context_1.delete()
        response = self.request(self.owner_token)
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateQAtextAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.put(
            "/v2/repository/qa/text/{}/?repository_uuid={}".format(
                self.context_1.pk, self.repository.uuid
            ),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = QAtextViewSet.as_view({"put": "update"})(
            request, pk=self.context_1.pk, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)

        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "text": "teste text",
                "language": languages.LANGUAGE_EN,
                "knowledge_base": self.knowledge_base_2.pk,
            },
            self.owner_token,
        )
        self.assertEqual(content_data.get("text"), "teste text")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_okay(self):
        response, content_data = self.request(
            {
                "text": "teste text",
                "language": languages.LANGUAGE_PT_BR,
                "knowledge_base": self.knowledge_base_1.pk,
            },
            self.user_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateQAtextAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.post(
            "/v2/repository/qa/text/", data, **authorization_header
        )

        response = QAtextViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "text": "teste text",
                "language": languages.LANGUAGE_PT,
                "knowledge_base": self.knowledge_base_1.pk,
            },
            self.owner_token,
        )

        self.assertEqual(content_data.get("text"), "teste text")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unique_together(self):
        response, content_data = self.request(
            {
                "text": "teste text",
                "language": languages.LANGUAGE_PT_BR,
                "knowledge_base": self.knowledge_base_1.pk,
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_data(self):
        response, content_data = self.request({}, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DetailQAtextAPITestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/qa/text/{}/?repository_uuid={}".format(
                self.context_1.pk, self.repository.uuid
            ),
            **authorization_header,
        )

        response = QAtextViewSet.as_view({"get": "retrieve"})(
            request, repository_uuid=self.repository.uuid, pk=self.context_1.pk
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.repository, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("text"), self.context_1.text)
