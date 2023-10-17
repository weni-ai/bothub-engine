import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model

from bothub.common import languages
from bothub.common.models import Repository
from bothub.wenigpt.models import ContentBase, ContentBaseText, ContentBaseFile


User = get_user_model()


class ContentBaseTest(TestCase):

    def setUp(self):
        self.my_user = User.objects.create(email="fake_email@fake.com", nickname="fake_email@fake.com")
        self.repository = self.repository = Repository.objects.create(
            owner=self.my_user,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.base_content = ContentBase.objects.create(
            uuid=uuid.uuid4(),
            title="my base test",
            created_by=self.my_user,
            repository=self.repository
        )

    def test_content_base_created(self):
        self.assertEqual(self.base_content.title, "my base test")
        self.assertEqual(self.base_content.created_by, self.my_user)
        self.assertEqual(self.base_content.repository, self.repository)


class ContentBaseTextTestCase(TestCase):

    def setUp(self):
        self.my_user = User.objects.create(email="fake_email@fake.com", nickname="fake_email@fake.com")
        self.repository = self.repository = Repository.objects.create(
            owner=self.my_user,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.base_content = ContentBase.objects.create(
            uuid=uuid.uuid4(),
            title="my base test",
            created_by=self.my_user,
            repository=self.repository
        )
        self.base_content_text = ContentBaseText.objects.create(
            text="este é um texto de teste para ser classificado aqui no teste",
            content_base=self.base_content
        )

    def test_content_base_text(self):
        self.assertEqual(self.base_content_text.text, "este é um texto de teste para ser classificado aqui no teste")


class ContentBaseFileTestCase(TestCase):
    def setUp(self):
        self.my_user = User.objects.create(email="fake_email@fake.com", nickname="fake_email@fake.com")
        self.repository = self.repository = Repository.objects.create(
            owner=self.my_user,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.base_content = ContentBase.objects.create(
            uuid=uuid.uuid4(),
            title="my base test",
            created_by=self.my_user,
            repository=self.repository
        )
        self.base_content_file = ContentBaseFile.objects.create(
            file_url="http://test@weni.ai",
            file_extension=".txt",
            content_base=self.base_content
        )

    def test_content_base_file(self):
        self.assertEqual(self.base_content_file.file_url, "http://test@weni.ai")
        self.assertEqual(self.base_content_file.file_extension, ".txt")
