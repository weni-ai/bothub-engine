from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet
from .views import NewRepositoryExampleViewSet
from .views import RepositoryExampleViewSet
from .views import NewRepositoryTranslatedExampleViewSet
from .views import RepositoryTranslatedExampleViewSet
from .views import NewRepositoryTranslatedExampleEntityViewSet
from .views import RepositoryTranslatedExampleEntityViewSet
from .views import RepositoryExamplesViewSet
from .views import RegisterUserViewSet
from .views import LoginViewSet
from .views import ChangePasswordViewSet
from .views import RequestResetPassword
from .views import ResetPassword
from .views import MyUserProfileViewSet
from .views import UserProfileViewSet
from .views import Categories
from .views import RepositoriesViewSet
from .views import TranslationsViewSet


class Router(routers.SimpleRouter):
    routes = [
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        routers.DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        routers.DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_routes(self, viewset):
        ret = super().get_routes(viewset)
        lookup_field = getattr(viewset, 'lookup_field', None)

        if lookup_field:
            # List route.
            ret.append(routers.Route(
                url=r'^{prefix}{trailing_slash}$',
                mapping={
                    'get': 'list',
                    'post': 'create'
                },
                name='{basename}-list',
                initkwargs={'suffix': 'List'}
            ))

        detail_url_regex = r'^{prefix}/{lookup}{trailing_slash}$'
        if not lookup_field:
            detail_url_regex = r'^{prefix}{trailing_slash}$'
        # Detail route.
        ret.append(routers.Route(
            url=detail_url_regex,
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ))

        return ret

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        lookup_fields = getattr(viewset, 'lookup_fields', None)
        if lookup_fields:
            base_regex = '(?P<{lookup_prefix}{lookup_url_kwarg}>[^/.]+)'
            return '/'.join(map(
                lambda x: base_regex.format(
                    lookup_prefix=lookup_prefix,
                    lookup_url_kwarg=x),
                lookup_fields))
        return super().get_lookup_regex(viewset, lookup_prefix)


router = Router()
router.register('repository/new', NewRepositoryViewSet)
router.register('my-repositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
router.register('example/new', NewRepositoryExampleViewSet)
router.register('example', RepositoryExampleViewSet)
router.register('translate-example', NewRepositoryTranslatedExampleViewSet)
router.register('translation', RepositoryTranslatedExampleViewSet)
router.register('translation-entity/new',
                NewRepositoryTranslatedExampleEntityViewSet)
router.register('translation-entity',
                RepositoryTranslatedExampleEntityViewSet)
router.register('examples', RepositoryExamplesViewSet)
router.register('register', RegisterUserViewSet)
router.register('login', LoginViewSet)
router.register('change-password', ChangePasswordViewSet)
router.register('forgot-password', RequestResetPassword)
router.register('reset-password', ResetPassword)
router.register('my-profile', MyUserProfileViewSet)
router.register('user-profile', UserProfileViewSet)
router.register('categories', Categories)
router.register('repositories', RepositoriesViewSet)
router.register('translations', TranslationsViewSet)
