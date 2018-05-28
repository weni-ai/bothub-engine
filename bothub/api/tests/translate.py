import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryExampleEntity

from ..views import NewRepositoryTranslatedExampleViewSet
from ..views import RepositoryTranslatedExampleViewSet
from ..views import NewRepositoryTranslatedExampleEntityViewSet
from ..views import RepositoryTranslatedExampleEntityViewSet

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
            '/api/translate-example/',
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
            '/api/translation/{}/'.format(translated.id),
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
            '/api/translation/{}/'.format(translated.id),
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


class NewRepositoryTranslatedExampleEntityTestCase(TestCase):
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
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='meu nome é Douglas')

    def request(self, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/translate-example/',
            data,
            **authorization_header)
        response = NewRepositoryTranslatedExampleEntityViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository_translated_example': self.translated.id,
                'start': 11,
                'end': 18,
                'entity': 'name',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('value'),
            'Douglas')

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            {
                'repository_translated_example': self.translated.id,
                'start': 11,
                'end': 18,
                'entity': 'name',
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryTranslatedExampleEntityRetrieveTestCase(TestCase):
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
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='meu nome é Douglas')
        self.translated_entity = RepositoryTranslatedExampleEntity.objects \
            .create(
                repository_translated_example=self.translated,
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
        self.private_translated = RepositoryTranslatedExample.objects.create(
            original_example=self.private_example,
            language=languages.LANGUAGE_PT,
            text='meu nome é Douglas')
        self.private_translated_entity = RepositoryTranslatedExampleEntity \
            .objects.create(
                repository_translated_example=self.private_translated,
                start=11,
                end=18,
                entity='name')

    def request(self, translated_entity, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/translation-entity/{}/'.format(translated_entity.id),
            **authorization_header)
        response = RepositoryTranslatedExampleEntityViewSet.as_view(
            {'get': 'retrieve'})(request, pk=translated_entity.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.translated_entity,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.translated_entity.id)

    def test_private_okay(self):
        response, content_data = self.request(
            self.private_translated_entity,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.private_translated_entity.id)

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            self.private_translated_entity,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryTranslatedExampleEntityDestroyTestCase(TestCase):
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
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='meu nome é Douglas')
        self.translated_entity = RepositoryTranslatedExampleEntity.objects \
            .create(
                repository_translated_example=self.translated,
                start=11,
                end=18,
                entity='name')

    def request(self, translated_entity, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/api/translation-entity/{}/'.format(translated_entity.id),
            **authorization_header)
        response = RepositoryTranslatedExampleEntityViewSet.as_view(
            {'delete': 'destroy'})(request, pk=translated_entity.id)
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
