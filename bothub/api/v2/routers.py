from rest_framework import routers

from bothub.api.v2.versionning.views import RepositoryVersionViewSet
from .groups.views import RepositoryEntityGroupViewSet
from .knowledge_base.views import QAKnowledgeBaseViewSet
from .organization.views import (
    OrganizationViewSet,
    OrganizationProfileViewSet,
    OrganizationAuthorizationViewSet,
)
from .repository.views import (
    RepositoryViewSet,
    RepositoryNLPLogViewSet,
    RepositoryEntitiesViewSet,
    NewRepositoryViewSet,
    RasaUploadViewSet,
    RepositoryTaskQueueViewSet,
    RepositoriesPermissionsViewSet,
    RepositoryNLPLogReportsViewSet,
    RepositoryIntentViewSet,
    RepositoryTranslatorInfoViewSet,
    RepositoryTrainInfoViewSet,
    RepositoryExamplesBulkViewSet,
)
from .repository.views import RepositoryVotesViewSet
from .repository.views import RepositoryMigrateViewSet
from .repository.views import RepositoriesViewSet
from .repository.views import RepositoriesContributionsViewSet
from .repository.views import RepositoryCategoriesView
from .repository.views import SearchRepositoriesViewSet
from .repository.views import RepositoryAuthorizationViewSet
from .repository.views import RepositoryAuthorizationRequestsViewSet
from .repository.views import RepositoryExampleViewSet
from .nlp.views import (
    RepositoryAuthorizationTrainViewSet,
    RepositoryNLPLogsViewSet,
    RepositoryAuthorizationKnowledgeBaseViewSet,
)
from .nlp.views import RepositoryAuthorizationParseViewSet
from .nlp.views import RepositoryAuthorizationInfoViewSet
from .nlp.views import RepositoryAuthorizationEvaluateViewSet
from .nlp.views import NLPLangsViewSet
from .nlp.views import RepositoryUpdateInterpretersViewSet
from .examples.views import ExamplesViewSet
from .evaluate.views import EvaluateViewSet
from .evaluate.views import ResultsListViewSet
from .account.views import LoginViewSet
from .account.views import RegisterUserViewSet
from .account.views import ChangePasswordViewSet
from .account.views import RequestResetPasswordViewSet
from .account.views import UserProfileViewSet
from .account.views import MyUserProfileViewSet
from .account.views import SearchUserViewSet
from .account.views import ResetPasswordViewSet
from .translation.views import RepositoryTranslatedExampleViewSet
from .translation.views import RepositoryTranslatedExporterViewSet
from .translator.views import (
    TranslatorExamplesViewSet,
    RepositoryTranslationTranslatorExampleViewSet,
    RepositoryTranslatorViewSet,
)


class Router(routers.SimpleRouter):
    routes = [
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r"^{prefix}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
        # Dynamically generated list routes.
        # Generated using @action decorator
        # on methods of the viewset.
        routers.DynamicRoute(
            url=r"^{prefix}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
        # Dynamically generated detail routes.
        # Generated using @action decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
    ]

    def get_routes(self, viewset):
        ret = super().get_routes(viewset)
        lookup_field = getattr(viewset, "lookup_field", None)

        if lookup_field:
            # List route.
            ret.append(
                routers.Route(
                    url=r"^{prefix}{trailing_slash}$",
                    mapping={"get": "list", "post": "create"},
                    name="{basename}-list",
                    detail=False,
                    initkwargs={"suffix": "List"},
                )
            )

        detail_url_regex = r"^{prefix}/{lookup}{trailing_slash}$"
        if not lookup_field:
            detail_url_regex = r"^{prefix}{trailing_slash}$"
        # Detail route.
        ret.append(
            routers.Route(
                url=detail_url_regex,
                mapping={
                    "get": "retrieve",
                    "put": "update",
                    "patch": "partial_update",
                    "delete": "destroy",
                },
                name="{basename}-detail",
                detail=True,
                initkwargs={"suffix": "Instance"},
            )
        )

        return ret

    def get_lookup_regex(self, viewset, lookup_prefix=""):
        lookup_fields = getattr(viewset, "lookup_fields", None)
        if lookup_fields:
            base_regex = "(?P<{lookup_prefix}{lookup_url_kwarg}>[^/.]+)"
            return "/".join(
                map(
                    lambda x: base_regex.format(
                        lookup_prefix=lookup_prefix, lookup_url_kwarg=x
                    ),
                    lookup_fields,
                )
            )
        return super().get_lookup_regex(viewset, lookup_prefix)


router = Router()
router.register("repository/repository-details", RepositoryViewSet)
router.register("repository/info", NewRepositoryViewSet)
router.register("repository/train/info", RepositoryTrainInfoViewSet)
router.register("repository/repository-votes", RepositoryVotesViewSet)
router.register("repository/repositories", RepositoriesViewSet)
router.register(
    "repository/repositories-contributions", RepositoriesContributionsViewSet
)
router.register("repository/repository-reports", RepositoryNLPLogReportsViewSet)
router.register("repository/categories", RepositoryCategoriesView)
router.register("repository/examples", ExamplesViewSet)
router.register("repository/translator/control", RepositoryTranslatorViewSet)
router.register("repository/translator/info", RepositoryTranslatorInfoViewSet)
router.register("repository/translator/examples", TranslatorExamplesViewSet)
router.register(
    "repository/translator/translation", RepositoryTranslationTranslatorExampleViewSet
)
router.register("repository/search-repositories", SearchRepositoriesViewSet)
router.register("repository/repositories-permissions", RepositoriesPermissionsViewSet)
router.register("repository/authorizations", RepositoryAuthorizationViewSet)
router.register(
    "repository/authorization-requests", RepositoryAuthorizationRequestsViewSet
)
router.register("repository/example", RepositoryExampleViewSet)
router.register("repository/example-bulk", RepositoryExamplesBulkViewSet)
router.register("repository/intent", RepositoryIntentViewSet)
router.register("repository/evaluate/results", ResultsListViewSet)
router.register("repository/evaluate", EvaluateViewSet)
router.register("repository/translation", RepositoryTranslatedExampleViewSet)
router.register("repository/translation-export", RepositoryTranslatedExporterViewSet)
router.register("repository/version", RepositoryVersionViewSet)
router.register("repository/log", RepositoryNLPLogViewSet)
router.register("repository/entities", RepositoryEntitiesViewSet)
router.register("repository/task-queue", RepositoryTaskQueueViewSet)
router.register("repository/knowledge-base", QAKnowledgeBaseViewSet)
router.register("repository/upload-rasa-file", RasaUploadViewSet)
router.register("repository/entity/group", RepositoryEntityGroupViewSet)
router.register("repository/repository-migrate", RepositoryMigrateViewSet)
router.register(
    "repository/nlp/authorization/train", RepositoryAuthorizationTrainViewSet
)
router.register(
    "repository/nlp/authorization/parse", RepositoryAuthorizationParseViewSet
)
router.register("repository/nlp/authorization/info", RepositoryAuthorizationInfoViewSet)
router.register(
    "repository/nlp/authorization/evaluate", RepositoryAuthorizationEvaluateViewSet
)
router.register("repository/nlp/authorization/langs", NLPLangsViewSet)
router.register(
    "repository/nlp/update_interpreters", RepositoryUpdateInterpretersViewSet
)
router.register(
    "repository/nlp/authorization/knowledge-base",
    RepositoryAuthorizationKnowledgeBaseViewSet,
)
router.register("repository/nlp/log", RepositoryNLPLogsViewSet)
router.register("account/login", LoginViewSet)
router.register("account/register", RegisterUserViewSet)
router.register("account/change-password", ChangePasswordViewSet)
router.register("account/forgot-password", RequestResetPasswordViewSet)
router.register("account/user-profile", UserProfileViewSet)
router.register("account/my-profile", MyUserProfileViewSet)
router.register("account/search-user", SearchUserViewSet)
router.register("account/reset-password", ResetPasswordViewSet)
router.register("org/organization", OrganizationViewSet)
router.register("org/profile", OrganizationProfileViewSet)
router.register("org/authorizations", OrganizationAuthorizationViewSet)
