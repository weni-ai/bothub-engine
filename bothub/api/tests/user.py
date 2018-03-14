import json

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.authentication.models import User

from ..views import RegisterUserViewSet
from ..views import UserViewSet

from .utils import create_user_and_token


class RegisterUserTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def request(self, data):
        request = self.factory.post(
            '/api/register/',
            data)
        response = RegisterUserViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        email = 'fake@user.com'
        password = 'abc!1234'
        response, content_data = self.request({
            'email': email,
            'name': 'Fake',
            'nick': 'fake',
            'password': password,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        user = User.objects.get(email=email)
        self.assertTrue(user.check_password(password))

    def test_invalid_password(self):
        response, content_data = self.request({
            'email': 'fake@user.com',
            'name': 'Fake',
            'nick': 'fake',
            'password': 'abc',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'password',
            content_data.keys())


class UserRetrieveTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user, self.user_token = create_user_and_token()

    def request(self, user, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/profile/{}/'.format(user.pk),
            **authorization_header)
        response = UserViewSet.as_view(
            {'get': 'retrieve'})(request, pk=user.pk)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.user,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)


class UserUpdateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user, self.user_token = create_user_and_token()

    def request(self, user, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.patch(
            '/api/profile/{}/'.format(user.pk),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)
        response = UserViewSet.as_view(
            {'patch': 'update'})(request, pk=user.pk, partial=True)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        new_locale = 'Maceió - Alagoas'
        response, content_data = self.request(
            self.user,
            {
                'locale': new_locale,
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('locale'),
            new_locale)

    def test_forbidden(self):
        user, user_token = create_user_and_token('other')
        response, content_data = self.request(
            self.user,
            {
                'locale': 'new locale',
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
