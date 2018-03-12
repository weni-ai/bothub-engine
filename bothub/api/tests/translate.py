import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample

from ..views import NewRepositoryTranslatedExampleViewSet
from ..views import RepositoryTranslatedExampleViewSet

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
            data,
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
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'non_field_errors',
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
            language=languages.LANGUAGE_EN)
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
            '/api/translated/{}/'.format(translated.id),
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
