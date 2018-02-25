from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet

router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
router.register('myrepositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
