import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity

from ..views import NewRepositoryExampleEntityViewSet
from ..views import RepositoryExampleEntityViewSet

from .utils import create_user_and_token


class NewRepositoryExampleEntityTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas')

    def request(self, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/entity/new/',
            data,
            **authorization_header)
        response = NewRepositoryExampleEntityViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository_example': self.example.id,
                'start': 11,
                'end': 18,
                'entity': 'name',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('value'),
            'Douglas')

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            user_token,
            {
                'repository_example': self.example.id,
                'start': 11,
                'end': 18,
                'entity': 'name',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryExampleEntityRetrieveTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas')
        self.entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='my name is Douglas')
        self.private_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.private_example,
            start=11,
            end=18,
            entity='name')

    def request(self, entity, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/entity/{}/'.format(entity.id),
            **authorization_header)
        response = RepositoryExampleEntityViewSet.as_view(
            {'get': 'retrieve'})(request, pk=entity.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.entity,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.entity.id)

    def test_private_okay(self):
        response, content_data = self.request(
            self.entity,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_private_forbidden(self):
        user, user_token = create_user_and_token()
        response, content_data = self.request(
            self.private_entity,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
