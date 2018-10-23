from rest_framework import routers

from .repository.views import RepositoryViewSet
from .examples.views import ExamplesViewSet


router = routers.SimpleRouter()
router.register('repository', RepositoryViewSet)
router.register('examples', ExamplesViewSet)
