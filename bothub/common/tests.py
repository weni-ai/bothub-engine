import requests_mock
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from bothub.authentication.models import User
from . import languages
from .exceptions import DoesNotHaveTranslation
from .exceptions import TrainingNotAllowed
from .models import (
    Repository,
    RepositoryIntent,
    RepositoryEvaluate,
    RepositoryQueueTask,
    QAKnowledgeBase,
    QAtext,
    Organization,
    OrganizationAuthorization
)
from .models import RepositoryAuthorization
from .models import RepositoryEntity
from .models import RepositoryEntityGroup
from .models import RepositoryExample
from .models import RepositoryExampleEntity
from .models import RepositoryTranslatedExample
from .models import RepositoryTranslatedExampleEntity
from .models import RequestRepositoryAuthorization


class RepositoryVersionTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create_user("fake@user.com", "user", "123456")
        self.repository = Repository.objects.create(owner=owner, slug="test")
        self.repository_update = self.repository.current_version("en")
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias", repository_version=self.repository_update.repository_version
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository_update,
            text="my name is User",
            intent=self.example_intent_1,
        )
        self.entity = RepositoryExampleEntity.objects.create(
            repository_example=example, start=11, end=18, entity="name"
        )

    def test_repository_example_entity(self):
        self.assertEqual(self.entity.value, "User")

    def test_repository_current_version(self):
        update1 = self.repository.current_version("en")
        self.assertEqual(update1, self.repository.current_version("en"))
        update1.training_started_at = timezone.now()
        update1.save()
        self.assertEqual(update1, self.repository.current_version("en"))


class TranslateTestCase(TestCase):
    EXPECTED_RASA_NLU_DATA = {
        "text": "meu nome é User",
        "intent": "greet",
        "entities": [],
    }

    EXPECTED_RASA_NLU_DATA_WITH_ENTITIES = {
        "text": "meu nome é User",
        "intent": "greet",
        "entities": [{"start": 11, "end": 18, "value": "User", "entity": "name"}],
    }

    def setUp(self):
        owner = User.objects.create_user("fake@user.com", "user", "123456")
        self.repository = Repository.objects.create(
            owner=owner, slug="test", language=languages.LANGUAGE_EN
        )
        self.repository_update = self.repository.current_version("en")
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_update.repository_version
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository_update,
            text="my name is User",
            intent=self.example_intent_1,
        )

    def test_new_translate(self):
        language = languages.LANGUAGE_PT
        RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )
        self.assertEqual(len(self.repository.current_version(language).examples), 1)

    def test_translated_entity(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="name"
        )

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=11, end=18, entity="name"
        )

    def test_valid_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=12, end=19, entity="name"
        )

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=11, end=18, entity="name"
        )

        self.assertEqual(translate.has_valid_entities, True)

    def test_invalid_count_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=12, end=19, entity="name"
        )

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )

        self.assertEqual(translate.has_valid_entities, False)

        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=11, end=18, entity="name"
        )

        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=0, end=3, entity="my"
        )

        self.assertEqual(translate.has_valid_entities, False)

    def test_invalid_how_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=12, end=19, entity="name"
        )

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=11, end=18, entity="nome"
        )

        self.assertEqual(translate.has_valid_entities, False)

    def test_invalid_many_how_entities(self):
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=12, end=19, entity="name"
        )
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=19, entity="name"
        )
        RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=12, entity="space"
        )

        language = languages.LANGUAGE_PT
        translate = RepositoryTranslatedExample.objects.create(
            original_example=self.example, language=language, text="meu nome é User"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=11, end=18, entity="name"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=10, end=11, entity="space"
        )
        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=translate, start=10, end=11, entity="space"
        )

        self.assertEqual(translate.has_valid_entities, False)

    def test_does_not_have_translation(self):
        with self.assertRaises(DoesNotHaveTranslation):
            self.example.get_translation(languages.LANGUAGE_NL)


class RepositoryTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "owner")
        self.user = User.objects.create_user("fake@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = self.repository.current_version().repository_version

        self.private_repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="private",
            is_private=True,
        )

        self.repository_version_private = (
            self.private_repository.current_version().repository_version
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_version
        )

        example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_EN
            ),
            text="hi",
            intent=self.example_intent_1,
        )
        RepositoryTranslatedExample.objects.create(
            original_example=example_1, language=languages.LANGUAGE_PT, text="oi"
        )
        RepositoryTranslatedExample.objects.create(
            original_example=example_1, language=languages.LANGUAGE_ES, text="hola"
        )

        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_PT
            ),
            text="olá",
            intent=self.example_intent_1,
        )

        self.evaluate_test_phrase = RepositoryEvaluate.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_EN
            ),
            intent=self.example_intent_1,
            text="test",
        )

    def test_languages_status(self):
        languages_status = self.repository.languages_status
        self.assertListEqual(
            list(languages_status.keys()), list(settings.SUPPORTED_LANGUAGES.keys())
        )
        # TODO: Update test_languages_status test
        #       Create expeted result

    def test_last_trained_update(self):
        self.assertFalse(self.repository.last_trained_update())
        update_1 = self.repository.current_version()
        update_1.start_training(self.owner)
        update_2 = self.repository.current_version()
        update_2.start_training(self.owner)
        update_1.save_training(b"bot", settings.BOTHUB_NLP_RASA_VERSION)
        self.assertEqual(update_1, self.repository.last_trained_update())
        update_2.train_fail()
        self.assertEqual(update_1, self.repository.last_trained_update())
        self.assertEqual(update_1.total_training_end, 1)

    def test_available_languages(self):
        available_languages = self.repository.available_languages()
        self.assertIn(languages.LANGUAGE_EN, available_languages)
        self.assertIn(languages.LANGUAGE_PT, available_languages)
        self.assertIn(languages.LANGUAGE_ES, available_languages)
        self.assertEqual(len(available_languages), 3)

    def test_specific_verson_id(self):
        version = self.repository.current_version(language=languages.LANGUAGE_PT)
        specific_version = self.repository.get_specific_version_id(
            repository_version=version.repository_version.pk,
            language=languages.LANGUAGE_PT,
        )
        self.assertEqual(version.language, specific_version.language)
        self.assertEqual(
            version.repository_version, specific_version.repository_version
        )
        self.assertEqual(
            version.repository_version.repository,
            specific_version.repository_version.repository,
        )

    def test_intents(self):
        self.assertIn("greet", self.repository.intents())

        example_intent_1 = RepositoryIntent.objects.create(
            text="bye",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_PT
            ),
            text="tchau",
            intent=example_intent_1,
        )

        self.assertIn("greet", self.repository.intents())
        self.assertIn("bye", self.repository.intents())

        example.delete()

        self.assertNotIn("bye", self.repository.intents())

    def test_entities(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_EN
            ),
            text="my name is User",
            intent=example_intent_1,
        )
        RepositoryExampleEntity.objects.create(
            repository_example=example, start=11, end=18, entity="name"
        )

        self.assertIn(
            "name", self.repository_version.entities.values_list("value", flat=True)
        )

    def test_not_blank_value_in_intents(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_EN
            ),
            text="hi",
            intent=example_intent_1,
        )

        self.assertNotIn("", self.repository.intents())

    def test_have_at_least_one_test_phrase_registered(self):
        self.assertFalse(
            self.repository.have_at_least_one_test_phrase_registered(
                language=languages.LANGUAGE_PT_BR
            )
        )
        self.assertTrue(
            self.repository.have_at_least_one_test_phrase_registered(
                language=languages.LANGUAGE_EN
            )
        )

    def test_have_at_least_two_intents_registered(self):
        self.assertFalse(self.repository.have_at_least_two_intents_registered())
        intent_test = RepositoryIntent.objects.create(
            text="farewall", repository_version=self.repository_version
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_PT
            ),
            text="test",
            intent=intent_test,
        )
        self.assertTrue(self.repository.have_at_least_two_intents_registered())

    def test_have_at_least_twenty_examples_for_each_intent(self):
        self.assertFalse(
            self.repository.have_at_least_twenty_examples_for_each_intent(
                language=languages.LANGUAGE_EN
            )
        )
        for i in range(0, 20):
            RepositoryExample.objects.create(
                repository_version_language=self.repository.current_version(
                    languages.LANGUAGE_EN
                ),
                text=f"test{i}",
                intent=self.example_intent_1,
            )
        self.assertTrue(
            self.repository.have_at_least_twenty_examples_for_each_intent(
                language=languages.LANGUAGE_EN
            )
        )

    def test_validate_if_can_run_manual_evaluate(self):
        with self.assertRaises(ValidationError):
            self.repository.validate_if_can_run_manual_evaluate(
                language=languages.LANGUAGE_EN
            )

    def test_validate_if_can_run_automatic_evaluate(self):
        with self.assertRaises(ValidationError):
            self.repository.validate_if_can_run_automatic_evaluate(
                language=languages.LANGUAGE_EN
            )

    @requests_mock.Mocker()
    def test_request_nlp_manual_evaluate(self, request_mock):
        intent_test = RepositoryIntent.objects.create(
            text="farewall", repository_version=self.repository_version
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(
                languages.LANGUAGE_PT
            ),
            text="test",
            intent=intent_test,
        )

        url = f"{self.repository.nlp_server if self.repository.nlp_server else settings.BOTHUB_NLP_BASE_URL}"
        url = f"{url}v2/evaluate/"
        json = {
            "language": languages.LANGUAGE_EN,
            "status": RepositoryQueueTask.STATUS_PROCESSING,
            "repository_version": self.repository_version.pk,
            "evaluate_id": None,
            "evaluate_version": None,
            "cross_validation": False,
        }
        request_mock.post(url=url, json=json)

        response = self.repository.request_nlp_manual_evaluate(
            user_authorization=self.repository.get_user_authorization(self.owner),
            data={
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
            },
        )
        self.assertEqual(json, response.json())

    @requests_mock.Mocker()
    def test_request_nlp_automatic_evaluate(self, request_mock):
        intent_test = RepositoryIntent.objects.create(
            text="farewall", repository_version=self.repository_version
        )
        for i in range(0, 20):
            RepositoryExample.objects.create(
                repository_version_language=self.repository.current_version(
                    languages.LANGUAGE_EN
                ),
                text=f"test{i}",
                intent=intent_test,
            )
        for i in range(0, 20):
            RepositoryExample.objects.create(
                repository_version_language=self.repository.current_version(
                    languages.LANGUAGE_EN
                ),
                text=f"test{i}",
                intent=self.example_intent_1,
            )
        url = f"{self.repository.nlp_server if self.repository.nlp_server else settings.BOTHUB_NLP_BASE_URL}"
        url = f"{url}v2/evaluate/"
        json = {
            "language": languages.LANGUAGE_EN,
            "status": RepositoryQueueTask.STATUS_PROCESSING,
            "repository_version": self.repository_version.pk,
            "evaluate_id": None,
            "evaluate_version": None,
            "cross_validation": True,
        }
        request_mock.post(url=url, json=json)

        response = self.repository.request_nlp_automatic_evaluate(
            user_authorization=self.repository.get_user_authorization(self.owner),
            data={
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
            },
        )
        self.assertEqual(json, response.json())

    @requests_mock.Mocker()
    def test_request_nlp_qa(self, request_mock):
        qa_knowledge_base = QAKnowledgeBase.objects.create(
            repository=self.repository, title="teste"
        )
        qa_context = QAtext.objects.create(
            knowledge_base=qa_knowledge_base,
            text="texto teste",
            language=languages.LANGUAGE_PT_BR,
        )
        url = f"{self.repository.nlp_server if self.repository.nlp_server else settings.BOTHUB_NLP_BASE_URL}"
        url = f"{url}v2/question-answering/"
        json = {
            "answers": [
                {"text": "teste 1", "confidence": "0.8423367973327138"},
                {"text": "teste 2", "confidence": "0.07927308637792603"},
            ]
        }
        request_mock.post(url=url, json=json)

        response = self.repository.request_nlp_qa(
            user_authorization=self.repository.get_user_authorization(self.owner),
            data={
                "knowledge_base_id": qa_knowledge_base.pk,
                "question": "question teste?",
                "language": qa_context.language,
            },
        )
        self.assertEqual(json, response.json())


class RepositoryExampleTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

    def test_language(self):
        self.assertEqual(
            self.example.language, self.example.repository_version_language.language
        )
        self.assertEqual(self.example.language, self.language)


class RepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "owner")
        self.user = User.objects.create_user("fake@user.com", "user")
        self.collaborator = User.objects.create_user("colaborator@user.com", "collaborator")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner, name="Test", slug="test"
        )
        self.private_repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="private",
            is_private=True,
        )
        self.organization = Organization.objects.create(name="Weni")
        self.organization_repository = Repository.objects.create(
            owner=self.organization, 
            name="Organization Repository", 
            slug="organization_repository"
        )

    def test_admin_level(self):
        authorization = self.repository.get_user_authorization(self.owner)
        self.assertEqual(authorization.level, RepositoryAuthorization.LEVEL_ADMIN)

    def test_read_level(self):
        authorization = self.repository.get_user_authorization(self.user)
        self.assertEqual(authorization.level, RepositoryAuthorization.LEVEL_READER)

    def test_nothing_level(self):
        authorization = self.private_repository.get_user_authorization(self.user)
        self.assertEqual(authorization.level, RepositoryAuthorization.LEVEL_NOTHING)

    def test_can_read(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(self.owner)
        self.assertTrue(authorization_owner.can_read)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        self.assertTrue(authorization_user.can_read)
        # private repository owner
        private_authorization_owner = self.private_repository.get_user_authorization(
            self.owner
        )
        self.assertTrue(private_authorization_owner.can_read)
        # secondary user in private repository
        private_authorization_user = self.private_repository.get_user_authorization(
            self.user
        )
        self.assertFalse(private_authorization_user.can_read)

    def test_can_contribute(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(self.owner)
        self.assertTrue(authorization_owner.can_contribute)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        self.assertFalse(authorization_user.can_contribute)
        # private repository owner
        private_authorization_owner = self.private_repository.get_user_authorization(
            self.owner
        )
        self.assertTrue(private_authorization_owner.can_contribute)
        # secondary user in private repository
        private_authorization_user = self.private_repository.get_user_authorization(
            self.user
        )
        self.assertFalse(private_authorization_user.can_contribute)

    def test_can_write(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(self.owner)
        self.assertTrue(authorization_owner.can_write)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        self.assertFalse(authorization_user.can_write)
        # private repository owner
        private_authorization_owner = self.private_repository.get_user_authorization(
            self.owner
        )
        self.assertTrue(private_authorization_owner.can_write)
        # secondary user in private repository
        private_authorization_user = self.private_repository.get_user_authorization(
            self.user
        )
        self.assertFalse(private_authorization_user.can_write)

    def test_is_admin(self):
        # repository owner
        authorization_owner = self.repository.get_user_authorization(self.owner)
        self.assertTrue(authorization_owner.is_admin)
        # secondary user in public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        self.assertFalse(authorization_user.is_admin)
        # private repository owner
        private_authorization_owner = self.private_repository.get_user_authorization(
            self.owner
        )
        self.assertTrue(private_authorization_owner.is_admin)
        # secondary user in private repository
        private_authorization_user = self.private_repository.get_user_authorization(
            self.user
        )
        self.assertFalse(private_authorization_user.is_admin)

    def test_owner_ever_admin(self):
        authorization_owner = self.repository.get_user_authorization(self.owner)
        self.assertTrue(authorization_owner.is_admin)

    def test_role_user_can_read(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertTrue(authorization_user.can_read)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertTrue(authorization_user.can_read)

    def test_role_user_can_t_contribute(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertFalse(authorization_user.can_contribute)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_USER
        authorization_user.save()
        self.assertFalse(authorization_user.can_contribute)

    def test_role_contributor_can_contribute(self):
        # public repository
        authorization_user = self.repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        authorization_user.save()
        self.assertTrue(authorization_user.can_contribute)

        # private repository
        authorization_user = self.private_repository.get_user_authorization(self.user)
        authorization_user.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        authorization_user.save()
        self.assertTrue(authorization_user.can_contribute)

    def test_organization_auth_over_repository_auth(self):
        """ 
        Tests that a User's authorization role is of the highest level possible in a Repository, 
        either using the RepositoryAuthorization or the OrganizationAuthorization.
        The expected behavior is that the organization's authorization role should be passed to the repository's authorization for that user.
        """

        # The role that the user should inherit from the organization authorization inside the repository.
        initial_organization_role = OrganizationAuthorization.ROLE_ADMIN

        # Set user's role to a low level at the Repository
        collaborator_repository_auth, created = RepositoryAuthorization.objects.get_or_create(
            user=self.collaborator, repository=self.organization_repository, role=RepositoryAuthorization.ROLE_USER
        )
        # Set user's role to a high level at the Organization
        collaborator_organization_auth = self.organization.organization_authorizations.create(
            user=self.collaborator, role=initial_organization_role
        )
        
        # Validate that their access level corresponds to their role in the Organization and not the Repository, as it is higher at this point.
        user_authorization = self.organization_repository.get_user_authorization(self.collaborator)
        self.assertEqual(user_authorization.role, collaborator_organization_auth.role)

        # Lower their level inside the Organization
        collaborator_organization_auth.role = OrganizationAuthorization.ROLE_NOT_SETTED
        collaborator_organization_auth.save()
        
        # Validate that the repository authorization level was updated.
        collaborator_repository_auth.refresh_from_db()
        self.assertEqual(collaborator_repository_auth.role, initial_organization_role)

        # Validate that the user's level is now the Repository's and not the Organization's, as it is higher.
        user_authorization = self.organization_repository.get_user_authorization(self.collaborator)
        self.assertEqual(user_authorization.role, collaborator_repository_auth.role)

        ## Verify that org auth with (role >= 4) will not update the repository's authorization
        
        # Set user's role to ROLE_TRANSLATE level at the Organization
        collaborator_organization_auth.role = OrganizationAuthorization.ROLE_TRANSLATE
        collaborator_organization_auth.save()
        
        user_authorization = self.organization_repository.get_user_authorization(self.collaborator)
        self.assertEqual(user_authorization.role, collaborator_repository_auth.role)


class RepositoryVersionTrainingTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def test_train(self):
        update = self.repository.current_version()
        update.start_training(self.owner)

        bot_data = "https://s3.amazonaws.com"

        update.save_training(bot_data, settings.BOTHUB_NLP_RASA_VERSION)
        self.assertEqual(update.get_bot_data.bot_data, bot_data)

    def test_training_not_allowed(self):
        user = User.objects.create_user("fake@user.com", "fake")

        update = self.repository.current_version()
        with self.assertRaises(TrainingNotAllowed):
            update.start_training(user)


class RepositoryVersionExamplesTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello1",
            intent=self.example_intent_1,
        )
        example.delete()

        self.update = self.repository.current_version()
        self.update.start_training(self.owner)
        self.update.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)

    def test_okay(self):
        new_update_1 = self.repository.current_version()
        RepositoryExample.objects.create(
            repository_version_language=new_update_1,
            text="hello",
            intent=self.example_intent_1,
        )
        new_update_1.start_training(self.owner)

        new_update_2 = self.repository.current_version()
        RepositoryExample.objects.create(
            repository_version_language=new_update_2,
            text="good morning",
            intent=self.example_intent_1,
        )
        self.assertEqual(self.update.examples.count(), 3)
        self.assertEqual(new_update_1.examples.count(), 3)
        self.assertEqual(new_update_2.examples.count(), 3)


class RepositoryReadyForTrain(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example_intent_2 = RepositoryIntent.objects.create(
            text="bye",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )
        self.example_2 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello",
            intent=self.example_intent_1,
        )
        self.example_3 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="bye!",
            intent=self.example_intent_2,
        )
        self.example_4 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="good bye",
            intent=self.example_intent_2,
        )
        self.example_5 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hellow",
            intent=self.example_intent_1,
        )

    def test_be_true(self):
        self.assertTrue(self.repository.ready_for_train())

    # def test_be_false(self):
    #     self.repository.current_version().start_training(self.owner)
    #     self.assertFalse(self.repository.ready_for_train())

    def test_be_true_when_new_translate(self):
        self.repository.current_version().start_training(self.owner)
        RepositoryTranslatedExample.objects.create(
            original_example=self.example_1, language=languages.LANGUAGE_PT, text="oi"
        )
        RepositoryTranslatedExample.objects.create(
            original_example=self.example_2, language=languages.LANGUAGE_PT, text="olá"
        )
        self.repository.current_version()
        self.assertTrue(self.repository.ready_for_train())

    def test_be_true_when_deleted_example(self):
        self.repository.current_version()
        self.repository.current_version().start_training(self.owner)
        self.example_1.delete()
        self.assertTrue(self.repository.ready_for_train())

    def test_last_train_failed(self):
        current_version = self.repository.current_version()
        current_version.start_training(self.owner)
        current_version.train_fail()
        self.assertTrue(self.repository.current_version().ready_for_train)

    def test_change_algorithm(self):
        self.assertTrue(self.repository.ready_for_train())
        for (val_current, verb_current) in Repository.ALGORITHM_CHOICES:
            for (val_next, verb_next) in Repository.ALGORITHM_CHOICES:
                if val_current == val_next:
                    continue
                self.repository.algorithm = val_current
                self.repository.save()
                current_version = self.repository.current_version()
                current_version.start_training(self.owner)
                current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
                # self.assertFalse(self.repository.ready_for_train())
                self.repository.algorithm = val_next
                self.repository.save()
                self.assertTrue(self.repository.ready_for_train())


class RepositoryUpdateReadyForTrain(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
            algorithm=Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL,
        )

    def test_be_true(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        self.assertTrue(self.repository.current_version().ready_for_train)

    def test_be_false(self):
        self.assertFalse(self.repository.current_version().ready_for_train)

    def test_new_translate(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        example_2 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello",
            intent=example_intent_1,
        )
        self.repository.current_version().start_training(self.owner)
        RepositoryTranslatedExample.objects.create(
            original_example=example_1, language=languages.LANGUAGE_PT, text="oi"
        )
        RepositoryTranslatedExample.objects.create(
            original_example=example_2, language=languages.LANGUAGE_PT, text="olá"
        )
        self.assertTrue(
            self.repository.current_version(languages.LANGUAGE_PT).ready_for_train
        )

    def test_when_deleted(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello",
            intent=example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hellow",
            intent=example_intent_1,
        )
        self.repository.current_version().start_training(self.owner)
        example.delete()
        self.assertTrue(self.repository.current_version().ready_for_train)

    def test_empty_intent(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="user",
            intent=example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="user",
            intent=example_intent_1,
        )
        RepositoryExampleEntity.objects.create(
            repository_example=example, start=0, end=7, entity="name"
        )
        RepositoryExampleEntity.objects.create(
            repository_example=example, start=0, end=7, entity="name"
        )

        self.assertFalse(self.repository.current_version().ready_for_train)

    def test_intent_dont_have_min_examples(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        self.assertFalse(self.repository.current_version().ready_for_train)

    def test_entity_dont_have_min_examples(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello",
            intent=example_intent_1,
        )
        RepositoryExampleEntity.objects.create(
            repository_example=example, start=0, end=2, entity="hi"
        )
        self.assertFalse(self.repository.current_version().ready_for_train)
        RepositoryExampleEntity.objects.create(
            repository_example=example, start=1, end=2, entity="hi"
        )
        self.assertTrue(self.repository.current_version().ready_for_train)

    def test_settings_change_exists_requirements(self):
        self.repository.current_version().start_training(self.owner)
        self.repository.algorithm = Repository.ALGORITHM_NEURAL_NETWORK_EXTERNAL
        self.repository.save()
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hello",
            intent=example_intent_1,
        )
        self.assertEqual(
            len(self.repository.current_version().requirements_to_train), 1
        )
        self.assertFalse(self.repository.current_version().ready_for_train)

    def test_no_examples(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        self.repository.current_version().start_training(self.owner)
        example.delete()
        self.assertFalse(self.repository.current_version().ready_for_train)


class RequestRepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "owner")
        repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.user = User.objects.create_user("user@user.com", "user")
        self.ra = RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=repository, text="I can contribute"
        )
        self.admin = User.objects.create_user("admin@user.com", "admin")
        admin_authorization = repository.get_user_authorization(self.admin)
        admin_authorization.role = RepositoryAuthorization.ROLE_ADMIN
        admin_authorization.save()

    def test_approve(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        user_authorization = self.ra.repository.get_user_authorization(self.ra.user)
        self.assertEqual(user_authorization.role, RepositoryAuthorization.ROLE_USER)

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

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
        )

        self.repository_version = self.repository.current_version().repository_version

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias", repository_version=self.repository_version
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is User",
            intent=self.example_intent_1,
        )

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="name"
        )

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=0, end=2, entity="object"
        )

    def test_example_entity_create_entity(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )
        self.assertEqual(name_entity.pk, self.example_entity_1.entity.pk)

    def test_dont_duplicate_entity(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )

        new_example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="name"
        )

        self.assertEqual(name_entity.pk, self.example_entity_1.entity.pk)
        self.assertEqual(name_entity.pk, new_example_entity.entity.pk)


class RepositoryEntityGroupTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
        )

        self.repository_version = self.repository.current_version().repository_version

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias", repository_version=self.repository_version
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is User",
            intent=self.example_intent_1,
        )

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="name"
        )

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=0, end=2, entity="object"
        )

    def test_set_label(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )

        name_entity.set_group("subject")

        self.assertIsNotNone(name_entity.group)

    def test_entity_label_created(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )

        name_entity.set_group("subject")

        subject_label = RepositoryEntityGroup.objects.get(
            repository_version=self.repository_version, value="subject"
        )

        self.assertEqual(name_entity.group.pk, subject_label.pk)

    def test_dont_duplicate_label(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )
        name_entity.set_group("subject")

        object_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="object"
        )
        object_entity.set_group("subject")

        subject_label = RepositoryEntityGroup.objects.get(
            repository_version=self.repository_version, value="subject"
        )

        self.assertEqual(name_entity.group.pk, subject_label.pk)
        self.assertEqual(object_entity.group.pk, subject_label.pk)

    def test_set_label_to_none(self):
        name_entity = RepositoryEntity.objects.get(
            repository_version=self.repository_version, value="name"
        )

        name_entity.set_group(None)

        self.assertIsNone(name_entity.group)


class RepositoryOtherEntitiesTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = self.repository.current_version().repository_version

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias", repository_version=self.repository_version
        )

        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is User",
            intent=self.example_intent_1,
        )

        self.example_entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="user"
        )
        entity = self.example_entity_1.entity
        entity.set_group("name")
        entity.save()

        self.example_entity_2 = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=0, end=2, entity="object"
        )

    def test_ok(self):
        other_entities = self.repository_version.other_entities()
        self.assertEqual(other_entities.count(), 1)
        self.assertIn(self.example_entity_2.entity, other_entities)


class UseLanguageModelFeaturizerTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
            algorithm=Repository.ALGORITHM_NEURAL_NETWORK_EXTERNAL,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is John",
            intent=self.example_intent_1,
        )

    def test_equal_repository_value_after_train(self):
        current_version = self.repository.current_version()
        self.repository.algorithm = Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL
        self.repository.save()
        current_version.start_training(self.owner)
        current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
        self.assertFalse(current_version.use_language_model_featurizer)


class UseCompetingIntentsTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
            use_competing_intents=True,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is John",
            intent=self.example_intent_1,
        )

    def test_change_ready_for_train(self):
        self.assertTrue(self.repository.ready_for_train())
        current_version = self.repository.current_version()
        current_version.start_training(self.owner)
        current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
        # self.assertFalse(self.repository.ready_for_train())
        self.repository.use_competing_intents = False
        self.repository.save()
        self.assertTrue(self.repository.ready_for_train())
        self.repository.use_competing_intents = True
        self.repository.save()
        # self.assertFalse(self.repository.ready_for_train())

    def test_equal_repository_value_after_train(self):
        current_version = self.repository.current_version()
        self.repository.use_competing_intents = False
        self.repository.save()
        current_version.start_training(self.owner)
        current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
        self.assertFalse(current_version.use_competing_intents)


class UseNameEntitiesTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
            use_name_entities=True,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is John",
            intent=self.example_intent_1,
        )

    def test_change_ready_for_train(self):
        self.assertTrue(self.repository.ready_for_train())
        current_version = self.repository.current_version()
        current_version.start_training(self.owner)
        current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
        # self.assertFalse(self.repository.ready_for_train())
        self.repository.use_name_entities = False
        self.repository.save()
        self.assertTrue(self.repository.ready_for_train())
        self.repository.use_name_entities = True
        self.repository.save()
        # self.assertFalse(self.repository.ready_for_train())

    def test_equal_repository_value_after_train(self):
        current_version = self.repository.current_version()
        self.repository.use_name_entities = False
        self.repository.save()
        current_version.start_training(self.owner)
        current_version.save_training(b"", settings.BOTHUB_NLP_RASA_VERSION)
        self.assertFalse(current_version.use_name_entities)


class RepositoryUpdateWarnings(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
            use_competing_intents=True,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )

    def test_min_intents(self):
        self.assertEqual(len(self.repository.current_version().warnings), 1)
        example_intent_1 = RepositoryIntent.objects.create(
            text="bye",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="bye",
            intent=example_intent_1,
        )
        self.assertEqual(len(self.repository.current_version().warnings), 0)


class RepositorySupportedLanguageQueryTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")
        self.uid = 0

    def _create_repository(self, language):
        self.uid += 1
        return Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test {}".format(language),
            slug="test-{}-{}".format(self.uid, language),
            language=language,
        )

    def test_main_language(self):
        language = languages.LANGUAGE_EN
        repository_en = self._create_repository(language)
        q = Repository.objects.all().supported_language(language)
        self.assertEqual(q.count(), 1)
        self.assertIn(repository_en, q)
        q = Repository.objects.all().supported_language(language)
        repository_pt = self._create_repository(languages.LANGUAGE_PT)
        self.assertEqual(q.count(), 1)
        self.assertNotIn(repository_pt, q)

    def test_has_translation(self):
        language = languages.LANGUAGE_EN
        t_language = languages.LANGUAGE_PT
        repository_en = self._create_repository(language)
        example_intent_1 = RepositoryIntent.objects.create(
            text="bye",
            repository_version=repository_en.current_version().repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=repository_en.current_version(),
            text="bye",
            intent=example_intent_1,
        )
        RepositoryTranslatedExample.objects.create(
            original_example=example, language=t_language, text="tchau"
        )
        q = Repository.objects.all().supported_language(t_language)
        self.assertEqual(q.count(), 1)
        self.assertIn(repository_en, q)

    def test_has_example(self):
        language = languages.LANGUAGE_EN
        e_language = languages.LANGUAGE_PT
        repository_en = self._create_repository(language)
        example_intent_1 = RepositoryIntent.objects.create(
            text="bye",
            repository_version=repository_en.current_version(
                e_language
            ).repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=repository_en.current_version(e_language),
            text="bye",
            intent=example_intent_1,
        )
        q = Repository.objects.all().supported_language(e_language)
        self.assertEqual(q.count(), 1)
        self.assertIn(repository_en, q)
        example.delete()
        q = Repository.objects.all().supported_language(e_language)
        self.assertEqual(q.count(), 0)


class QAKnowledgeBaseTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def test_ok(self):
        qa_knowledge_base = QAKnowledgeBase.objects.create(
            repository=self.repository, title="teste"
        )
        self.assertEqual("teste", qa_knowledge_base.title)
        self.assertEqual(self.repository.knowledge_bases.last(), qa_knowledge_base)


class QAtextTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.knowledge_base = QAKnowledgeBase.objects.create(
            repository=self.repository, title="teste"
        )

    def test_ok(self):
        qa_context = QAtext.objects.create(
            knowledge_base=self.knowledge_base,
            text="teste text",
            language=languages.LANGUAGE_PT,
        )
        self.assertEqual("teste text", qa_context.text)
        self.assertEqual(self.knowledge_base.texts.last(), qa_context)


class RepositoryFormattedIntentsTestCase(TestCase):
    def setUp(self):
        self.language = languages.LANGUAGE_EN

        self.owner = User.objects.create_user("owner@user.com", "user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Test",
            slug="test",
            language=self.language,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

        self.example_2 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi_2",
            intent=self.example_intent_1,
        )

    def test_get_formatted_intents(self):
        intents = self.repository.get_formatted_intents()
        self.assertEqual(intents[0].get("value"), self.example_intent_1.text)
        self.assertEqual(intents[0].get("id"), self.example_intent_1.pk)
        self.assertEqual(intents[0].get("examples__count"), 2)
