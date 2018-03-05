from django.test import TestCase
from django.utils import timezone

from bothub.authentication.models import User
from .models import Repository, RepositoryExample, RepositoryExampleEntity


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
