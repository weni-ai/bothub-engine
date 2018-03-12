import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample

from ..views import NewRepositoryExampleViewSet
from ..views import RepositoryExampleViewSet

from .utils import create_user_and_token


class NewRepositoryExampleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/example/new/',
            data,
            **authorization_header)
        response = NewRepositoryExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        text = 'hi'
        intent = 'greet'
        current_update = self.repository.current_update()
        response, content_data = self.request(
            self.owner_token,
            {
                'repository_uuid': self.repository.uuid,
                'text': text,
                'intent': intent,
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)
        self.assertEqual(
            content_data.get('repository_update'),
            current_update.id)

    def test_forbidden(self):
        response, content_data = self.request(
            self.user_token,
            {
                'repository_uuid': self.repository.uuid,
                'text': 'hi',
                'intent': 'greet',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_repository_uuid_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'text': 'hi',
                'intent': 'greet',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_repository_does_not_exists(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository_uuid': uuid.uuid4(),
                'text': 'hi',
                'intent': 'greet',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_invalid_repository_uuid(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository_uuid': 'invalid',
                'text': 'hi',
                'intent': 'greet',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)


class RepositoryExampleRetrieveTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, example, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/example/{}/'.format(example.id),
            **authorization_header)
        response = RepositoryExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=example.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.example.id)

    def test_forbidden(self):
        response, content_data = self.request(
            self.private_example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_public(self):
        response, content_data = self.request(
            self.example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.example.id)


class RepositoryExampleDestroyTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, example, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/api/example/{}/'.format(example.id),
            **authorization_header)
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=example.id)
        return response

    def test_okay(self):
        response = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(
            self.private_example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        response = self.request(
            self.example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_private_forbidden(self):
        response = self.request(
            self.private_example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.example.delete()

        response = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
