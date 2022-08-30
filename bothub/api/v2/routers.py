from rest_framework import routers

from bothub.api.v2.internal.organization.views import InternalOrganizationViewSet
from bothub.api.v2.internal.repository.views import InternalRepositoriesViewSet
from bothub.api.v2.internal.user.views import (
    UserLanguageViewSet,
    UserPermissionViewSet,
    UserViewSet,
)
from bothub.api.v2.versionning.views import RepositoryVersionViewSet

from .account.views import (
    ChangePasswordViewSet,
    LoginViewSet,
    MyUserProfileViewSet,
    RegisterUserViewSet,
    RequestResetPasswordViewSet,
    ResetPasswordViewSet,
    SearchUserViewSet,
    UserProfileViewSet,
)
from .evaluate.views import EvaluateViewSet, ResultsListViewSet
from .examples.views import ExamplesViewSet
from .groups.views import RepositoryEntityGroupViewSet
from .knowledge_base.views import QAKnowledgeBaseViewSet, QAtextViewSet
from .nlp.views import (
    NLPLangsViewSet,
    RepositoryAuthorizationAutomaticEvaluateViewSet,
    RepositoryAuthorizationEvaluateViewSet,
    RepositoryAuthorizationExamplesViewSet,
    RepositoryAuthorizationInfoViewSet,
    RepositoryAuthorizationKnowledgeBaseViewSet,
    RepositoryAuthorizationParseViewSet,
    RepositoryAuthorizationTrainLanguagesViewSet,
    RepositoryAuthorizationTrainViewSet,
    RepositoryNLPLogsViewSet,
    RepositoryQANLPLogsViewSet,
    RepositoryUpdateInterpretersViewSet,
)
from .organization.views import (
    OrganizationAuthorizationViewSet,
    OrganizationProfileViewSet,
    OrganizationViewSet,
)
from .repository.views import (
    CloneRepositoryViewSet,
    NewRepositoryViewSet,
    RasaUploadViewSet,
    RepositoriesContributionsViewSet,
    RepositoriesPermissionsViewSet,
    RepositoriesViewSet,
    RepositoryAuthorizationRequestsViewSet,
    RepositoryAuthorizationViewSet,
    RepositoryCategoriesView,
    RepositoryEntitiesViewSet,
    RepositoryExamplesBulkViewSet,
    RepositoryExampleViewSet,
    RepositoryIntentViewSet,
    RepositoryMigrateViewSet,
    RepositoryNLPLogReportsViewSet,
    RepositoryNLPLogViewSet,
    RepositoryQANLPLogViewSet,
    RepositoryTaskQueueViewSet,
    RepositoryTokenByUserViewSet,
    RepositoryTrainInfoViewSet,
    RepositoryTranslatorInfoViewSet,
    RepositoryViewSet,
    RepositoryVotesViewSet,
    SearchRepositoriesViewSet,
)
from .translation.views import (
    RepositoryTranslatedExampleViewSet,
    RepositoryTranslatedExporterViewSet,
)
from .translator.views import (
    RepositoryTranslationTranslatorExampleViewSet,
    RepositoryTranslatorViewSet,
    TranslatorExamplesViewSet,
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
router.register(
    "repository/authorization-by-user",
    RepositoryTokenByUserViewSet,
    basename="authorization-by-user",
)
router.register("repository/example", RepositoryExampleViewSet)
router.register("repository/example-bulk", RepositoryExamplesBulkViewSet)
router.register("repository/intent", RepositoryIntentViewSet)
router.register("repository/evaluate/results", ResultsListViewSet)
router.register("repository/evaluate", EvaluateViewSet)
router.register("repository/translation", RepositoryTranslatedExampleViewSet)
router.register("repository/translation-export", RepositoryTranslatedExporterViewSet)
router.register("repository/version", RepositoryVersionViewSet)
router.register("repository/log", RepositoryNLPLogViewSet, basename="es-repository-log")
router.register(
    "repository/qalog", RepositoryQANLPLogViewSet, basename="es-repository-qa-log"
)
router.register("repository/entities", RepositoryEntitiesViewSet)
router.register("repository/task-queue", RepositoryTaskQueueViewSet)
router.register("repository/qa/knowledge-base", QAKnowledgeBaseViewSet)
router.register("repository/qa/text", QAtextViewSet)
router.register("repository/upload-rasa-file", RasaUploadViewSet)
router.register("repository/entity/group", RepositoryEntityGroupViewSet)
router.register("repository/repository-migrate", RepositoryMigrateViewSet)
router.register("repository/clone-repository", CloneRepositoryViewSet)

router.register(
    "repository/nlp/authorization/train", RepositoryAuthorizationTrainViewSet
)
router.register(
    "repository/nlp/authorization/train-languages",
    RepositoryAuthorizationTrainLanguagesViewSet,
)
router.register(
    "repository/nlp/authorization/parse", RepositoryAuthorizationParseViewSet
)
router.register(
    "repository/nlp/authorization/examples", RepositoryAuthorizationExamplesViewSet
)
router.register("repository/nlp/authorization/info", RepositoryAuthorizationInfoViewSet)
router.register(
    "repository/nlp/authorization/evaluate", RepositoryAuthorizationEvaluateViewSet
)
router.register(
    "repository/nlp/authorization/automatic-evaluate",
    RepositoryAuthorizationAutomaticEvaluateViewSet,
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
router.register("repository/nlp/qa/log", RepositoryQANLPLogsViewSet)
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
router.register("internal/organization", InternalOrganizationViewSet)
router.register("internal/repository", InternalRepositoriesViewSet)
router.register("internal/user", UserViewSet)
router.register("internal/user/permission", UserPermissionViewSet)
router.register("internal/user/language", UserLanguageViewSet)
