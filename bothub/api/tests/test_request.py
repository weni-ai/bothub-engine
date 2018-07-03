import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RequestRepositoryAuthorization

from ..views import RequestAuthorizationViewSet
from .utils import create_user_and_token


class RequestAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.post(
            '/api/request-authorization/',
            data,
            **authorization_header)
        response = RequestAuthorizationViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository': self.repository.uuid,
            'text': 'I can contribute',
        }, self.token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_forbidden_two_requests(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text='I can contribute')
        response, content_data = self.request({
            'repository': self.repository.uuid,
            'text': 'I can contribute',
        }, self.token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'non_field_errors',
            content_data.keys())
