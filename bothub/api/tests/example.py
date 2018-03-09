import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository

from ..views import NewRepositoryExampleViewSet

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
