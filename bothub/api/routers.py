from rest_framework import routers

from .views import NewRepositoryViewSet

router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
