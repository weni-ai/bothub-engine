from uuid import uuid4

from django.test import RequestFactory, TestCase
from django.utils import timezone
from bothub.common.tasks import clone_repository, clone_version
from django.conf import settings
from bothub.api.v2.tests.utils import (
    create_repository_from_mockup,
    create_user_and_token,
    get_valid_mockups,
)
from bothub.common.models import (
    Organization,
    OrganizationAuthorization,
    QAKnowledgeBase,
    Repository,
    RepositoryCategory,
    RepositoryVersion,
    RepositoryVersionLanguage,
)


class RepositoryCloneTestCase(TestCase):
    """Test clone_repository task, validating all repository fields"""

    # Ideally, the test would invoke the 'clone_self' method of the Repository model,
    # queueing into celery both the clone_repository and clone_version functions.
    # But, in order to more easily test the result of those functions synchronously,
    # we invoke each of them in a separate function, respecting the way it's done
    # in the Repository.clone_self method

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")
        self.organization = Organization.objects.create(name="Org", verificated=True)
        self.organization.set_user_permission(
            self.user, OrganizationAuthorization.ROLE_ADMIN
        )

        # Create categories for repositories
        self.category_1 = RepositoryCategory.objects.create(name="Category 1")
        self.category_2 = RepositoryCategory.objects.create(name="Category 2")
        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category_1, self.category_2])
        ]
        # Create versions and knowledge bases for repositories
        languages = list(settings.SUPPORTED_LANGUAGES.keys())
        for repository in self.repositories:
            rv1 = RepositoryVersion.objects.create(
                repository=repository, name="beta", is_default=False
            )
            RepositoryVersionLanguage.objects.create(
                repository_version=rv1,
                language=languages[0],
            )
            RepositoryVersionLanguage.objects.create(
                repository_version=rv1,
                language=languages[-1],
            )

            rv2 = RepositoryVersion.objects.create(
                repository=repository, name="alfa", is_default=True
            )
            RepositoryVersionLanguage.objects.create(
                repository_version=rv2,
                language=languages[0],
            )
            RepositoryVersionLanguage.objects.create(
                repository_version=rv2,
                language=languages[-1],
            )

            QAKnowledgeBase.objects.create(repository=repository, user=self.user)
            QAKnowledgeBase.objects.create(repository=repository, user=self.owner)

        self.main_repository = self.repositories[0]
        self.slug = uuid4().hex[:32]

        return super().setUp()

    def clone_repository_function(self):

        """validate the underlying function result"""

        original_data = {
            "pk": self.main_repository.pk,
            "owner_id": self.main_repository.owner_id,
            "slug": self.main_repository.slug,
            "name": self.main_repository.name,
            "owner": self.main_repository.owner,
            "is_private": self.main_repository.is_private,
            "count_authorizations": self.main_repository.count_authorizations,
            "created_at": self.main_repository.created_at,
            "categories_ids": self.main_repository.categories.all().values_list(
                "id", flat=True
            ),
            "versions_ids": self.main_repository.versions.all().values_list(
                "id", flat=True
            ),
            "knowledge_bases_ids": self.main_repository.knowledge_bases.all().values_list(
                "id", flat=True
            ),
        }
        clone_created_at = timezone.now()

        # Cloning Now
        clone = Repository.objects.create(owner=self.organization, slug=self.slug)
        clone_id = clone_repository(
            self.main_repository.pk, clone.pk, self.organization.pk
        )

        self.main_repository = Repository.objects.get(pk=original_data.get("pk"))

        # Ensure original Repository fields were not altered.
        self.assertEqual(
            original_data.get("owner_id"), getattr(self.main_repository, "owner_id")
        )
        self.assertEqual(
            original_data.get("slug"), getattr(self.main_repository, "slug")
        )
        self.assertEqual(
            original_data.get("name"), getattr(self.main_repository, "name")
        )
        self.assertEqual(
            original_data.get("is_private"), getattr(self.main_repository, "is_private")
        )
        self.assertEqual(
            original_data.get("count_authorizations"),
            getattr(self.main_repository, "count_authorizations"),
        )
        self.assertEqual(
            original_data.get("created_at"), getattr(self.main_repository, "created_at")
        )
        repository_categories = self.main_repository.categories.all().values_list(
            "id", flat=True
        )
        repository_versions = self.main_repository.versions.all().values_list(
            "id", flat=True
        )
        repository_knowledge_bases = (
            self.main_repository.knowledge_bases.all().values_list("id", flat=True)
        )
        self.assertEqual(
            set(original_data.get("categories_ids")), set(repository_categories)
        )
        self.assertEqual(
            set(original_data.get("versions_ids")), set(repository_versions)
        )
        self.assertEqual(
            set(original_data.get("knowledge_bases_ids")),
            set(repository_knowledge_bases),
        )

        self.assertEqual(clone_id, clone.pk)
        clone.refresh_from_db()

        # Ensure clone fields were inherited
        self.assertEqual(clone.repository_type, self.main_repository.repository_type)
        self.assertEqual(clone.algorithm, self.main_repository.algorithm)
        self.assertEqual(clone.language, self.main_repository.language)
        self.assertEqual(
            clone.use_competing_intents, self.main_repository.use_competing_intents
        )
        self.assertEqual(
            clone.use_name_entities, self.main_repository.use_name_entities
        )
        self.assertEqual(clone.use_analyze_char, self.main_repository.use_analyze_char)
        self.assertEqual(clone.description, self.main_repository.description)

        # Ensure clone fields were not inherited
        self.assertEqual(clone.owner_id, self.organization.pk)
        self.assertEqual(clone.is_private, True)
        self.assertEqual(clone.count_authorizations, 0)
        self.assertGreaterEqual(clone.created_at, clone_created_at)

        clone_categories = clone.categories.all().values_list("id", flat=True)
        self.assertNotEqual(len(clone_categories), 0)
        self.assertEqual(len(clone_categories), len(repository_categories))
        self.assertEqual(set(clone_categories), set(repository_categories))

        clone_knowledge_bases = clone.knowledge_bases.all().values_list("id", flat=True)
        self.assertNotEqual(len(clone_knowledge_bases), 0)
        self.assertEqual(len(clone_knowledge_bases), len(repository_knowledge_bases))

    def clone_versions_function(self):

        clone = Repository.objects.get(owner=self.organization, slug=self.slug)
        default_repository_version = (
            self.main_repository.versions.filter(is_default=True)
            .order_by("-last_update")
            .first()
        )
        success = clone_version(clone.pk, default_repository_version.pk)

        self.assertEqual(success, True)
        clone.refresh_from_db()

        # Verify that the cloned version of the repository has had all of the original repository's
        # version_languages cloned
        self.assertEqual(clone.versions.count(), 1)
        clone_repository_version = clone.versions.first()
        repository_version = self.main_repository.versions.filter(
            name=clone_repository_version.name,
            is_default=clone_repository_version.is_default,
        ).first()
        self.assertIsNotNone(repository_version)

        self.assertEqual(repository_version.repositoryversionlanguage_set.count(), 2)
        self.assertEqual(
            repository_version.repositoryversionlanguage_set.count(),
            clone_repository_version.repositoryversionlanguage_set.count(),
        )

    def test_functions(self):
        self.clone_repository_function()
        self.clone_versions_function()
