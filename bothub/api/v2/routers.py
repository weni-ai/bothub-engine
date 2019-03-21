from rest_framework import routers

from .repository.views import RepositoryViewSet
from .repository.views import RepositoriesViewSet
from .examples.views import ExamplesViewSet
from .validation.views import NewValidationViewSet
from .validation.views import ListValidationViewSet
from .validation.views import ListValidationsViewSet


router = routers.SimpleRouter()
router.register('repository', RepositoryViewSet)
router.register('repositories', RepositoriesViewSet)
router.register('examples', ExamplesViewSet)
router.register('validation/new', NewValidationViewSet)
router.register('validation', ListValidationViewSet)
router.register('validations', ListValidationsViewSet)
