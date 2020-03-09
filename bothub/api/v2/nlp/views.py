import base64

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from rest_framework import mixins, pagination
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from bothub.api.v2.repository.serializers import RepositorySerializer
from bothub.api.v2.nlp.serializers import NLPSerializer, RepositoryNLPLogSerializer
from bothub.authentication.models import User
from bothub.common.models import (
    RepositoryAuthorization,
    RepositoryVersionLanguage,
    RepositoryNLPLog,
)
from bothub.common.models import RepositoryEntity
from bothub.common.models import RepositoryEvaluateResult
from bothub.common.models import RepositoryEvaluateResultScore
from bothub.common.models import RepositoryEvaluateResultIntent
from bothub.common.models import RepositoryEvaluateResultEntity
from bothub.common.models import Repository
from bothub.common import languages
from bothub.utils import send_bot_data_file_aws


def check_auth(request):
    try:
        auth = request.META.get("HTTP_AUTHORIZATION").split()
        auth = auth[1]
        RepositoryAuthorization.objects.get(uuid=auth)
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

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()
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
            }
        )

    @action(detail=True, methods=["GET"], url_name="get_examples", lookup_field=[])
    def get_examples(self, request, **kwargs):
        check_auth(request)
        queryset = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )

        page = self.paginate_queryset(queryset.examples)

        examples = [
            {"example_id": example.id, "example_intent": example.intent}
            for example in page
        ]
        return self.get_paginated_response(examples)

    @action(
        detail=True, methods=["GET"], url_name="get_examples_labels", lookup_field=[]
    )
    def get_examples_labels(self, request, **kwargs):
        check_auth(request)
        queryset = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )

        page = self.paginate_queryset(
            queryset.examples.filter(entities__entity__label__isnull=False)
            .annotate(entities_count=models.Count("entities"))
            .filter(entities_count__gt=0)
        )

        label_examples_query = []

        for label_examples in page:
            label_examples_query.append({"example_id": label_examples.id})
        return self.get_paginated_response(label_examples_query)

    @action(detail=True, methods=["POST"], url_name="start_training", lookup_field=[])
    def start_training(self, request, **kwargs):
        check_auth(request)

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
                "ALGORITHM_STATISTICAL_MODEL": Repository.ALGORITHM_STATISTICAL_MODEL,
                "ALGORITHM_NEURAL_NETWORK_EXTERNAL": Repository.ALGORITHM_NEURAL_NETWORK_EXTERNAL,
            }
        )

    @action(
        detail=True,
        methods=["GET"],
        url_name="get_entities_and_labels",
        lookup_field=[],
    )
    def get_entities_and_labels(self, request, **kwargs):
        check_auth(request)

        try:
            examples = request.data.get("examples")
            label_examples_query = request.data.get("label_examples_query")
            update_id = request.data.get("repository_version")
        except ValueError:
            raise exceptions.NotFound()

        repository_update = RepositoryVersionLanguage.objects.get(pk=update_id)

        examples_return = []
        label_examples = []

        for example in examples:
            try:
                repository = repository_update.examples.get(
                    pk=example.get("example_id")
                )

                get_entities = repository.get_entities(
                    request.query_params.get("language")
                )

                get_text = repository.get_text(request.query_params.get("language"))

                examples_return.append(
                    {
                        "text": get_text,
                        "intent": example.get("example_intent"),
                        "entities": [entit.rasa_nlu_data for entit in get_entities],
                    }
                )

            except Exception:
                pass

        for example in label_examples_query:
            try:
                repository_examples = repository_update.examples.get(
                    pk=example.get("example_id")
                )

                entities = [
                    example_entity.get_rasa_nlu_data(label_as_entity=True)
                    for example_entity in filter(
                        lambda ee: ee.entity.label,
                        repository_examples.get_entities(
                            request.query_params.get("language")
                        ),
                    )
                ]

                label_examples.append(
                    {
                        "entities": entities,
                        "text": repository_examples.get_text(
                            request.query_params.get("language")
                        ),
                    }
                )
            except Exception:
                pass

        return Response({"examples": examples_return, "label_examples": label_examples})

    @action(detail=True, methods=["POST"], url_name="train_fail", lookup_field=[])
    def train_fail(self, request, **kwargs):
        check_auth(request)
        repository = get_object_or_404(
            RepositoryVersionLanguage, pk=request.data.get("repository_version")
        )
        repository.train_fail()
        return Response({})

    @action(detail=True, methods=["POST"], url_name="training_log", lookup_field=[])
    def training_log(self, request, **kwargs):
        check_auth(request)
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
                }
            )
        except Exception:
            return Response({}, status=400)

    @action(detail=True, methods=["GET"], url_name="repository_entity", lookup_field=[])
    def repository_entity(self, request, **kwargs):
        check_auth(request)
        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )
        repository_entity = get_object_or_404(
            RepositoryEntity,
            repository=repository_update.repository_version.repository,
            value=request.query_params.get("entity"),
        )

        return Response(
            {
                "label": True if repository_entity.label else False,
                "label_value": repository_entity.label.value
                if repository_entity.label
                else None,
            }
        )


class RepositoryAuthorizationInfoViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()
        repository = repository_authorization.repository
        serializer = RepositorySerializer(repository)
        return Response(serializer.data)


class RepositoryAuthorizationEvaluateViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = RepositoryAuthorization.objects
    serializer_class = NLPSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        repository_authorization = self.get_object()
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
                "repository_version": update.id,
                "language": update.language,
                "user_id": repository_authorization.user.id,
            }
        )

    @action(detail=True, methods=["GET"], url_name="evaluations", lookup_field=[])
    def evaluations(self, request, **kwargs):
        check_auth(request)
        repository_update = get_object_or_404(
            RepositoryVersionLanguage, pk=request.query_params.get("repository_version")
        )
        evaluations = repository_update.repository_version.repository.evaluations(
            language=repository_update.language
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
        check_auth(request)
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
        check_auth(request)

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
        check_auth(request)

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
                repository=repository_update.repository_version.repository,
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

    def retrieve(self, request, *args, **kwargs):
        check_auth(request)
        update = self.get_object()

        validator = URLValidator()

        aws = False

        try:
            validator(str(update.bot_data))
            bot_data = update.bot_data
            aws = True
        except ValidationError:
            bot_data = update.bot_data
        except Exception:
            bot_data = b""

        return Response(
            {
                "version_id": update.id,
                "repository_uuid": update.repository_version.repository.uuid,
                "bot_data": str(bot_data),
                "from_aws": aws,
            }
        )

    def create(self, request, *args, **kwargs):
        check_auth(request)
        id = request.data.get("id")
        repository = get_object_or_404(RepositoryVersionLanguage, pk=id)
        if settings.AWS_SEND:
            bot_data = base64.b64decode(request.data.get("bot_data"))
            repository.save_training(send_bot_data_file_aws(id, bot_data))
        else:
            repository.save_training(request.data.get("bot_data"))
        return Response({})


class RepositoryNLPLogsViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = RepositoryNLPLog.objects
    serializer_class = RepositoryNLPLogSerializer
    permission_classes = [AllowAny]
