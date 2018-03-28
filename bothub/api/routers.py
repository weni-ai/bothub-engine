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
from .views import UserViewSet
from .views import LoginViewSet
from .views import ChangePasswordViewSet
from .views import RequestResetPassword
from .views import ResetPassword


router = routers.SimpleRouter()
router.register('repository/new', NewRepositoryViewSet)
router.register('my-repositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
router.register('example/new', NewRepositoryExampleViewSet)
router.register('example', RepositoryExampleViewSet)
router.register('entity/new', NewRepositoryExampleEntityViewSet)
router.register('entity', RepositoryExampleEntityViewSet)
router.register('translate-example', NewRepositoryTranslatedExampleViewSet)
router.register('translation', RepositoryTranslatedExampleViewSet)
router.register('translation-entity/new',
                NewRepositoryTranslatedExampleEntityViewSet)
router.register('translation-entity',
                RepositoryTranslatedExampleEntityViewSet)
router.register('examples', RepositoryExamplesViewSet)
router.register('register', RegisterUserViewSet)
router.register('profile', UserViewSet)
router.register('login', LoginViewSet)
router.register('change-password', ChangePasswordViewSet)
router.register('forgot-password', RequestResetPassword)
router.register('reset-password', ResetPassword)
