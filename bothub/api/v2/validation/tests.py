import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate
from bothub.common.models import RepositoryValidation
from bothub.common.models import RepositoryTranslatedValidation
from bothub.common.models import RepositoryValidationEntity
from bothub.common import languages

from ..tests.utils import create_user_and_token
from .views import NewValidationViewSet
from .views import ListValidationViewSet
from .views import ListValidationsViewSet




class CreateValidationAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/api/v2/validation/new/',
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = NewValidationViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        text = 'hi'
        intent = 'greet'
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'intent': intent,
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)

    def test_okay_with_language(self):
        text = 'hi'
        intent = 'greet'
        language = languages.LANGUAGE_PT
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'language': language,
                'intent': intent,
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)
        repository_update_pk = content_data.get('repository_update')
        repository_update = RepositoryUpdate.objects.get(
            pk=repository_update_pk)
        self.assertEqual(repository_update.language, language)

    def test_forbidden(self):
        response, content_data = self.request(
            self.user_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_repository_uuid_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_repository_does_not_exists(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(uuid.uuid4()),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'repository',
            content_data.keys())

    def test_invalid_repository_uuid(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': 'invalid',
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_with_entities(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_with_entities_with_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'subject',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)
        id = content_data.get('id')
        repository_validation = RepositoryValidation.objects.get(id=id)
        validation_entity = repository_validation.entities.all()[0]
        self.assertIsNotNone(validation_entity.entity.label)

    def test_with_entities_with_invalid_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'other',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'entities',
            content_data.keys())
        entities_errors = content_data.get('entities')
        self.assertIn(
            'label',
            entities_errors[0])

    def test_with_entities_with_equal_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'name',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'entities',
            content_data.keys())
        entities_errors = content_data.get('entities')
        self.assertIn(
            'label',
            entities_errors[0])

    def test_intent_or_entity_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': '',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_entity_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': '',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'nam&',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_intent_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'nam$s',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('intent')),
            1)


class RetrieveValidationAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.validation = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        self.validation_entity = RepositoryValidationEntity.objects.create(
            repository_validation=self.validation,
            start=11,
            end=18,
            entity='name')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_validation = RepositoryValidation.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, validation, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/api/v2/validation/{}/'.format(validation.id),
            **authorization_header)
        response = ListValidationViewSet.as_view(
            {'get': 'retrieve'})(request, pk=validation.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.validation.id)

    def test_forbidden(self):
        response, content_data = self.request(
            self.private_validation,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_public(self):
        response, content_data = self.request(
            self.validation,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.validation.id)

    def test_list_entities(self):
        response, content_data = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entity_has_label(self):
        response, content_data = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        entity = content_data.get('entities')[0]
        self.assertIn(
            'label',
            entity.keys())

    def test_entity_has_valid_label(self):
        label = 'subject'
        self.validation_entity.entity.set_label('subject')
        self.validation_entity.entity.save(update_fields=['label'])
        response, content_data = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        entity = content_data.get('entities')[0]
        self.assertIn(
            'label',
            entity.keys())
        self.assertEqual(
            entity.get('label'),
            label)


class DestroyValidationAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.validation = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_validation = RepositoryValidation.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, validation, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/api/v2/validation/{}/'.format(validation.id),
            **authorization_header)
        response = ListValidationViewSet.as_view(
            {'delete': 'destroy'})(request, pk=validation.id)
        return response

    def test_okay(self):
        response = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(
            self.private_validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        response = self.request(
            self.validation,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_private_forbidden(self):
        response = self.request(
            self.private_validation,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.validation.delete()

        response = self.request(
            self.validation,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListValidationsAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token('user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Repository 1',
            slug='repo',
            language=languages.LANGUAGE_EN)
        self.example_1 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        entity_1 = RepositoryValidationEntity.objects.create(
            repository_validation=self.example_1,
            start=0,
            end=0,
            entity='hi')
        entity_1.entity.set_label('greet')
        entity_1.entity.save()
        self.example_2 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        self.example_3 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='bye',
            intent='farewell')
        self.example_4 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='bye bye',
            intent='farewell')

        self.repository_2 = Repository.objects.create(
            owner=self.owner,
            name='Repository 2',
            slug='repo2',
            language=languages.LANGUAGE_EN)
        self.example_5 = RepositoryValidation.objects.create(
            repository_update=self.repository_2.current_update(),
            text='hi',
            intent='greet')
        self.example_6 = RepositoryValidation.objects.create(
            repository_update=self.repository_2.current_update(
                languages.LANGUAGE_PT),
            text='oi',
            intent='greet')
        self.translation_6 = RepositoryTranslatedValidation.objects.create(
            original_validation=self.example_6,
            language=languages.LANGUAGE_EN,
            text='hi')

    def request(self, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.get(
            '/api/v2/validations/',
            data,
            **authorization_header)

        response = ListValidationsViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            4)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_deleted(self):
        self.example_1.delete()
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            3)

    def test_without_repository_uuid(self):
        response, content_data = self.request()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_filter_text(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'text': self.example_1.text,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            self.example_1.id)

    def test_filter_part_text(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'search': 'h',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_filter_language(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'language': languages.LANGUAGE_PT
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_has_translation(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_translation': False
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_translation': True
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_has_not_translation_to(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_not_translation_to': languages.LANGUAGE_ES,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_not_translation_to': languages.LANGUAGE_EN,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_order_by_translation(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository_2.uuid,
                'order_by_translation': languages.LANGUAGE_EN,
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        results = content_data.get('results')
        self.assertEqual(
            0,
            len(results[0].get('translations')))
        self.assertEqual(
            1,
            len(results[1].get('translations')))

    def test_filter_order_by_translation_inverted(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository_2.uuid,
                'order_by_translation': '-{}'.format(languages.LANGUAGE_EN),
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        results = content_data.get('results')
        self.assertEqual(
            1,
            len(results[0].get('translations')))
        self.assertEqual(
            0,
            len(results[1].get('translations')))

    def test_filter_intent(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'intent': 'farewell',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_filter_label(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'label': 'greet',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_entity(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'entity': 'hi',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
