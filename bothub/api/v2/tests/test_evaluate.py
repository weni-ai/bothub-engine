import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.evaluate.views import EvaluateViewSet
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample, RepositoryUpdate
from .utils import create_user_and_token


# TestCases

class NewEvaluateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()
        self.authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
        }

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language='en'
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language='en',
            algorithm='statistical_model',
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_update=self.repository_update,
            text="teste",
            intent="greet",
        )

    def request(self, data):
        request = self.factory.post(
            '/api/v2/evaluate/',
            json.dumps(data),
            content_type='application/json',
            **self.authorization_header)
        response = EvaluateViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository': str(self.repository.uuid),
                'text': 'haha',
                'language': 'en',
                'intent': 'greet',
                'entities': []
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_intent(self):
        response, content_data = self.request(
            {
                'repository': str(self.repository.uuid),
                'text': 'haha',
                'language': 'en',
                'intent': '',
                'entities': []
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('intent', content_data)

    def test_entities_not_exists(self):
        response, content_data = self.request(
            {
                'repository': str(self.repository.uuid),
                'text': 'haha',
                'language': 'en',
                'intent': 'greet',
                'entities': [{"entity": "hello", "start": 0, "end": 3}]
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

        self.assertIn('entities', content_data)
