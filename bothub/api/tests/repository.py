import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common import languages
from bothub.common.models import RepositoryCategory
from bothub.common.models import Repository

from ..views import NewRepositoryViewSet
from ..views import RepositoryViewSet

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

    def test_invalid_slug(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'invalid slug',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('slug', content_data.keys())

    def test_invalid_language(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'test',
            'language': 'jj',
            'categories': [self.category.id],
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', content_data.keys())


class RetrieveRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.category = RepositoryCategory.objects.create(
            name='ID')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.repository.categories.add(self.category)

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_repository.categories.add(self.category)

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/repository/{}/'.format(repository.uuid),
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'get': 'retrieve'})(request, pk=repository.uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_allowed_in_public(self):
        # owner
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        # secondary user
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_allowed_in_private(self):
        # owner
        response, content_data = self.request(
            self.private_repository,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_forbidden_in_private(self):
        # secondary user
        response, content_data = self.request(
            self.private_repository,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
