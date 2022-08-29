from uuid import uuid4

from django.test import RequestFactory, TestCase
from django.utils import timezone
from bothub.common.tasks import clone_repository

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
)


class RepositoryCloneTestCase(TestCase):
    """Test clone_repository task, validating all repository fields"""

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
        for repository in self.repositories:
            RepositoryVersion.objects.create(
                repository=repository, name="beta", is_default=False
            )
            RepositoryVersion.objects.create(
                repository=repository, name="alfa", is_default=True
            )

            QAKnowledgeBase.objects.create(repository=repository, user=self.user)
            QAKnowledgeBase.objects.create(repository=repository, user=self.owner)

        return super().setUp()

    def test_clone_function(self):

        """validate the underlying function result"""
        repository = self.repositories[0]

        original_data = {
            "pk": repository.pk,
            "owner_id": repository.owner_id,
            "slug": repository.slug,
            "name": repository.name,
            "owner": repository.owner,
            "is_private": repository.is_private,
            "count_authorizations": repository.count_authorizations,
            "created_at": repository.created_at,
            "categories_ids": repository.categories.all().values_list("id", flat=True),
            "versions_ids": repository.versions.all().values_list("id", flat=True),
            "knowledge_bases_ids": repository.knowledge_bases.all().values_list(
                "id", flat=True
            ),
        }
        clone_created_at = timezone.now()

        # Cloning Now
        clone = Repository.objects.create(
            owner=self.organization, slug=uuid4().hex[:32]
        )
        clone_id = clone_repository(repository.pk, clone.pk, self.organization.pk)

        repository = Repository.objects.get(pk=original_data.get("pk"))

        # Ensure original Repository fields were not altered.
        self.assertEqual(original_data.get("owner_id"), getattr(repository, "owner_id"))
        self.assertEqual(original_data.get("slug"), getattr(repository, "slug"))
        self.assertEqual(original_data.get("name"), getattr(repository, "name"))
        self.assertEqual(
            original_data.get("is_private"), getattr(repository, "is_private")
        )
        self.assertEqual(
            original_data.get("count_authorizations"),
            getattr(repository, "count_authorizations"),
        )
        self.assertEqual(
            original_data.get("created_at"), getattr(repository, "created_at")
        )
        repository_categories = repository.categories.all().values_list("id", flat=True)
        repository_versions = repository.versions.all().values_list("id", flat=True)
        repository_knowledge_bases = repository.knowledge_bases.all().values_list(
            "id", flat=True
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
        self.assertEqual(clone.repository_type, repository.repository_type)
        self.assertEqual(clone.algorithm, repository.algorithm)
        self.assertEqual(clone.language, repository.language)
        self.assertEqual(clone.use_competing_intents, repository.use_competing_intents)
        self.assertEqual(clone.use_name_entities, repository.use_name_entities)
        self.assertEqual(clone.use_analyze_char, repository.use_analyze_char)
        self.assertEqual(clone.description, repository.description)

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

        # clone_versions = clone.versions.all().values_list("id", flat=True)
        # self.assertNotEqual(len(clone_versions), 0)
        # self.assertEqual(len(clone_versions), len(repository_versions))
