import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity

from ..views import NewRepositoryExampleViewSet
from ..views import RepositoryExampleViewSet
from ..views import RepositoryEntitiesViewSet

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
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = NewRepositoryExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        text = 'hi'
        intent = 'greet'
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'intent': intent,
                'entities': [],
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

    def test_forbidden(self):
        response, content_data = self.request(
            self.user_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
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
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_repository_does_not_exists(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(uuid.uuid4()),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'repository',
            content_data.keys())

    def test_invalid_repository_uuid(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': 'invalid',
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_with_entities(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_with_entities_with_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'subject',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)
        id = content_data.get('id')
        repository_example = RepositoryExample.objects.get(id=id)
        example_entity = repository_example.entities.all()[0]
        self.assertIsNotNone(example_entity.entity.label)

    def test_intent_or_entity_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': '',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_entity_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': '',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'nam&',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_intent_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'nam$s',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('intent')),
            1)


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
            text='my name is douglas')
        self.example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')

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

    def test_list_entities(self):
        response, content_data = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entity_has_label(self):
        response, content_data = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        entity = content_data.get('entities')[0]
        self.assertIn(
            'label',
            entity.keys())

    def test_entity_has_valid_label(self):
        label = 'subject'
        self.example_entity.entity.set_label('subject')
        self.example_entity.entity.save(update_fields=['label'])
        response, content_data = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        entity = content_data.get('entities')[0]
        self.assertIn(
            'label',
            entity.keys())
        self.assertEqual(
            entity.get('label'),
            label)


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


class RepositoryEntitiesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.entity_value = 'douglas'

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        self.example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity=self.entity_value)
        self.example_entity.entity.set_label('name')
        self.example_entity.entity.save()

    def request(self, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/entities/',
            data=data,
            **authorization_header)
        response = RepositoryEntitiesViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(content_data.get('count'), 1)

        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'value': self.entity_value,
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(content_data.get('count'), 1)

        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'value': 'other',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(content_data.get('count'), 0)
