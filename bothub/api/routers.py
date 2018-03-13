from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet
from .views import NewRepositoryExampleViewSet
from .views import RepositoryExampleViewSet
from .views import NewRepositoryExampleEntityViewSet
from .views import RepositoryExampleEntityViewSet
from .views import NewRepositoryTranslatedExampleViewSet
from .views import RepositoryTranslatedExampleViewSet
from .views import NewRepositoryTranslatedExampleEntityViewSet
from .views import RepositoryTranslatedExampleEntityViewSet
from .views import RepositoryExamplesViewSet
from .views import RegisterUserViewSet


router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
router.register('my-repositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
router.register('example/new', NewRepositoryExampleViewSet)
router.register('example', RepositoryExampleViewSet)
router.register('entity/new', NewRepositoryExampleEntityViewSet)
router.register('entity', RepositoryExampleEntityViewSet)
router.register('translate-example', NewRepositoryTranslatedExampleViewSet)
router.register('translated', RepositoryTranslatedExampleViewSet)
router.register('translated-entity/new',
                NewRepositoryTranslatedExampleEntityViewSet)
router.register('translated-entity',
                RepositoryTranslatedExampleEntityViewSet)
router.register('examples', RepositoryExamplesViewSet)
router.register('register', RegisterUserViewSet)
