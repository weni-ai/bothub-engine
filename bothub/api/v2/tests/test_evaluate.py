import json
from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status
from bothub.api.v2.evaluate.views import EvaluateViewSet, ResultsListViewSet
from bothub.common import languages
from bothub.common.models import (
    RepositoryExample,
    RepositoryVersion,
    RepositoryVersionLanguage,
    RepositoryIntent,
)
from bothub.common.models import Repository
from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateResultScore
from bothub.common.models import RepositoryEvaluateResult
from bothub.common.models import RepositoryEvaluateResultIntent
from bothub.common.models import RepositoryEvaluateResultEntity
from .utils import create_user_and_token


# TestCases


class ListEvaluateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_version
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        self.repository_evaluate = RepositoryEvaluate.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent="greet",
        )

    def request(self, token, version=None, language=None):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            f"/v2/evaluate/?repository_uuid={self.repository.uuid}"
            + (f"&repository_version={version}" if version else "")
            + (f"&language={language}" if language else ""),
            **authorization_header,
        )
        response = EvaluateViewSet.as_view({"get": "list"})(
            request, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)

        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_okay_language(self):
        repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_PT,
            algorithm="neural_network_internal",
        )

        RepositoryExample.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        RepositoryEvaluate.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent="greet",
        )

        RepositoryEvaluate.objects.create(
            repository_version_language=repository_version_language,
            text="test2",
            intent="greet",
        )
        response, content_data = self.request(
            self.owner_token, language=languages.LANGUAGE_PT
        )

        self.assertEqual(content_data["count"], 2)
        self.assertEqual(len(content_data["results"]), 2)
        self.assertEqual(
            content_data["results"][0].get("language"), languages.LANGUAGE_PT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_version(self):
        repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="new_test"
        )

        repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

        RepositoryExample.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        RepositoryEvaluate.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent="greet",
        )

        response, content_data = self.request(self.owner_token, repository_version.pk)

        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)
        self.assertEqual(
            content_data["results"][0].get("repository_version"), repository_version.pk
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NewEvaluateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_version
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/evaluate/?repository_uuid={}".format(self.repository.uuid),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = EvaluateViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_intent(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "intent": "",
                "entities": [],
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("intent", content_data)

    def test_entities_not_exists(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "repository_version": self.repository_version.pk,
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "intent": "greet",
                "entities": [{"entity": "hello", "start": 0, "end": 3}],
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("entities", content_data)

    def test_private_okay(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "intent": "greet",
                "entities": [],
            },
            self.token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_version(self):
        repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="new_test"
        )

        repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

        RepositoryExample.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        RepositoryEvaluate.objects.create(
            repository_version_language=repository_version_language,
            text="test",
            intent="greet",
        )

        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "intent": "greet",
                "entities": [],
                "repository_version": repository_version.pk,
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content_data.get("repository_version"), repository_version.pk)

    def test_exist_sentence(self):
        self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )

        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sentence_in_other_language(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "haha",
                "language": languages.LANGUAGE_PT,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EvaluateDestroyTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language="en",
            algorithm="neural_network_internal",
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_version
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        self.repository_evaluate = RepositoryEvaluate.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.delete(
            "/v2/evaluate/{}/?repository_uuid={}".format(
                self.repository_evaluate.id, self.repository.uuid
            ),
            **authorization_header,
        )
        response = EvaluateViewSet.as_view({"delete": "destroy"})(
            request,
            pk=self.repository_evaluate.id,
            repository_uuid=self.repository.uuid,
        )
        return response

    def test_okay(self):
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(self.token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.repository_evaluate.delete()
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EvaluateUpdateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language="en",
            algorithm="neural_network_internal",
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=self.repository_version
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        self.repository_evaluate = RepositoryEvaluate.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent="greet",
        )

    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.patch(
            "/v2/evaluate/{}/?repository_uuid={}".format(
                self.repository_evaluate.id, self.repository.uuid
            ),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = EvaluateViewSet.as_view({"patch": "update"})(
            request,
            pk=self.repository_evaluate.id,
            repository_uuid=self.repository.uuid,
        )
        response.render()
        content_data = json.loads(response.content)

        return (response, content_data)

    def test_okay(self):
        text = "testing"
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": text,
                "language": languages.LANGUAGE_EN,
                "repository_version": self.repository_version.pk,
                "intent": "greet",
                "entities": [],
            },
            self.owner_token,
        )
        self.assertEqual(content_data["text"], text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_okay(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "text": "testing",
                "language": languages.LANGUAGE_EN,
                "intent": "greet",
                "entities": [],
            },
            self.token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ListEvaluateResultTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        for x in range(0, 2):
            intent_results = RepositoryEvaluateResultScore.objects.create(
                f1_score=0.976, precision=0.978, accuracy=0.976
            )

            entity_results = RepositoryEvaluateResultScore.objects.create(
                f1_score=0.977, precision=0.978, accuracy=0.978
            )

            evaluate_log = [
                {
                    "text": "hey",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.9263743763408538,
                    },
                    "status": "success",
                },
                {
                    "text": "howdy",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.8099720606047796,
                    },
                    "status": "success",
                },
                {
                    "text": "hey there",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.8227075176309955,
                    },
                    "status": "success",
                },
                {
                    "text": "test with nlu",
                    "intent": "restaurant_search",
                    "intent_prediction": {
                        "name": "goodbye",
                        "confidence": 0.3875259420712092,
                    },
                    "status": "error",
                },
            ]

            sample_url = "https://s3.amazonaws.com/bothub-sample"
            evaluate_result = RepositoryEvaluateResult.objects.create(
                repository_version_language=self.repository.current_version(),
                intent_results=intent_results,
                entity_results=entity_results,
                matrix_chart="{}/confmat.png".format(sample_url),
                confidence_chart="{}/hist.png".format(sample_url),
                log=json.dumps(evaluate_log),
            )

            intent_score_1 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=1.0, f1_score=1.0, support=11
            )

            intent_score_2 = RepositoryEvaluateResultScore.objects.create(
                precision=0.89, recall=1.0, f1_score=0.94, support=8
            )

            intent_score_3 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=1.0, f1_score=1.0, support=8
            )

            intent_score_4 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.93, f1_score=0.97, support=15
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="affirm", score=intent_score_1
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="goodbye", score=intent_score_2
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="greet", score=intent_score_3
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result,
                intent="restaurant_search",
                score=intent_score_4,
            )

            entity_score_1 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.90, f1_score=0.95, support=10
            )

            entity_score_2 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.75, f1_score=0.86, support=8
            )

            RepositoryEvaluateResultEntity.objects.create(
                evaluate_result=evaluate_result, entity="cuisine", score=entity_score_1
            )

            RepositoryEvaluateResultEntity.objects.create(
                evaluate_result=evaluate_result, entity="greet", score=entity_score_2
            )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/evaluate/results/?repository_uuid={}".format(self.repository.uuid),
            **authorization_header,
        )
        response = ResultsListViewSet.as_view({"get": "list"})(
            request, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)
        self.assertEqual(content_data["count"], 2)
        self.assertEqual(len(content_data["results"]), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ListEvaluateResultTestFilterCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        intent_results = RepositoryEvaluateResultScore.objects.create(
            f1_score=0.976, precision=0.978, accuracy=0.976
        )

        entity_results = RepositoryEvaluateResultScore.objects.create(
            f1_score=0.977, precision=0.978, accuracy=0.978
        )

        evaluate_log = [
            {
                "text": "hey",
                "intent": "greet",
                "intent_prediction": {
                    "name": "greet",
                    "confidence": 0.9263743763408538,
                },
                "status": "success",
            },
            {
                "text": "howdy",
                "intent": "greet",
                "intent_prediction": {
                    "name": "greet",
                    "confidence": 0.8099720606047796,
                },
                "status": "success",
            },
            {
                "text": "hey there",
                "intent": "greet",
                "intent_prediction": {
                    "name": "greet",
                    "confidence": 0.8227075176309955,
                },
                "status": "success",
            },
            {
                "text": "test with nlu",
                "intent": "restaurant_search",
                "intent_prediction": {
                    "name": "goodbye",
                    "confidence": 0.3875259420712092,
                },
                "status": "error",
            },
        ]

        sample_url = "https://s3.amazonaws.com/bothub-sample"
        self.evaluate_result = RepositoryEvaluateResult.objects.create(
            repository_version_language=self.repository.current_version(),
            intent_results=intent_results,
            entity_results=entity_results,
            matrix_chart="{}/confmat.png".format(sample_url),
            confidence_chart="{}/hist.png".format(sample_url),
            log=json.dumps(evaluate_log),
        )

        intent_score_1 = RepositoryEvaluateResultScore.objects.create(
            precision=1.0, recall=1.0, f1_score=1.0, support=11
        )

        intent_score_2 = RepositoryEvaluateResultScore.objects.create(
            precision=0.89, recall=1.0, f1_score=0.94, support=8
        )

        intent_score_3 = RepositoryEvaluateResultScore.objects.create(
            precision=1.0, recall=1.0, f1_score=1.0, support=8
        )

        intent_score_4 = RepositoryEvaluateResultScore.objects.create(
            precision=1.0, recall=0.93, f1_score=0.97, support=15
        )

        RepositoryEvaluateResultIntent.objects.create(
            evaluate_result=self.evaluate_result, intent="affirm", score=intent_score_1
        )

        RepositoryEvaluateResultIntent.objects.create(
            evaluate_result=self.evaluate_result, intent="goodbye", score=intent_score_2
        )

        RepositoryEvaluateResultIntent.objects.create(
            evaluate_result=self.evaluate_result, intent="greet", score=intent_score_3
        )

        RepositoryEvaluateResultIntent.objects.create(
            evaluate_result=self.evaluate_result,
            intent="restaurant_search",
            score=intent_score_4,
        )

        entity_score_1 = RepositoryEvaluateResultScore.objects.create(
            precision=1.0, recall=0.90, f1_score=0.95, support=10
        )

        entity_score_2 = RepositoryEvaluateResultScore.objects.create(
            precision=1.0, recall=0.75, f1_score=0.86, support=8
        )

        RepositoryEvaluateResultEntity.objects.create(
            evaluate_result=self.evaluate_result, entity="cuisine", score=entity_score_1
        )

        RepositoryEvaluateResultEntity.objects.create(
            evaluate_result=self.evaluate_result, entity="greet", score=entity_score_2
        )

    def request(self, token, params):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/evaluate/results/{}/{}".format(self.evaluate_result.id, params),
            **authorization_header,
        )
        response = ResultsListViewSet.as_view({"get": "retrieve"})(
            request, pk=self.evaluate_result.id, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            self.owner_token, "?repository_uuid={}".format(self.repository.uuid)
        )
        self.assertEqual(len(content_data["log"]["results"]), 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_okay_intent_filter(self):
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&intent=greet&min=0&max=100".format(
                self.repository.uuid
            ),
        )
        self.assertEqual(len(content_data["log"]["results"]), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_okay_without_intent_filter(self):
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&min=0&max=100".format(self.repository.uuid),
        )
        self.assertEqual(len(content_data["log"]["results"]), 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_okay_range_without_intent_filter(self):
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&min=50&max=80".format(self.repository.uuid),
        )
        self.assertEqual(len(content_data["log"]["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_okay_range_with_intent_filter(self):
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&intent=greet&min=50&max=80".format(
                self.repository.uuid
            ),
        )
        self.assertEqual(len(content_data["log"]["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crossvalidation_false_filter(self):
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&cross_validation=False".format(self.repository.uuid),
        )
        self.assertEqual(content_data["cross_validation"], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crossvalidation_true_filter(self):
        intent_results = RepositoryEvaluateResultScore.objects.create(
            f1_score=0.976, precision=0.978, accuracy=0.976
        )
        entity_results = RepositoryEvaluateResultScore.objects.create(
            f1_score=0.977, precision=0.978, accuracy=0.978
        )
        self.evaluate_result = RepositoryEvaluateResult.objects.create(
            repository_version_language=self.repository.current_version(),
            intent_results=intent_results,
            entity_results=entity_results,
            cross_validation=True,
        )
        response, content_data = self.request(
            self.owner_token,
            "?repository_uuid={}&cross_validation={}".format(
                self.repository.uuid, True
            ),
        )
        self.assertEqual(content_data["cross_validation"], True)
        self.assertEqual(len(content_data["log"]["results"]), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompareEvaluateResultsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        for x in range(0, 2):
            intent_results = RepositoryEvaluateResultScore.objects.create(
                f1_score=0.976, precision=0.978, accuracy=0.976
            )

            entity_results = RepositoryEvaluateResultScore.objects.create(
                f1_score=0.977, precision=0.978, accuracy=0.978
            )

            evaluate_log = [
                {
                    "text": "hey",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.9263743763408538,
                    },
                    "status": "success",
                },
                {
                    "text": "howdy",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.8099720606047796,
                    },
                    "status": "success",
                },
                {
                    "text": "hey there",
                    "intent": "greet",
                    "intent_prediction": {
                        "name": "greet",
                        "confidence": 0.8227075176309955,
                    },
                    "status": "success",
                },
                {
                    "text": "test with nlu",
                    "intent": "restaurant_search",
                    "intent_prediction": {
                        "name": "goodbye",
                        "confidence": 0.3875259420712092,
                    },
                    "status": "error",
                },
            ]

            sample_url = "https://s3.amazonaws.com/bothub-sample"
            evaluate_result = RepositoryEvaluateResult.objects.create(
                repository_version_language=self.repository.current_version(),
                intent_results=intent_results,
                entity_results=entity_results,
                matrix_chart="{}/confmat.png".format(sample_url),
                confidence_chart="{}/hist.png".format(sample_url),
                log=json.dumps(evaluate_log),
            )

            intent_score_1 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=1.0, f1_score=1.0, support=11
            )

            intent_score_2 = RepositoryEvaluateResultScore.objects.create(
                precision=0.89, recall=1.0, f1_score=0.94, support=8
            )

            intent_score_3 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=1.0, f1_score=1.0, support=8
            )

            intent_score_4 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.93, f1_score=0.97, support=15
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="affirm", score=intent_score_1
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="goodbye", score=intent_score_2
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result, intent="greet", score=intent_score_3
            )

            RepositoryEvaluateResultIntent.objects.create(
                evaluate_result=evaluate_result,
                intent="restaurant_search",
                score=intent_score_4,
            )

            entity_score_1 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.90, f1_score=0.95, support=10
            )

            entity_score_2 = RepositoryEvaluateResultScore.objects.create(
                precision=1.0, recall=0.75, f1_score=0.86, support=8
            )

            RepositoryEvaluateResultEntity.objects.create(
                evaluate_result=evaluate_result, entity="cuisine", score=entity_score_1
            )

            RepositoryEvaluateResultEntity.objects.create(
                evaluate_result=evaluate_result, entity="greet", score=entity_score_2
            )

    def request(self, token):
        ids = f"{RepositoryEvaluateResult.objects.first().pk},{RepositoryEvaluateResult.objects.last().pk}"
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/evaluate/results/compare_results/?repository_uuid={}&ids={}".format(
                self.repository.uuid, ids
            ),
            **authorization_header,
        )
        response = ResultsListViewSet.as_view({"get": "compare_results"})(
            request, repository_uuid=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_compare_two_results(self):
        response, content_data = self.request(self.owner_token)
        self.assertEqual(
            RepositoryEvaluateResult.objects.last().pk, response.data[1].get("id")
        )
        self.assertEqual(
            RepositoryEvaluateResult.objects.first().pk, response.data[0].get("id")
        )
