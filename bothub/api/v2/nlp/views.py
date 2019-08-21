import base64
from django.db import models
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny

from bothub.api.v2.repository.serializers import RepositorySerializer
from bothub.authentication.models import User
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryUpdate
from bothub.common.models import Repository
from bothub.common import languages


class RepositoryAuthorizationTrainViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        repository_authorization = self.get_object()
        current_update = repository_authorization.repository.current_update(
            str(request.query_params.get('language'))
        )

        data = {
            'ready_for_train':
                current_update.ready_for_train,
            'current_update_id':
                current_update.id,
            'repository_authorization_user_id':
                repository_authorization.user.id,
            'language':
                current_update.language
        }
        return Response(data)

    @action(
        detail=True,
        methods=['POST'],
        url_name='start_training',
        lookup_field=[])
    def starttraining(self, request, **kwargs):
        repository = RepositoryUpdate.objects.get(
            id=request.data.get('update_id')
        )
        examples = []
        for example in repository.examples:
            examples.append(
                {
                    'example_id': example.id,
                    'example_intent': example.intent
                }
            )
        repository.start_training(
            User.objects.get(id=request.data.get('by_user'))
        )

        label_examples_query = []

        for label_examples in repository.examples.filter(
                entities__entity__label__isnull=False
            ).annotate(
                entities_count=models.Count('entities')
            ).filter(
                entities_count__gt=0):
            label_examples_query.append(
                {
                    'example_id': label_examples.id
                }
            )

        data = {
            'language': repository.language,
            'update_id': repository.id,
            'repository_uuid': str(repository.repository.uuid),
            'examples': examples,
            'label_examples_query': label_examples_query,
            'intent': repository.intents,
            'algorithm': repository.algorithm,
            'use_name_entities': repository.use_name_entities,
            'use_competing_intents': repository.use_competing_intents,
            'ALGORITHM_STATISTICAL_MODEL':
                Repository.ALGORITHM_STATISTICAL_MODEL,
            'ALGORITHM_NEURAL_NETWORK_EXTERNAL':
                Repository.ALGORITHM_NEURAL_NETWORK_EXTERNAL
        }
        return Response(data)

    @action(
        detail=True,
        methods=['GET'],
        url_name='gettext',
        lookup_field=[])
    def gettext(self, request, **kwargs):
        repository = RepositoryUpdate.objects.get(
            id=request.query_params.get('update_id')
        ).examples.get(
            id=request.query_params.get('example_id')
        ).get_text(
            request.query_params.get('language')
        )

        data = {
            'get_text': repository
        }
        return Response(data)

    @action(
        detail=True,
        methods=['GET'],
        url_name='get_entities',
        lookup_field=[])
    def getentities(self, request, **kwargs):
        repository = RepositoryUpdate.objects.get(
            id=request.query_params.get('update_id')
        ).examples.get(
            id=request.query_params.get('example_id')
        ).get_entities(
            request.query_params.get('language')
        )

        entities = []

        for entit in repository:
            entities.append(entit.rasa_nlu_data)

        data = {
            'entities': entities,
        }
        return Response(data)

    @action(
        detail=True,
        methods=['GET'],
        url_name='get_entities_label',
        lookup_field=[])
    def getentitieslabel(self, request, **kwargs):
        repository = RepositoryUpdate.objects.get(
            id=request.query_params.get('update_id')
        ).examples.get(
            id=request.query_params.get('example_id')
        ).get_entities(
            request.query_params.get('language')
        )

        entities = []

        for example_entity in filter(lambda ee: ee.entity.label, repository):
            entities.append(
                example_entity.get_rasa_nlu_data(
                    label_as_entity=True
                )
            )

        data = {
            'entities': entities,
        }
        return Response(data)

    @action(
        detail=True,
        methods=['POST'],
        url_name='train_fail',
        lookup_field=[])
    def trainfail(self, request, **kwargs):
        RepositoryUpdate.objects.get(
            id=request.data.get('update_id')
        ).train_fail()
        return Response({})

    @action(
        detail=True,
        methods=['POST'],
        url_name='training_log',
        lookup_field=[])
    def traininglog(self, request, **kwargs):
        repository = RepositoryUpdate.objects.get(
            id=request.data.get('update_id')
        )
        repository.training_log = request.data.get('training_log')
        repository.save(update_fields=['training_log'])
        return Response({})


class RepositoryAuthorizationParseViewSet(
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        repository_authorization = self.get_object()
        repository = repository_authorization.repository
        update = repository.last_trained_update(
            str(request.query_params.get('language'))
        )
        data = {
            'update': False if update is None else True,
            'update_id': update.id,
            'language': update.language
        }
        return Response(data)


class RepositoryAuthorizationInfoViewSet(
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        repository_authorization = self.get_object()
        repository = repository_authorization.repository
        serializer = RepositorySerializer(repository)
        return Response(serializer.data)


class RepositoryAuthorizationEvaluateViewSet(
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        repository_authorization = self.get_object()
        repository = repository_authorization.repository
        update = repository.last_trained_update(
            str(request.query_params.get('language'))
        )
        data = {
            'update': False if update is None else True,
            'update_id': update.id,
            'language': update.language,
            'user_id': repository_authorization.user.id
        }
        return Response(data)


class NLPLangsViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        data = {
            'english': [
                languages.LANGUAGE_EN,
            ],
            'portuguese': [
                languages.LANGUAGE_PT,
                languages.LANGUAGE_PT_BR,
            ],
            languages.LANGUAGE_PT: [
                languages.LANGUAGE_PT_BR,
            ],
            'pt-br': [
                languages.LANGUAGE_PT_BR,
            ],
            'br': [
                languages.LANGUAGE_PT_BR,
            ],
        }
        return Response(data)


class RepositoryUpdateInterpretersViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryUpdate.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        update = self.get_object()
        data = {
            'update_id': update.id,
            'repository_uuid': update.repository.uuid,
            'bot_data': str(update.bot_data)
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        repository = self.queryset.get(pk=request.data.get('id'))
        bot_data = base64.b64decode(request.data.get('bot_data'))
        repository.save_training(bot_data)
        return Response({})
