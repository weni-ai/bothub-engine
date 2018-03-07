import json
import random
import uuid

from django.test import TestCase, RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework.authtoken.models import Token

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryCategory
from bothub.common import languages

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet
from .views import NewRepositoryExampleViewSet
from .views import RepositoryExampleViewSet
from .views import RepositoryAuthorizationView
from .views import NewRepositoryExampleEntityViewSet
from .views import NewRepositoryTranslatedExampleViewSet


class APITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            'fake@user.com',
            'user',
            '123456')
        self.user_token, create = Token.objects.get_or_create(user=self.user)

        self.other_user = User.objects.create_user(
            'fake2@user.com',
            'user2',
            '123456')
        self.other_user_token, create = Token.objects.get_or_create(
            user=self.other_user)

        self.category = RepositoryCategory.objects.create(
            name='category')

        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='test',
            language=languages.LANGUAGE_EN)
        self.repository.categories.add(self.category)

        self.private_repository = Repository.objects.create(
            owner=self.user,
            slug='private',
            is_private=True,
            name='private test',
            language=languages.LANGUAGE_EN)
        self.private_repository.categories.add(self.category)

        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hey Douglas',
            intent='greet')

    def _new_repository_request(self, slug, name, language, categories):
        request = self.factory.post(
            '/api/repository/new/',
            {
                'slug': slug,
                'name': name,
                'language': language,
                'categories': categories,
            },
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_repository(self):
        test_slug = 'test_{}'.format(random.randint(100, 9999))
        (response, content_data) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content_data.get('slug'), test_slug)

    def test_new_repository_unique_slug(self):
        test_slug = 'test_{}'.format(random.randint(100, 9999))
        (response_1, content_data_1) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response_1.status_code, 201)
        (response_2, content_data_2) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response_2.status_code, 400)

    def test_my_repositories(self):
        request = self.factory.get(
            '/api/myrepositories/',
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = MyRepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('results')[0].get('uuid'),
            str(self.repository.uuid))

    def test_repository_retrieve(self):
        request = self.factory.get(
            '/api/repository/{}/'.format(self.repository.uuid),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view({'get': 'retrieve'})(
            request,
            pk=str(self.repository.uuid))
        response.render()
        content_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get('uuid'), str(self.repository.uuid))

    def _repository_currentupdate_request(self, data):
        request = self.factory.post(
            '/api/repository/{}/currentupdate/'.format(self.repository.uuid),
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'post': 'currentupdate'})(request, pk=str(self.repository.uuid))
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_repository_currentupdate(self):
        response, content_data = self._repository_currentupdate_request({
            'language': languages.LANGUAGE_EN,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('repository'),
            str(self.repository.uuid))

    def test_repository_currentupdate_without_language(self):
        response, content_data = self._repository_currentupdate_request({})
        self.assertEqual(response.status_code, 500)

    def _repository_examples_request(self, data):
        request = self.factory.post(
            '/api/repository/{}/examples/'.format(self.repository.uuid),
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'post': 'examples'})(request, pk=str(self.repository.uuid))
        response.render()
        return response

    def test_repository_examples(self):
        response = self._repository_examples_request({
            'language': languages.LANGUAGE_EN,
        })
        self.assertEqual(response.status_code, 200)

    def test_repository_examples_without_language(self):
        response = self._repository_examples_request({})
        self.assertEqual(response.status_code, 500)

    def _repository_currentrasanludata_request(self, data):
        request = self.factory.post(
            '/api/repository/{}/currentrasanludata/'.format(
                self.repository.uuid),
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'post': 'currentrasanludata'})(
                request,
                pk=str(self.repository.uuid))
        response.render()
        return response

    def test_repository_currentrasanludata(self):
        response = self._repository_currentrasanludata_request({
            'language': languages.LANGUAGE_EN,
        })
        self.assertEqual(response.status_code, 200)

    def test_repository_currentrasanludata_without_language(self):
        response = self._repository_currentrasanludata_request({})
        self.assertEqual(response.status_code, 500)

    def _repository_authorization_request(self, token=None, **data):
        token = token or self.user_token.key
        request = self.factory.post(
            '/api/authorization/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(token),
            })
        response = RepositoryAuthorizationView.as_view(
            {'post': 'create'})(request)
        response.render()
        return response

    def test_repository_authorization(self):
        response = self._repository_authorization_request(
            repository_uuid=self.repository.uuid)
        self.assertEqual(response.status_code, 200)

    def test_repository_authorization_private_and_authorized(self):
        response = self._repository_authorization_request(
            repository_uuid=self.private_repository.uuid)
        self.assertEqual(response.status_code, 200)

    def test_repository_authorization_private_and_unauthorized(self):
        response = self._repository_authorization_request(
            repository_uuid=self.private_repository.uuid,
            token=self.other_user_token.key)
        self.assertEqual(response.status_code, 403)

    def test_repository_authorization_without_repository_uuid(self):
        response = self._repository_authorization_request()
        self.assertEqual(response.status_code, 500)

    def test_repository_authorization_repository_does_not_exist(self):
        response = self._repository_authorization_request(
            repository_uuid=uuid.uuid4())
        self.assertEqual(response.status_code, 404)

    def test_repository_authorization_repository_uuid_invalid(self):
        response = self._repository_authorization_request(
            repository_uuid='invalid')
        self.assertEqual(response.status_code, 500)

    def _update_repository_request(self, repository_uuid, data):
        request = self.factory.put(
            '/api/repository/{}/'.format(repository_uuid),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'put': 'update'})(request, pk=repository_uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_repository_update(self):
        new_slug = 'test_{}'.format(random.randint(1, 10))
        (response, content_data) = self._update_repository_request(
            str(self.repository.uuid),
            {
                'slug': new_slug,
                'is_private': True,
                'name': self.repository.name,
                'language': self.repository.language,
                'categories': [self.category.id],
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get('slug'), new_slug)
        self.assertEqual(content_data.get('is_private'), True)

    def test_repository_cannot_update_uuid(self):
        new_uuid = str(uuid.uuid4())
        new_slug = 'test_{}'.format(random.randint(1, 10))
        (response, content_data) = self._update_repository_request(
            str(self.repository.uuid),
            {
                'uuid': new_uuid,
                'slug': new_slug,
                'name': self.repository.name,
                'language': self.repository.language,
                'categories': [self.category.id],
            })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(content_data.get('uuid'), new_uuid)

    def test_repository_destroy(self):
        request = self.factory.delete(
            '/api/repository/{}/'.format(self.repository.uuid),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'delete': 'destroy'})(request, pk=str(self.repository.uuid))
        response.render()
        self.assertEqual(response.status_code, 204)

    def _new_repository_example_request(self, data):
        request = self.factory.post(
            '/api/example/new/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_repository_example(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': self.repository.uuid,
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 201)

    def test_new_repository_example_without_repository_uuid(self):
        response, content_data = self._new_repository_example_request({
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 400)

    def test_new_repository_example_repository_does_not_exists(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': uuid.uuid4(),
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 404)

    def test_new_repository_example_invalid_repository_uuid(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': 'invalid',
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 400)

    def test_repository_example_retrieve(self):
        request = self.factory.get(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_repository_example_destroy(self):
        request = self.factory.delete(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 204)
        self.example = RepositoryExample.objects.get(id=self.example.id)
        self.assertEqual(
            self.example.deleted_in,
            self.repository.current_update(
                self.example.repository_update.language))

    def test_repository_example_already_deleted(self):
        self.example.delete()
        request = self.factory.delete(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 500)

    def _new_repository_example_entity_request(self, data):
        request = self.factory.post(
            '/api/entity/new/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryExampleEntityViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_repository_example_entity(self):
        response, content_data = self._new_repository_example_entity_request({
            'repository_example': self.example.id,
            'start': 4,
            'end': 11,
            'entity': 'name',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content_data.get('value'), 'Douglas')

    def test_translate_example(self):
        request = self.factory.post(
            '/api/translateexample/',
            {
               'original_example': self.example.id,
               'language': languages.LANGUAGE_PT,
               'text': 'ei Douglas',
            },
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryTranslatedExampleViewSet.as_view(
            {'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
