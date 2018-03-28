import json

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.authentication.models import User

from ..views import RegisterUserViewSet
from ..views import UserViewSet
from ..views import LoginViewSet
from ..views import ChangePasswordViewSet
from ..views import RequestResetPassword

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
            'nickname': 'fake',
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
            'nickname': 'fake',
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


class LoginTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.password = 'abcgq!!123'
        self.email = 'user@user.com'

        user = User.objects.create(
            email=self.email,
            nickname='user',
            name='User')
        user.set_password(self.password)
        user.save(update_fields=['password'])

    def request(self, data):
        request = self.factory.post(
            '/api/login/',
            data)
        response = LoginViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'username': self.email,
            'password': self.password,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertIn(
            'token',
            content_data.keys())

    def test_wrong_password(self):
        response, content_data = self.request({
            'username': self.email,
            'password': 'wrong',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)


class ChangePasswordTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user, self.user_token = create_user_and_token()
        self.password = '12555q!66'
        self.user.set_password(self.password)
        self.user.save(update_fields=['password'])

    def request(self, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/',
            data,
            **authorization_header)
        response = ChangePasswordViewSet.as_view(
            {'post': 'update'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        new_password = 'kkl8&!qq'
        response, content_data = self.request(
            {
                'current_password': self.password,
                'password': new_password,
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_wrong_password(self):
        response, content_data = self.request(
            {
                'current_password': 'wrong_password',
                'password': 'new_password',
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'current_password',
            content_data.keys())


class RequestResetPasswordTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.email = 'user@user.com'

        User.objects.create(
            email=self.email,
            nickname='user',
            name='User')

    def request(self, data):
        request = self.factory.post(
            '/api/forgot-password/',
            data)
        response = RequestResetPassword.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'email': self.email,
        })
        print(response.status_code, content_data)

    def test_email_not_found(self):
        response, content_data = self.request({
            'email': 'nouser@fake.com',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'email',
            content_data.keys())
