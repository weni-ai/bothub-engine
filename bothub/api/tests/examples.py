import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample

from ..views import RepositoryExamplesViewSet

from .utils import create_user_and_token


class ExamplesTestCase(TestCase):
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
            text='oi',
            language=languages.LANGUAGE_PT)

    def request(self, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/examples/',
            data,
            **authorization_header)
        response = RepositoryExamplesViewSet.as_view(
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

    def test_repository_uuid_required(self):
        response, content_data = self.request(
            {},
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            0)

    def test_repository_does_not_exist(self):
        response, content_data = self.request(
            {
                'repository_uuid': uuid.uuid4(),
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_invalid_repository_uuid(self):
        response, content_data = self.request(
            {
                'repository_uuid': 'invalid',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_language_filter(self):
        response_1, content_data_1 = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'language': languages.LANGUAGE_EN,
            },
            self.owner_token)
        self.assertEqual(
            response_1.status_code,
            status.HTTP_200_OK)
        self.assertGreaterEqual(
            content_data_1.get('count'),
            1)

        response_2, content_data_2 = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'language': languages.LANGUAGE_NL,
            },
            self.owner_token)
        self.assertEqual(
            response_2.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data_2.get('count'),
            0)

    def test_has_translation_filter(self):
        response_1, content_data_1 = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'has_translation': True,
            },
            self.owner_token)
        self.assertEqual(
            response_1.status_code,
            status.HTTP_200_OK)
        self.assertGreaterEqual(
            content_data_1.get('count'),
            1)

        response_2, content_data_2 = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'has_translation': False,
            },
            self.owner_token)
        self.assertEqual(
            response_2.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data_2.get('count'),
            0)
