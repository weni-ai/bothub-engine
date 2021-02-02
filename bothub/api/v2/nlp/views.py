import base64

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import mixins, pagination
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.nlp.serializers import NLPSerializer, RepositoryNLPLogSerializer
from bothub.authentication.authorization import NLPAuthentication
from bothub.authentication.models import User
from bothub.common import languages
from bothub.common.models import (
    RepositoryAuthorization,
    RepositoryVersionLanguage,
    RepositoryNLPLog,
    RepositoryExample,
    RepositoryEvaluate,
    RepositoryQueueTask,
)
from bothub.common.models import RepositoryEntity
from bothub.common.models import RepositoryEvaluateResult
from bothub.common.models import RepositoryEvaluateResultEntity
from bothub.common.models import RepositoryEvaluateResultIntent
from bothub.common.models import RepositoryEvaluateResultScore
from bothub.utils import send_bot_data_file_aws


def check_auth(request):
    try:
        auth = request.META.get("HTTP_AUTHORIZATION").split()
        auth = auth[1]
        return RepositoryAuthorization.objects.get(uuid=auth)
    except Exception:
        msg = _("Invalid token header.")
        raise exceptions.AuthenticationFailed(msg)


class NLPPagination(pagination.PageNumberPagination):
    page_size = 200


class RepositoryAuthorizationTrainViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet
):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    pagination_class = NLPPagination
    authentication_classes = [NLPAuthentication]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository_version = request.query_params.get("repository_version")
        if repository_version:
            current_version = repository_authorization.repository.get_specific_version_id(
                repository_version, str(request.query_params.get("language"))
            )
        else:
            current_version = repository_authorization.repository.current_version(
                str(request.query_params.get("language"))
            )

        return Response(
            {
                "ready_for_train": current_version.ready_for_train,
                "current_version_id": current_version.id,
                "repository_authorization_user_id": repository_authorization.user.id,
                "language": current_version.language,
                "algorithm": current_version.repository_version.repository.algorithm,
                "use_name_entities": current_version.repository_version.repository.use_name_entities,
                "use_competing_intents": current_version.repository_version.repository.use_competing_intents,
                "use_analyze_char": current_version.repository_version.repository.use_analyze_char,
            }
        )

    @action(detail=True, methods=["GET"], url_name="get_examples", lookup_field=[])
    def get_examples(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        queryset = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )

        intent = request.query_params.get("intent")
        examples = (
            queryset.examples.filter(intent__text=intent)
            if intent
            else queryset.examples
        )

        page = self.paginate_queryset(examples)

        examples_return = []

        for example in page:
            get_entities = example.get_entities(queryset.language)

            get_text = example.get_text(queryset.language)

            examples_return.append(
                {
                    "text": get_text,
                    "intent": example.intent.text,
                    "entities": [entit.rasa_nlu_data for entit in get_entities],
                }
            )

        return self.get_paginated_response(examples_return)

    @action(detail=True, methods=["POST"], url_name="save_queue_id", lookup_field=[])
    def save_queue_id(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )

        id_queue = request.data.get("task_id")
        from_queue = request.data.get("from_queue")
        repository.create_task(
            id_queue=id_queue,
            from_queue=from_queue,
            type_processing=RepositoryQueueTask.TYPE_PROCESSING_TRAINING,
        )
        return Response({})

    @action(detail=True, methods=["POST"], url_name="start_training", lookup_field=[])
    def start_training(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )

        repository.start_training(
            get_object_or_404(User, pk=request.data.get("by_user"))
        )

        return Response(
            {
                "language": repository.language,
                "repository_version": repository.id,
                "repository_uuid": str(repository.repository_version.repository.uuid),
                "intent": repository.intents,
                "algorithm": repository.algorithm,
                "use_name_entities": repository.use_name_entities,
                "use_competing_intents": repository.use_competing_intents,
                "use_analyze_char": repository.use_analyze_char,
                "total_training_end": repository.total_training_end,
            }
        )

    @action(detail=True, methods=["POST"], url_name="train_fail", lookup_field=[])
    def train_fail(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )
        repository.train_fail()
        return Response({})

    @action(detail=True, methods=["POST"], url_name="training_log", lookup_field=[])
    def training_log(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )
        repository.training_log = request.data.get("training_log")
        repository.save(update_fields=["training_log"])
        return Response({})


class RepositoryAuthorizationParseViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()

        repository = repository_authorization.repository

        language = request.query_params.get("language")
        repository_version = request.query_params.get("repository_version")

        if language == "None" or language is None:
            language = str(repository.language)

        if repository_version:
            update = repository.get_specific_version_id(repository_version, language)
        else:
            update = repository.last_trained_update(language)

        try:
            return Response(
                {
                    "version": False if update is None else True,
                    "repository_version": update.id,
                    "total_training_end": update.total_training_end,
                    "language": update.language,
                    "algorithm": update.algorithm,
                    "use_name_entities": update.use_name_entities,
                    "use_competing_intents": update.use_competing_intents,
                    "use_analyze_char": update.use_analyze_char,
                }
            )
        except Exception:
            return Response({}, status=400)

    @action(detail=True, methods=["GET"], url_name="repository_entity", lookup_field=[])
    def repository_entity(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )
        repository_entity = get_object_or_404(
            RepositoryEntity,
            repository_version=repository_update.repository_version,
            value=request.query_params.get("entity"),
        )

        return Response(
            {
                "label": True if repository_entity.group else False,
                "label_value": repository_entity.group.value
                if repository_entity.group
                else None,
            }
        )


class RepositoryAuthorizationInfoViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()
        repository = repository_authorization.repository

        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version__repository=repository,
            repository_version_language__repository_version__is_default=True,
        )
        serializer = repository.intents(queryset=queryset, version_default=True)

        return Response({"intents": serializer})


class RepositoryAuthorizationEvaluateViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository = repository_authorization.repository

        repository_version = request.query_params.get("repository_version")

        if repository_version:
            update = repository.get_specific_version_id(
                repository_version, str(request.query_params.get("language"))
            )
        else:
            update = repository.last_trained_update(
                str(request.query_params.get("language"))
            )

        return Response(
            {
                "update": False if update is None else True,
                "repository_version": update.pk,
                "language": update.language,
                "user_id": repository_authorization.user.pk,
                "algorithm": update.algorithm,
                "use_name_entities": update.use_name_entities,
                "use_competing_intents": update.use_competing_intents,
                "use_analyze_char": update.use_analyze_char,
            }
        )

    @action(detail=True, methods=["GET"], url_name="evaluations", lookup_field=[])
    def evaluations(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )
        evaluations = repository_update.repository_version.repository.evaluations(
            language=repository_update.language,
            queryset=RepositoryEvaluate.objects.filter(
                repository_version_language=repository_update
            ),
            version_default=repository_update.repository_version.is_default,
        )

        data = []

        for evaluate in evaluations:
            entities = []

            for evaluate_entity in evaluate.get_entities(repository_update.language):
                entities.append(
                    {
                        "start": evaluate_entity.start,
                        "end": evaluate_entity.end,
                        "value": evaluate.text[
                            evaluate_entity.start : evaluate_entity.end
                        ],
                        "entity": evaluate_entity.entity.value,
                    }
                )

            data.append(
                {
                    "text": evaluate.get_text(repository_update.language),
                    "intent": evaluate.intent,
                    "entities": entities,
                }
            )
        return Response(data)

    @action(detail=True, methods=["POST"], url_name="evaluate_results", lookup_field=[])
    def evaluate_results(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )

        intents_score = RepositoryEvaluateResultScore.objects.create(
            precision=request.data.get("intentprecision"),
            f1_score=request.data.get("intentf1_score"),
            accuracy=request.data.get("intentaccuracy"),
        )

        entities_score = RepositoryEvaluateResultScore.objects.create(
            precision=request.data.get("entityprecision"),
            f1_score=request.data.get("entityf1_score"),
            accuracy=request.data.get("entityaccuracy"),
        )

        evaluate_result = RepositoryEvaluateResult.objects.create(
            repository_version_language=repository_update,
            entity_results=entities_score,
            intent_results=intents_score,
            matrix_chart=request.data.get("matrix_chart"),
            confidence_chart=request.data.get("confidence_chart"),
            log=request.data.get("log"),
            cross_validation=request.data.get("cross_validation"),
        )

        return Response(
            {
                "evaluate_id": evaluate_result.id,
                "evaluate_version": evaluate_result.version,
            }
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="evaluate_results_intent",
        lookup_field=[],
    )
    def evaluate_results_intent(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        evaluate_result = get_object_or_404(
            RepositoryEvaluateResult, pk=request.data.get("evaluate_id")
        )

        intent_score = RepositoryEvaluateResultScore.objects.create(
            precision=request.data.get("precision"),
            recall=request.data.get("recall"),
            f1_score=request.data.get("f1_score"),
            support=request.data.get("support"),
        )

        RepositoryEvaluateResultIntent.objects.create(
            intent=request.data.get("intent_key"),
            evaluate_result=evaluate_result,
            score=intent_score,
        )

        return Response({})

    @action(
        detail=True,
        methods=["POST"],
        url_name="evaluate_results_score",
        lookup_field=[],
    )
    def evaluate_results_score(self, request, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        evaluate_result = get_object_or_404(
            RepositoryEvaluateResult, pk=request.data.get("evaluate_id")
        )

        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )

        entity_score = RepositoryEvaluateResultScore.objects.create(
            precision=request.data.get("precision"),
            recall=request.data.get("recall"),
            f1_score=request.data.get("f1_score"),
            support=request.data.get("support"),
        )

        RepositoryEvaluateResultEntity.objects.create(
            entity=RepositoryEntity.objects.get(
                repository_version=repository_update.repository_version,
                value=request.data.get("entity_key"),
                create_entity=False,
            ),
            evaluate_result=evaluate_result,
            score=entity_score,
        )

        return Response({})


class NLPLangsViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]

    def list(self, request, *args, **kwargs):
        return Response(
            {
                "english": [languages.LANGUAGE_EN],
                "portuguese": [languages.LANGUAGE_PT, languages.LANGUAGE_PT_BR],
                languages.LANGUAGE_PT: [languages.LANGUAGE_PT_BR],
                "pt-br": [languages.LANGUAGE_PT_BR],
                "br": [languages.LANGUAGE_PT_BR],
            }
        )


class RepositoryUpdateInterpretersViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet
):
    queryset = RepositoryVersionLanguage.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)

        update = self.get_object()
        rasa_version = request.query_params.get(
            "rasa_version", settings.BOTHUB_NLP_RASA_VERSION
        )
        no_bot_data = request.query_params.get("no_bot_data")

        validator = URLValidator()
        aws = False

        if no_bot_data:  # pragma: no cover
            return Response(
                {
                    "version_id": update.id,
                    "repository_uuid": update.repository_version.repository.uuid,
                    "total_training_end": update.total_training_end,
                    "language": update.language,
                    "from_aws": aws,
                }
            )

        try:
            validator(str(update.get_trainer(rasa_version).bot_data))
            bot_data = update.get_trainer(rasa_version).bot_data
            aws = True
        except ValidationError:
            bot_data = update.get_trainer(rasa_version).bot_data
        except Exception:
            bot_data = b""

        return Response(
            {
                "version_id": update.id,
                "repository_uuid": update.repository_version.repository.uuid,
                "total_training_end": update.total_training_end,
                "language": update.language,
                "bot_data": str(bot_data),
                "from_aws": aws,
            }
        )

    def create(self, request, *args, **kwargs):
        repository_authorization = check_auth(request)

        if not repository_authorization.can_contribute:
            raise PermissionDenied()

        id = request.data.get("id")
        rasa_version = request.data.get(
            "rasa_version", settings.BOTHUB_NLP_RASA_VERSION
        )
        repository = get_object_or_404(RepositoryVersionLanguage, pk=id)
        if settings.AWS_SEND:
            bot_data = base64.b64decode(request.data.get("bot_data"))
            repository.save_training(send_bot_data_file_aws(id, bot_data), rasa_version)
        else:
            repository.save_training(request.data.get("bot_data"), rasa_version)
        return Response({})


class RepositoryNLPLogsViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = RepositoryNLPLog.objects
    serializer_class = RepositoryNLPLogSerializer
    permission_classes = [AllowAny]
    authentication_classes = [NLPAuthentication]
