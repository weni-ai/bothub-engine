import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from ..views import RegisterUserViewSet


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
        response, content_data = self.request({
            'email': 'fake@user.com',
            'name': 'Fake',
            'nick': 'fake',
            'password': 'abc!1234',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

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
