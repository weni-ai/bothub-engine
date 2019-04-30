from rest_framework import routers

from .repository.views import RepositoryViewSet
from .repository.views import RepositoriesViewSet
from .examples.views import ExamplesViewSet
from .evaluate.views import EvaluateViewSet
from .evaluate.views import ResultsListViewSet


router = routers.SimpleRouter()
router.register('repository', RepositoryViewSet)
router.register('repositories', RepositoriesViewSet)
router.register('examples', ExamplesViewSet)
router.register('evaluate/results', ResultsListViewSet)
router.register('evaluate', EvaluateViewSet)
