from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

from bothub.authentication.models import User

from .models import Repository
from .models import RepositoryExample
from .models import RepositoryExampleEntity
from .models import RepositoryTranslatedExample
from .models import RepositoryTranslatedExampleEntity
from .models import RepositoryAuthorization
from .models import RequestRepositoryAuthorization
from .models import RepositoryEntity
from .models import RepositoryEntityLabel
from . import languages
from .exceptions import RepositoryUpdateAlreadyStartedTraining
from .exceptions import RepositoryUpdateAlreadyTrained
from .exceptions import TrainingNotAllowed
from .exceptions import DoesNotHaveTranslation


class RepositoryUpdateTestCase(TestCase):
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

    def test_repository_current_update(self):
        update1 = self.repository.current_update('en')
        self.assertEqual(update1, self.repository.current_update('en'))
        update1.training_started_at = timezone.now()
        update1.save()
        self.assertNotEqual(update1, self.repository.current_update('en'))


class TranslateTestCase(TestCase):
    EXPECTED_RASA_NLU_DATA = {
        'text': 'meu nome é Douglas',
        'intent': 'greet',
        'entities': [],
    }

    EXPECTED_RASA_NLU_DATA_WITH_ENTITIES = {
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

        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=11,
            end=18,
            entity='name')

        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate,
            start=0,
            end=3,
            entity='my')

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
        self.owner = User.objects.create_user('owner@user.com', 'owner')
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
            list(settings.SUPPORTED_LANGUAGES.keys()))
        # TODO: Update test_languages_status test
        #       Create expeted result

    def test_last_trained_update(self):
        self.assertFalse(self.repository.last_trained_update())
        update_1 = self.repository.current_update()
        update_1.start_training(self.owner)
        update_2 = self.repository.current_update()
        update_2.start_training(self.owner)
        update_1.save_training(b'bot')
        self.assertEqual(
            update_1,
            self.repository.last_trained_update())
        update_2.train_fail()
        self.assertEqual(
            update_1,
            self.repository.last_trained_update())

    def test_available_languages(self):
        available_languages = self.repository.available_languages
        self.assertIn(languages.LANGUAGE_EN, available_languages)
        self.assertIn(languages.LANGUAGE_PT, available_languages)
        self.assertIn(languages.LANGUAGE_ES, available_languages)
        self.assertEqual(len(available_languages), 3)

    def test_intents(self):
        self.assertIn(
            'greet',
            self.repository.intents)

        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_PT),
            text='tchau',
            intent='bye')

        self.assertIn(
            'greet',
            self.repository.intents)
        self.assertIn(
            'bye',
            self.repository.intents)

        example.delete()

        self.assertNotIn(
            'bye',
            self.repository.intents)

    def test_entities(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='my name is Douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=11,
            end=18,
            entity='name')

        self.assertIn(
            'name',
            self.repository.entities.values_list('value', flat=True))

    def test_not_blank_value_in_intents(self):
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hi')

        self.assertNotIn(
            '',
            self.repository.intents)


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

    def test_delete(self):
        self.example.delete()
        self.assertEqual(
            self.example.deleted_in,
            self.repository.current_update())


class RepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'owner')
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

    def test_owner_ever_admin(self):
        authorization_owner = self.repository.get_user_authorization(
            self.owner)
        self.assertTrue(authorization_owner.is_admin)

    def test_role_user_can_read(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertTrue(authorization_user.can_read)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertTrue(authorization_user.can_read)

    def test_role_user_can_t_contribute(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertFalse(authorization_user.can_contribute)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertFalse(authorization_user.can_contribute)

    def test_role_contributor_can_contribute(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        authorization_user.save()
        self.assertTrue(authorization_user.can_contribute)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(
            self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        authorization_user.save()
        self.assertTrue(authorization_user.can_contribute)


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
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello1',
            intent='greet')
        example.delete()

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

    def test_examples_deleted_consistency(self):
        new_update_1 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_1,
            text='hello',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=new_update_1,
            text='hello d1',
            intent='greet').delete()
        examples_1_count = new_update_1.examples.count()
        new_update_1.start_training(self.owner)

        new_update_2 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_2,
            text='hellow',
            intent='greet')
        examples_2_count = new_update_2.examples.count()
        new_update_2.start_training(self.owner)

        new_update_3 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_3,
            text='hellow',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=new_update_3,
            text='hello d2',
            intent='greet').delete()
        RepositoryExample.objects.create(
            repository_update=new_update_3,
            text='hello d3',
            intent='greet').delete()
        RepositoryExample.objects.create(
            repository_update=new_update_3,
            text='hello d4',
            intent='greet').delete()
        examples_3_count = new_update_3.examples.count()
        new_update_3.start_training(self.owner)

        new_update_4 = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=new_update_4,
            text='hellow',
            intent='greet')
        examples_4_count = new_update_4.examples.count()
        new_update_4.start_training(self.owner)

        self.assertEqual(
            examples_1_count,
            new_update_1.examples.count())

        self.assertEqual(
            examples_2_count,
            new_update_2.examples.count())

        self.assertEqual(
            examples_3_count,
            new_update_3.examples.count())

        self.assertEqual(
            examples_4_count,
            new_update_4.examples.count())


class RepositoryReadyForTrain(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example_1 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        self.example_2 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        self.example_3 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='bye!',
            intent='bye')
        self.example_4 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='good bye',
            intent='bye')
        self.example_5 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hellow',
            intent='greet')

    def test_be_true(self):
        self.assertTrue(self.repository.ready_for_train)

    def test_be_false(self):
        self.repository.current_update().start_training(self.owner)
        self.assertFalse(self.repository.ready_for_train)

    def test_be_true_when_new_translate(self):
        self.repository.current_update().start_training(self.owner)
        RepositoryTranslatedExample.objects.create(
            original_example=self.example_1,
            language=languages.LANGUAGE_PT,
            text='oi')
        RepositoryTranslatedExample.objects.create(
            original_example=self.example_2,
            language=languages.LANGUAGE_PT,
            text='olá')
        self.repository.current_update()
        self.assertTrue(self.repository.ready_for_train)

    def test_be_true_when_deleted_example(self):
        self.repository.current_update()
        self.repository.current_update().start_training(self.owner)
        self.example_1.delete()
        self.assertTrue(self.repository.ready_for_train)

    def test_last_train_failed(self):
        current_update = self.repository.current_update()
        current_update.start_training(self.owner)
        current_update.train_fail()
        self.assertTrue(self.repository.current_update().ready_for_train)

    def test_change_algorithm(self):
        self.assertTrue(self.repository.ready_for_train)
        for (val_current, verb_current) in Repository.ALGORITHM_CHOICES:
            for (val_next, verb_next) in Repository.ALGORITHM_CHOICES:
                if val_current == val_next:
                    continue
                self.repository.algorithm = val_current
                self.repository.save()
                current_update = self.repository.current_update()
                current_update.start_training(self.owner)
                current_update.save_training(b'')
                self.assertFalse(self.repository.ready_for_train)
                self.repository.algorithm = val_next
                self.repository.save()
                self.assertTrue(self.repository.ready_for_train)


class RepositoryUpdateReadyForTrain(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN,
            algorithm=Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL)

    def test_be_true(self):
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        self.assertTrue(self.repository.current_update().ready_for_train)

    def test_be_false(self):
        self.assertFalse(self.repository.current_update().ready_for_train)

    def test_new_translate(self):
        example_1 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        example_2 = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        self.repository.current_update().start_training(self.owner)
        RepositoryTranslatedExample.objects.create(
            original_example=example_1,
            language=languages.LANGUAGE_PT,
            text='oi')
        RepositoryTranslatedExample.objects.create(
            original_example=example_2,
            language=languages.LANGUAGE_PT,
            text='olá')
        self.assertTrue(self.repository.current_update(
            languages.LANGUAGE_PT).ready_for_train)

    def test_when_deleted(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hellow',
            intent='greet')
        self.repository.current_update().start_training(self.owner)
        example.delete()
        self.assertTrue(self.repository.current_update().ready_for_train)

    def test_empty_intent(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='douglas',
            intent='')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='douglas',
            intent='')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=0,
            end=7,
            entity='name')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=0,
            end=7,
            entity='name')
        self.assertFalse(self.repository.current_update().ready_for_train)

    def test_intent_dont_have_min_examples(self):
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        self.assertFalse(self.repository.current_update().ready_for_train)

    def test_entity_dont_have_min_examples(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=0,
            end=2,
            entity='hi')
        self.assertFalse(self.repository.current_update().ready_for_train)
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=1,
            end=2,
            entity='hi')
        self.assertTrue(self.repository.current_update().ready_for_train)

    def test_settings_change_exists_requirements(self):
        self.repository.current_update().start_training(self.owner)
        self.repository.algorithm = Repository \
            .ALGORITHM_NEURAL_NETWORK_EXTERNAL
        self.repository.save()
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        self.assertEqual(
            len(self.repository.current_update().requirements_to_train),
            1)
        self.assertFalse(self.repository.current_update().ready_for_train)

    def test_no_examples(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        self.repository.current_update().start_training(self.owner)
        example.delete()
        self.assertFalse(self.repository.current_update().ready_for_train)


class RequestRepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'owner')
        repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.user = User.objects.create_user('user@user.com', 'user')
        self.ra = RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=repository,
            text='I can contribute')
        self.admin = User.objects.create_user('admin@user.com', 'admin')
        admin_authorization = repository.get_user_authorization(self.admin)
        admin_authorization.role = RepositoryAuthorization.ROLE_ADMIN
        admin_authorization.save()

    def test_approve(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        user_authorization = self.ra.repository.get_user_authorization(
            self.ra.user)
        self.assertEqual(
            user_authorization.role,
            RepositoryAuthorization.ROLE_USER)

    def test_approve_twice(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        with self.assertRaises(ValidationError):
            self.ra.approved_by = self.owner
            self.ra.save()

    def test_approve_twice_another_admin(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        with self.assertRaises(ValidationError):
            self.ra.approved_by = self.admin
            self.ra.save()


class RepositoryEntityTestCase(TestCase):
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
            text='my name is Douglas')

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=0,
            end=2,
            entity='object')

    def test_example_entity_create_entity(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')
        self.assertEqual(
            name_entity.pk,
            self.example_entity_1.entity.pk)

    def test_dont_duplicate_entity(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')

        new_example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')

        self.assertEqual(
            name_entity.pk,
            self.example_entity_1.entity.pk)
        self.assertEqual(
            name_entity.pk,
            new_example_entity.entity.pk)


class RepositoryEntityLabelTestCase(TestCase):
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
            text='my name is Douglas')

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=0,
            end=2,
            entity='object')

    def test_set_label(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')

        name_entity.set_label('subject')

        self.assertIsNotNone(name_entity.label)

    def test_entity_label_created(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')

        name_entity.set_label('subject')

        subject_label = RepositoryEntityLabel.objects.get(
            repository=self.repository,
            value='subject')

        self.assertEqual(
            name_entity.label.pk,
            subject_label.pk)

    def test_dont_duplicate_label(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')
        name_entity.set_label('subject')

        object_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='object')
        object_entity.set_label('subject')

        subject_label = RepositoryEntityLabel.objects.get(
            repository=self.repository,
            value='subject')

        self.assertEqual(
            name_entity.label.pk,
            subject_label.pk)
        self.assertEqual(
            object_entity.label.pk,
            subject_label.pk)

    def test_set_label_to_none(self):
        name_entity = RepositoryEntity.objects.get(
            repository=self.repository,
            value='name')

        name_entity.set_label(None)

        self.assertIsNone(name_entity.label)


class RepositoryOtherEntitiesTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas')

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='douglas')
        entity = self.example_entity_1.entity
        entity.set_label('name')
        entity.save()

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=0,
            end=2,
            entity='object')

    def test_ok(self):
        other_entities = self.repository.other_entities
        self.assertEqual(
            other_entities.count(),
            1)
        self.assertIn(self.example_entity_2.entity, other_entities)


class UseLanguageModelFeaturizerTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=self.language,
            algorithm=Repository.ALGORITHM_NEURAL_NETWORK_EXTERNAL)

        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is John',
            intent='greet')

    def test_equal_repository_value_after_train(self):
        current_update = self.repository.current_update()
        self.repository.algorithm = Repository \
            .ALGORITHM_NEURAL_NETWORK_INTERNAL
        self.repository.save()
        current_update.start_training(self.owner)
        current_update.save_training(b'')
        self.assertFalse(current_update.use_language_model_featurizer)


class UseCompetingIntentsTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=self.language,
            use_competing_intents=True)

        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is John',
            intent='greet')

    def test_change_ready_for_train(self):
        self.assertTrue(self.repository.ready_for_train)
        current_update = self.repository.current_update()
        current_update.start_training(self.owner)
        current_update.save_training(b'')
        self.assertFalse(self.repository.ready_for_train)
        self.repository.use_competing_intents = False
        self.repository.save()
        self.assertTrue(self.repository.ready_for_train)
        self.repository.use_competing_intents = True
        self.repository.save()
        self.assertFalse(self.repository.ready_for_train)

    def test_equal_repository_value_after_train(self):
        current_update = self.repository.current_update()
        self.repository.use_competing_intents = False
        self.repository.save()
        current_update.start_training(self.owner)
        current_update.save_training(b'')
        self.assertFalse(current_update.use_competing_intents)


class UseNameEntitiesTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=self.language,
            use_name_entities=True)

        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is John',
            intent='greet')

    def test_change_ready_for_train(self):
        self.assertTrue(self.repository.ready_for_train)
        current_update = self.repository.current_update()
        current_update.start_training(self.owner)
        current_update.save_training(b'')
        self.assertFalse(self.repository.ready_for_train)
        self.repository.use_name_entities = False
        self.repository.save()
        self.assertTrue(self.repository.ready_for_train)
        self.repository.use_name_entities = True
        self.repository.save()
        self.assertFalse(self.repository.ready_for_train)

    def test_equal_repository_value_after_train(self):
        current_update = self.repository.current_update()
        self.repository.use_name_entities = False
        self.repository.save()
        current_update.start_training(self.owner)
        current_update.save_training(b'')
        self.assertFalse(current_update.use_name_entities)


class RepositoryUpdateWarnings(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user('owner@user.com', 'user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Test',
            slug='test',
            language=self.language,
            use_competing_intents=True)

        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is Douglas',
            intent='greet')

    def test_min_intents(self):
        self.assertEqual(
            len(self.repository.current_update().warnings),
            1)
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='bye',
            intent='bye')
        self.assertEqual(
            len(self.repository.current_update().warnings),
            0)


class RepositorySupportedLanguageQueryTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner@user.com', 'user')
        self.uid = 0

    def _create_repository(self, language):
        self.uid += 1
        return Repository.objects.create(
            owner=self.owner,
            name='Test {}'.format(language),
            slug='test-{}-{}'.format(self.uid, language),
            language=language)

    def test_main_language(self):
        language = languages.LANGUAGE_EN
        repository_en = self._create_repository(language)
        q = Repository.objects.all().supported_language(language)
        self.assertEqual(
            q.count(),
            1,
        )
        self.assertIn(repository_en, q)
        q = Repository.objects.all().supported_language(language)
        repository_pt = self._create_repository(languages.LANGUAGE_PT)
        self.assertEqual(
            q.count(),
            1,
        )
        self.assertNotIn(repository_pt, q)

    def test_has_translation(self):
        language = languages.LANGUAGE_EN
        t_language = languages.LANGUAGE_PT
        repository_en = self._create_repository(language)
        example = RepositoryExample.objects.create(
            repository_update=repository_en.current_update(),
            text='bye',
            intent='bye')
        RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=t_language,
            text='tchau')
        q = Repository.objects.all().supported_language(t_language)
        self.assertEqual(
            q.count(),
            1,
        )
        self.assertIn(repository_en, q)

    def test_has_example(self):
        language = languages.LANGUAGE_EN
        e_language = languages.LANGUAGE_PT
        repository_en = self._create_repository(language)
        example = RepositoryExample.objects.create(
            repository_update=repository_en.current_update(e_language),
            text='bye',
            intent='bye')
        q = Repository.objects.all().supported_language(e_language)
        self.assertEqual(
            q.count(),
            1,
        )
        self.assertIn(repository_en, q)
        example.delete()
        q = Repository.objects.all().supported_language(e_language)
        self.assertEqual(
            q.count(),
            0,
        )
