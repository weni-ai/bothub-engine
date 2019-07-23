import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryExampleEntity

from ..views import NewRepositoryTranslatedExampleViewSet
from ..views import RepositoryTranslatedExampleViewSet
from ..views import TranslationsViewSet

from .utils import create_user_and_token


class TranslateExampleTestCase(TestCase):
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
            text='hi')

    def request(self, data, user_token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(user_token.key),
        }
        request = self.factory.post(
            '/v1/translate-example/',
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = NewRepositoryTranslatedExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'oi',
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_unique_translate(self):
        language = languages.LANGUAGE_PT
        text = 'oi'

        RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text=text)

        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': language,
                'text': text,
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'non_field_errors',
            content_data.keys())

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'oi',
                'entities': [],
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_okay_with_entities(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entities_no_valid(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'nome',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entities_no_valid_2(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                    {
                        'start': 0,
                        'end': 3,
                        'entity': 'my',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_can_not_translate_to_same_language(self):
        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': self.example.repository_update.language,
                'text': 'oi',
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'language',
            content_data.keys())


class RepositoryTranslatedExampleRetrieveTestCase(TestCase):
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
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')
        self.private_translated = RepositoryTranslatedExample.objects.create(
            original_example=self.private_example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, translated, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/v1/translation/{}/'.format(translated.id),
            **authorization_header)
        response = RepositoryTranslatedExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=translated.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.translated.id)

    def test_private_okay(self):
        response, content_data = self.request(
            self.private_translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.private_translated.id)

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            self.private_translated,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryTranslatedExampleDestroyTestCase(TestCase):
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
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, translated, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/v1/translation/{}/'.format(translated.id),
            **authorization_header)
        response = RepositoryTranslatedExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=translated.id)
        return response

    def test_okay(self):
        response = self.request(
            self.translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response = self.request(
            self.translated,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class TranslationsViewTest(TestCase):
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
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, data, user_token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(user_token.key),
        } if user_token else {}
        request = self.factory.get(
            '/v1/translations/',
            data,
            **authorization_header)
        response = TranslationsViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_repository_not_found(self):
        response, content_data = self.request({
            'repository_uuid': uuid.uuid4(),
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_repository_uuid_invalid(self):
        response, content_data = self.request({
            'repository_uuid': 'invalid',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_forbidden(self):
        private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)

        response, content_data = self.request({
            'repository_uuid': private_repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

        user, user_token = create_user_and_token('user')
        response, content_data = self.request(
            {
                'repository_uuid': private_repository.uuid,
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_filter_from_language(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_ES),
            text='hola')
        translated = RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=languages.LANGUAGE_PT,
            text='oi')

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'from_language': self.example.repository_update.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            self.translated.id)

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'from_language': example.repository_update.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            translated.id)

    def test_filter_to_language(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_ES),
            text='hola')
        RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=languages.LANGUAGE_PT,
            text='oi')

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'to_language': self.translated.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'to_language': languages.LANGUAGE_DE,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            0)
