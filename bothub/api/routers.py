from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet
from .views import NewRepositoryExampleViewSet
from .views import RepositoryExampleViewSet
from .views import NewRepositoryExampleEntityViewSet
from .views import RepositoryExampleEntityViewSet


router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
router.register('myrepositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
router.register('example/new', NewRepositoryExampleViewSet)
router.register('example', RepositoryExampleViewSet)
router.register('entity/new', NewRepositoryExampleEntityViewSet)
router.register('entity', RepositoryExampleEntityViewSet)
