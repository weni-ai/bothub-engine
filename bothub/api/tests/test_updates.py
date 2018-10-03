import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status
from bothub.common.models import Repository
from bothub.common import languages

from ..views import RepositoryUpdatesViewSet
from .utils import create_user_and_token


class UpdatesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.repository.current_update()

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.get(
            '/api/updates/',
            data,
            **authorization_header)
        response = RepositoryUpdatesViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository_uuid': str(self.repository.uuid),
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_not_authenticated(self):
        response, content_data = self.request(
            {
                'repository_uuid': str(self.repository.uuid),
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED)

    def test_without_repository(self):
        response, content_data = self.request(
            {},
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            0)
