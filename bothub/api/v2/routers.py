from rest_framework import routers

from .repository.views import RepositoryViewSet


router = routers.SimpleRouter()
router.register('repository', RepositoryViewSet)
