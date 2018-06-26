import json

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryAuthorization

from ..views import RepositoryViewSet
from ..views import RepositoryAuthorizationViewSet
from ..views import RepositoryAuthorizationRoleViewSet

from .utils import create_user_and_token


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/repository/{}/{}/'.format(
                repository.owner.nickname,
                repository.slug),
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'get': 'authorization'})(
                request,
                owner__nickname=repository.owner.nickname,
                slug=repository.slug)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_owner_allowed_public(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('user'),
            self.owner.id)

    def test_user_allowed_public(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('user'),
            self.user.id)

    def test_owner_allowed_private(self):
        response, content_data = self.request(
            self.private_repository,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('user'),
            self.owner.id)

    def test_user_forbidden_private(self):
        response, content_data = self.request(
            self.private_repository,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class ListAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.user_auth = self.repository.get_user_authorization(self.user)
        self.user_auth.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        self.user_auth.save()

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/list-authorizations/',
            {
                'repository': repository.uuid,
            },
            **authorization_header)
        response = RepositoryAuthorizationViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

        self.assertEqual(
            content_data.get('count'),
            1)

        self.assertEqual(
            content_data.get('results')[0].get('user'),
            self.user.id)

    def test_user_forbidden(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class UpdateAuthorizationRoleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, repository, token, user, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.patch(
            '/api/authorization-role/{}/{}/'.format(
                repository.uuid, user.nickname),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)
        view = RepositoryAuthorizationRoleViewSet.as_view(
            {'patch': 'update'})
        response = view(
            request,
            repository__uuid=repository.uuid,
            user__nickname=user.nickname)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.user,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('role'),
            RepositoryAuthorization.ROLE_CONTRIBUTOR)

        user_authorization = self.repository.get_user_authorization(self.user)
        self.assertEqual(
            user_authorization.role,
            RepositoryAuthorization.ROLE_CONTRIBUTOR)

    def test_forbidden(self):
        response, content_data = self.request(
            self.repository,
            self.user_token,
            self.user,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_owner_can_t_set_your_role(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.owner,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
