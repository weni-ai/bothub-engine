import random

from django.core.management.base import BaseCommand
from django.conf import settings

from bothub.authentication.models import User
from bothub.common.models import RepositoryCategory
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common import languages


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        assert settings.DEBUG, 'Don\'t run this command in production'

        # Users

        User.objects.create_superuser(
            email='admin@bothub.it',
            nickname='admin',
            password='admin',
            name='Admin')

        douglas = User.objects.create_user(
            email='douglas@bothub.it',
            nickname='douglas',
            password='douglas',
            name='Douglas Paz')

        user = User.objects.create_user(
            email='user@bothub.it',
            nickname='user',
            password='user',
            name='User')

        # Categories

        categories = list(map(
            lambda x: RepositoryCategory.objects.create(
                name='Category {}'.format(x)),
            range(1, 6)))

        # Repositories

        repository_1 = Repository.objects.create(
            owner=douglas,
            name='Repository 1',
            slug='repo1',
            language=languages.LANGUAGE_EN)
        repository_1.categories.add(categories[0])
        repository_1.categories.add(categories[1])
        repository_1.categories.add(categories[3])

        repository_2 = Repository.objects.create(
            owner=user,
            name='Repository 2',
            slug='repo2',
            language=languages.LANGUAGE_EN)
        repository_2.categories.add(categories[0])
        repository_2.categories.add(categories[2])

        for x in range(3, 46):
            new_repository = Repository.objects.create(
                owner=random.choice([douglas, user]),
                name='Repository {}'.format(x),
                slug='repo{}'.format(x),
                language=languages.LANGUAGE_EN)
            new_repository.categories.add(random.choice(categories))

        # Examples

        example_1 = RepositoryExample.objects.create(
            repository_update=repository_1.current_update(),
            text='hi',
            intent='greet')

        example_2 = RepositoryExample.objects.create(
            repository_update=repository_1.current_update(),
            text='hello',
            intent='greet')

        example_3 = RepositoryExample.objects.create(
            repository_update=repository_1.current_update(),
            text='yes',
            intent='affirm')

        RepositoryExample.objects.create(
            repository_update=repository_1.current_update(),
            text='yep',
            intent='affirm')

        example_5 = RepositoryExample.objects.create(
            repository_update=repository_1.current_update(),
            text='show me chinese restaurants',
            intent='restaurant_search')

        # Example Entity

        RepositoryExampleEntity.objects.create(
            repository_example=example_5,
            start=8,
            end=15,
            entity='cuisine')

        # Translated Example

        RepositoryTranslatedExample.objects.create(
            original_example=example_1,
            language=languages.LANGUAGE_PT,
            text='oi')

        RepositoryTranslatedExample.objects.create(
            original_example=example_2,
            language=languages.LANGUAGE_PT,
            text='olá')

        RepositoryTranslatedExample.objects.create(
            original_example=example_3,
            language=languages.LANGUAGE_PT,
            text='sim')

        tranlated_4 = RepositoryTranslatedExample.objects.create(
            original_example=example_5,
            language=languages.LANGUAGE_PT,
            text='mostre me restaurantes chinês')

        # Translated Example Entity

        RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=tranlated_4,
            start=23,
            end=29,
            entity='cuisine')
