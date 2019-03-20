from rest_framework import routers

from .repository.views import RepositoryViewSet
from .repository.views import RepositoriesViewSet
from .examples.views import ExamplesViewSet
from .validation.views import ValidationViewSet
from .validation.views import ValidationsViewSet


router = routers.SimpleRouter()
router.register('repository', RepositoryViewSet)
router.register('repositories', RepositoriesViewSet)
router.register('examples', ExamplesViewSet)
router.register('validation', ValidationViewSet)
router.register('validations', ValidationsViewSet)
