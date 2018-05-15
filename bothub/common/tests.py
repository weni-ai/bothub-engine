from django.test import TestCase
from django.utils import timezone

from bothub.authentication.models import User
from .models import Repository
from .models import RepositoryExample
from .models import RepositoryExampleEntity
from .models import RepositoryTranslatedExample
from .models import RepositoryTranslatedExampleEntity
from .models import RepositoryAuthorization
from .models import DoesNotHaveTranslation
from . import languages
from .exceptions import RepositoryUpdateAlreadyStartedTraining
from .exceptions import RepositoryUpdateAlreadyTrained
from .exceptions import TrainingNotAllowed


class RepositoryUpdateTestCase(TestCase):
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
            RepositoryUpdateTestCase.EXPECTED_RASA_NLU_DATA)

    def test_repository_current_update(self):
        update1 = self.repository.current_update('en')
        self.assertEqual(update1, self.repository.current_update('en'))
        update1.training_started_at = timezone.now()
        update1.save()
        self.assertNotEqual(update1, self.repository.current_update('en'))


class TranslateTestCase(TestCase):
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

    def test_to_rasa_nlu_data(self):
        language = languages.LANGUAGE_PT
        RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text='meu nome é Douglas')

        self.assertDictEqual(
            self.repository.current_update(
                languages.LANGUAGE_PT).rasa_nlu_data,
            TranslateTestCase.EXPECTED_RASA_NLU_DATA)

    def test_translated_entity(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
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
        self.assertDictEqual(
            self.repository.current_update(
                languages.LANGUAGE_PT).rasa_nlu_data,
            TranslateTestCase.EXPECTED_RASA_NLU_DATA_WITH_ENTITIES)

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

    def test_invalid_many_how_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=12,
            end=19,
            entity='name')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=19,
            entity='name')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=12,
            entity='space')

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
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=10,
            end=11,
            entity='space')
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=10,
            end=11,
            entity='space')

        self.assertEqual(
            translate.has_valid_entities,
            False)

    def test_does_not_have_translation(self):
        with self.assertRaises(DoesNotHaveTranslation):
            self.example.get_translation(languages.LANGUAGE_NL)


class RepositoryTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')
        self.user = User.objects.create_user('fake@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='private',
            is_private=True)

        example_1 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hi',
            intent='greet')
        RepositoryTranslatedExample.objects.create(
            original_example=example_1,
            language=languages.LANGUAGE_PT,
            text='oi')
        RepositoryTranslatedExample.objects.create(
            original_example=example_1,
            language=languages.LANGUAGE_ES,
            text='hola')

        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_PT),
            text='olá',
            intent='greet')

    def test_languages_status(self):
        languages_status = self.repository.languages_status
        self.assertListEqual(
            list(languages_status.keys()),
            languages.SUPPORTED_LANGUAGES)
        # TODO: Update test_languages_status test
        #       Create expeted result

    def test_current_rasa_nlu_data(self):
        current_rasa_nlu_data = self.repository.current_rasa_nlu_data()
        self.assertListEqual(
            list(current_rasa_nlu_data.keys()),
            ['common_examples'])
        # TODO: Update test_current_rasa_nlu_data test
        #       Create expeted result

    def test_last_trained_update(self):
        self.assertFalse(self.repository.last_trained_update())
        # TODO: Update last_trained_update test

    def test_available_languages(self):
        available_languages = self.repository.available_languages
        self.assertIn(languages.LANGUAGE_EN, available_languages)
        self.assertIn(languages.LANGUAGE_PT, available_languages)
        self.assertIn(languages.LANGUAGE_ES, available_languages)
        self.assertEqual(len(available_languages), 3)


class RepositoryExampleTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=self.language)

        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')

    def test_language(self):
        self.assertEqual(
            self.example.language,
            self.example.repository_update.language)
        self.assertEqual(
            self.example.language,
            self.language)

    def teste_delete(self):
        self.example.delete()
        self.assertEqual(
            self.example.deleted_in,
            self.repository.current_update())


class RepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')
        self.user = User.objects.create_user('fake@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test')
        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='private',
            is_private=True)

    def test_admin_level(self):
        authorization = self.repository.get_user_authorization(self.owner)
        self.assertEqual(
            authorization.level,
            RepositoryAuthorization.LEVEL_ADMIN)

    def test_read_level(self):
        authorization = self.repository.get_user_authorization(self.user)
        self.assertEqual(
            authorization.level,
            RepositoryAuthorization.LEVEL_READER)

    def test_nothing_level(self):
        authorization = self.private_repository.get_user_authorization(
            self.user)
        self.assertEqual(
            authorization.level,
            RepositoryAuthorization.LEVEL_NOTHING)

    def test_can_read(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(
            self.owner)
        self.assertTrue(authorization_owner.can_read)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        self.assertTrue(authorization_user.can_read)
        # private repository owner
        private_authorization_owner = self.private_repository \
            .get_user_authorization(self.owner)
        self.assertTrue(private_authorization_owner.can_read)
        # secondary user in private repository
        private_authorization_user = self.private_repository \
            .get_user_authorization(self.user)
        self.assertFalse(private_authorization_user.can_read)

    def test_can_contribute(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(
            self.owner)
        self.assertTrue(authorization_owner.can_contribute)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        self.assertFalse(authorization_user.can_contribute)
        # private repository owner
        private_authorization_owner = self.private_repository \
            .get_user_authorization(self.owner)
        self.assertTrue(private_authorization_owner.can_contribute)
        # secondary user in private repository
        private_authorization_user = self.private_repository \
            .get_user_authorization(self.user)
        self.assertFalse(private_authorization_user.can_contribute)

    def test_can_write(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(
            self.owner)
        self.assertTrue(authorization_owner.can_write)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        self.assertFalse(authorization_user.can_write)
        # private repository owner
        private_authorization_owner = self.private_repository \
            .get_user_authorization(self.owner)
        self.assertTrue(private_authorization_owner.can_write)
        # secondary user in private repository
        private_authorization_user = self.private_repository \
            .get_user_authorization(self.user)
        self.assertFalse(private_authorization_user.can_write)

    def test_is_admin(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(
            self.owner)
        self.assertTrue(authorization_owner.is_admin)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        self.assertFalse(authorization_user.is_admin)
        # private repository owner
        private_authorization_owner = self.private_repository \
            .get_user_authorization(self.owner)
        self.assertTrue(private_authorization_owner.is_admin)
        # secondary user in private repository
        private_authorization_user = self.private_repository \
            .get_user_authorization(self.user)
        self.assertFalse(private_authorization_user.is_admin)


class RepositoryUpdateTrainingTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)

    def test_train(self):
        update = self.repository.current_update()
        update.start_training(self.owner)

        bot_data = b'bot_data__()\\\\//?(*)'

        update.save_training(bot_data)
        self.assertEqual(
            update.get_bot_data(),
            bot_data)

    def test_already_started_trained(self):
        update = self.repository.current_update()
        update.start_training(self.owner)
        with self.assertRaises(RepositoryUpdateAlreadyStartedTraining):
            update.start_training(self.owner)

    def test_already_trained(self):
        update = self.repository.current_update()
        update.start_training(self.owner)
        update.save_training(b'')

        with self.assertRaises(RepositoryUpdateAlreadyTrained):
            update.start_training(self.owner)

        with self.assertRaises(RepositoryUpdateAlreadyTrained):
            update.save_training(self.owner)

    def test_training_not_allowed(self):
        user = User.objects.create_user('fake@user.com', 'fake')

        update = self.repository.current_update()
        with self.assertRaises(TrainingNotAllowed):
            update.start_training(user)


class RepositoryUpdateExamplesTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')

        self.update = self.repository.current_update()
        self.update.start_training(self.owner)
        self.update.save_training(b'')

    def test_okay(self):
        new_update_1 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_1,
            text='hello',
            intent='greet')
        new_update_1.start_training(self.owner)

        new_update_2 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_2,
            text='good morning',
            intent='greet')

        self.assertEqual(
            self.update.examples.count(),
            1)
        self.assertEqual(
            new_update_1.examples.count(),
            2)
        self.assertEqual(
            new_update_2.examples.count(),
            3)
