from django.test import TestCase
from django.utils import timezone

from bothub.authentication.models import User
from .models import Repository
from .models import RepositoryExample
from .models import RepositoryExampleEntity
from .models import RepositoryTranslatedExample
from .models import RepositoryTranslatedExampleEntity
from . import languages


class RepositoryUpdateTest(TestCase):
    EXPECTED_RASA_NLU_DATA = {
        'common_examples': [
            {
                'text': 'my name is Douglas',
                'intent': '',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'value': 'Douglas',
                        'entity': 'name',
                    },
                ],
            }
        ],
    }

    def setUp(self):
        owner = User.objects.create_user('fake@user.com', 'user', '123456')
        self.repository = Repository.objects.create(
            owner=owner,
            slug='test')
        self.repository_update = self.repository.current_update('en')
        example = RepositoryExample.objects.create(
            repository_update=self.repository_update,
            text='my name is Douglas')
        self.entity = RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=11,
            end=18,
            entity='name')

    def test_repository_example_entity(self):
        self.assertEqual(self.entity.value, 'Douglas')

    def test_get_rasa_nlu_data(self):
        self.assertDictEqual(
            self.repository_update.rasa_nlu_data,
            RepositoryUpdateTest.EXPECTED_RASA_NLU_DATA)

    def test_repository_current_update(self):
        update1 = self.repository.current_update('en')
        self.assertEqual(update1, self.repository.current_update('en'))
        update1.training_started_at = timezone.now()
        update1.save()
        self.assertNotEqual(update1, self.repository.current_update('en'))


class TranslateTest(TestCase):
    EXPECTED_RASA_NLU_DATA = {
        'common_examples': [
            {
                'text': 'meu nome é Douglas',
                'intent': 'greet',
                'entities': [],
            },
        ],
    }

    EXPECTED_RASA_NLU_DATA_WITH_ENTITIES = {
        'common_examples': [
            {
                'text': 'meu nome é Douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'value': 'Douglas',
                        'entity': 'name',
                    }
                ],
            },
        ],
    }

    def setUp(self):
        owner = User.objects.create_user('fake@user.com', 'user', '123456')
        self.repository = Repository.objects.create(
            owner=owner,
            slug='test',
            language=languages.LANGUAGE_EN)
        self.repository_update = self.repository.current_update('en')
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository_update,
            text='my name is Douglas',
            intent='greet')

    def test_new_translate(self):
        language = languages.LANGUAGE_PT
        RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')
        self.assertEqual(
            len(self.repository.current_update(language).examples),
            1)

    def test_to_rsa_nlu_data(self):
        language = languages.LANGUAGE_PT
        RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')

        self.assertDictEqual(
            self.repository.current_update(
                languages.LANGUAGE_PT).rasa_nlu_data,
            TranslateTest.EXPECTED_RASA_NLU_DATA)

    def test_translated_entity(self):
        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=11,
            end=18,
            entity='name')
        self.assertDictEqual(
            self.repository.current_update(
                languages.LANGUAGE_PT).rasa_nlu_data,
            TranslateTest.EXPECTED_RASA_NLU_DATA_WITH_ENTITIES)

    def test_valid_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=12,
            end=19,
            entity='name')

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=11,
            end=18,
            entity='name')

        self.assertEqual(
            translate.has_valid_entities,
            True)

    def test_invalid_count_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=12,
            end=19,
            entity='name')

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')

        self.assertEqual(
            translate.has_valid_entities,
            False)

    def test_invalid_how_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=12,
            end=19,
            entity='name')

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=11,
            end=18,
            entity='nome')

        self.assertEqual(
            translate.has_valid_entities,
            False)
