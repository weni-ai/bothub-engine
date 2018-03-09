import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import RepositoryCategory

from ..views import NewRepositoryViewSet

from .utils import create_user_and_token


# TestCases

class NewRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.token = create_user_and_token()
        self.authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
        }

        self.category = RepositoryCategory.objects.create(
            name='ID')

    def request(self, data):
        request = self.factory.post(
            '/api/repository/new/',
            data,
            **self.authorization_header)
        response = NewRepositoryViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_fields_required(self):
        def request_and_check(field, data):
            response, content_data = self.request(data)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, content_data.keys())

        request_and_check('name', {
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })

        request_and_check('slug', {
            'name': 'Testing',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })

        request_and_check('language', {
            'name': 'Testing',
            'slug': 'test',
            'categories': [self.category.id],
        })

        request_and_check('categories', {
            'name': 'Testing',
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
        })
