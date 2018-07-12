import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.common import languages
from bothub.common.models import RepositoryCategory
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RequestRepositoryAuthorization

from ..views import NewRepositoryViewSet
from ..views import RepositoryViewSet
from ..views import MyRepositoriesViewSet
from ..views import RepositoriesViewSet

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
            'description': '',
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
            'description': '',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', content_data.keys())

    def test_unique_slug(self):
        same_slug = 'test'
        Repository.objects.create(
            owner=self.user,
            name='Testing',
            slug=same_slug,
            language=languages.LANGUAGE_EN)
        response, content_data = self.request({
            'name': 'Testing',
            'slug': same_slug,
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
            'description': '',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', content_data.keys())


class RetrieveRepositoryTestCase(TestCase):
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
            {'get': 'retrieve'})(
                request,
                owner__nickname=repository.owner.nickname,
                slug=repository.slug)
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

    def test_languages_status(self):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
        }
        request = self.factory.get(
            '/api/repository/{}/{}/languagesstatus/'.format(
                self.repository.owner.nickname,
                self.repository.uuid),
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'get': 'languagesstatus'})(
                request,
                owner__nickname=self.repository.owner.nickname,
                slug=self.repository.slug)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_available_request_authorization(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertTrue(content_data.get('available_request_authorization'))

    def test_owner_not_available_request_authorization(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        self.assertFalse(content_data.get('available_request_authorization'))

    def test_user_not_available_request_authorization(self):
        authorization = self.repository.get_user_authorization(self.user)
        authorization.role = RepositoryAuthorization.ROLE_USER
        authorization.save()
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertFalse(content_data.get('available_request_authorization'))

    def test_requested_not_available_request_authorization(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text='I can contribute')
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertFalse(content_data.get('available_request_authorization'))

    def test_none_request_authorization(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)
        self.assertIsNone(content_data.get('request_authorization'))

    def test_request_authorization(self):
        text = 'I can contribute'
        request = RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text=text)
        response, content_data = self.request(
            self.repository,
            self.user_token)
        request_authorization = content_data.get('request_authorization')
        self.assertEqual(
            request_authorization.get('id'),
            request.id)
        self.assertEqual(
            request_authorization.get('text'),
            text)


class UpdateRepositoryTestCase(TestCase):
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

    def request(self, repository, token, data, partial=True):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.patch(
            '/api/repository/{}/{}/'.format(
                repository.owner.nickname,
                repository.slug),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'patch': 'update'})(
                request,
                owner__nickname=repository.owner.nickname,
                slug=repository.slug,
                partial=partial)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_allowed(self):
        new_slug = 'test_2'
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            {'slug': new_slug})
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('slug'),
            new_slug)

    def test_forbidden(self):
        new_slug = 'test_2'
        response, content_data = self.request(
            self.repository,
            self.user_token,
            {'slug': new_slug})
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_update_fields(self):
        new_category = RepositoryCategory.objects.create(
            name='Other')
        mockups = [
            (
                'name',
                'New Name',
                True),
            (
                'language',
                languages.LANGUAGE_PT,
                True),
            (
                'categories',
                [
                    self.category.id,
                    new_category.id,
                ],
                True),
            (
                'description',
                'Add description',
                True),
            (
                'is_private',
                True,
                True),
            (
                'uuid',
                uuid.uuid4(),
                False),
            (
                'slug',
                'test-slug',
                True),
        ]
        for (field, value, equal,) in mockups:
            response, content_data = self.request(
                self.repository,
                self.owner_token,
                {field: value})
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK)
            if equal:
                self.assertEqual(
                    content_data.get(field),
                    value)
            else:
                self.assertNotEqual(
                    content_data.get(field),
                    value)


class DestroyRepositoryTestCase(TestCase):
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

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/api/repository/{}/{}/'.format(
                repository.owner.nickname,
                repository.slug),
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'delete': 'destroy'})(
                request,
                owner__nickname=repository.owner.nickname,
                slug=repository.slug)
        response.render()
        return response

    def test_allowed(self):
        response = self.request(
            self.repository,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        response = self.request(
            self.repository,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class MyRepositoriesTestCase(TestCase):
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

    def request(self, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/my-repositories/',
            **authorization_header)
        response = MyRepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            uuid.UUID(content_data.get('results')[0].get('uuid')),
            self.repository.uuid)

    def test_empty_okay(self):
        response, content_data = self.request(self.user_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('count'),
            0)


class RepositoriesTestCase(TestCase):
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
            name='Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.repository.categories.add(self.category)

    def request(self, data={}):
        request = self.factory.get(
            '/api/repositories/',
            data)
        response = RepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_show_just_publics(self):
        response, content_data = self.request()
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            uuid.UUID(content_data.get('results')[0].get('uuid')),
            self.repository.uuid)

    def test_filter_by_name(self):
        response, content_data = self.request({
            'search': 'Test',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

        response, content_data = self.request({
            'search': 'z',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            0)


class TrainRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/repository/{}/{}/train/'.format(
                repository.owner.nickname,
                repository.slug),
            **authorization_header)
        response = RepositoryViewSet.as_view({'get': 'train'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_permission_denied(self):
        response, content_data = self.request(self.repository, self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class AnalyzeRepositoryTestCase(TestCase):
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
            name='Testing',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)

    def request(self, repository, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/repository/{}/{}/analyze/'.format(
                repository.owner.nickname,
                repository.slug),
            data,
            **authorization_header)
        response = RepositoryViewSet.as_view({'post': 'analyze'})(
            request,
            owner__nickname=repository.owner.nickname,
            slug=repository.slug)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_permission_denied_in_private_repository(self):
        response, content_data = self.request(
            self.private_repository,
            self.user_token,
            {
                'language': 'en',
                'text': 'My name is Douglas',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_language_required(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            {
                'language': '',
                'text': 'My name is Douglas',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', content_data.keys())

    def test_text_required(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            {
                'language': 'en',
                'text': '',
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', content_data.keys())


class LanguagesStatusTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.example_1 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hi',
            intent='greet')
        self.example_2 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='Here is London',
            intent='place')
        self.example_3 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='Here is Brazil',
            intent='place')

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/repository/{}/{}/languagesstatus/'.format(
                repository.owner.nickname,
                repository.slug),
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'get': 'languagesstatus'})(request)
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

    def test_unique_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example_1,
            start=0,
            end=0,
            entity='entity1')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example_2,
            start=0,
            end=0,
            entity='entity1')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example_3,
            start=0,
            end=0,
            entity='entity2')

        counter = {}
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        languages_status = content_data.get('languages_status')
        for language in languages_status:
            language_status = languages_status.get(language)
            for entity in language_status.get('examples').get('entities'):
                counter[entity] = counter.get(entity, 0) + 1
                self.failIfEqual(counter.get(entity), 2)

    def test_none_entities(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        languages_status = content_data.get('languages_status')
        for language in languages_status:
            language_status = languages_status.get(language)
            for entity in language_status.get('examples').get('entities'):
                self.failIfEqual(entity, None)


class RepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, repository, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.post(
            '/api/repository/{}/{}/vote/'.format(
                repository.owner.nickname,
                repository.slug),
            data,
            **authorization_header)
        response = RepositoryViewSet.as_view(
            {'post': 'vote'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_unauthorized(self):
        response, content_data = self.request(self.repository)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED)

    def test_invalid_vote(self):
        response, content_data = self.request(
            self.repository,
            {
                'vote': 2,
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'vote',
            content_data.keys())

    def test_vote_up(self):
        response, content_data = self.request(
            self.repository,
            {
                'vote': RepositoryVote.UP_VOTE,
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        vote = RepositoryVote.objects.get(
            repository=self.repository,
            user=self.user)
        self.assertEqual(
            vote.vote,
            RepositoryVote.UP_VOTE)
        self.assertEqual(
            self.repository.votes_sum,
            1)
        self.assertEqual(
            content_data.get('votes_sum'),
            1)

    def test_vote_down(self):
        response, content_data = self.request(
            self.repository,
            {
                'vote': RepositoryVote.DOWN_VOTE,
            },
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        vote = RepositoryVote.objects.get(
            repository=self.repository,
            user=self.user)
        self.assertEqual(
            vote.vote,
            RepositoryVote.DOWN_VOTE)
        self.assertEqual(
            self.repository.votes_sum,
            -1)
