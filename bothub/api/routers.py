from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet

router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
router.register('myrepositories', MyRepositoriesViewSet)
