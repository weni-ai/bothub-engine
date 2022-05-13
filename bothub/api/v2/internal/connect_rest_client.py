import requests
import json
from typing import List, Dict

from django.conf import settings


class ConnectRESTClient:
    def __init__(self):
        self.base_url = settings.CONNECT_API_URL
        self.headers = {"Content-Type": "application/json; charset: utf-8", "authorization": settings.KEYCLOAK_USER_TOKEN}

    def list_classifiers(
        self, project_uuid: str, user_email: str
    ) -> List[Dict[str, str]]:
        request = requests.get(
            url=f"{self.base_url}/v2/internal/classifiers",
            headers=self.headers,
            params={"project_uuid": project_uuid, "user_email": user_email},
        )

        return request.json()

    def list_authorizations(self, project_uuid: str) -> List[str]:
        classifiers = self.list_classifiers(project_uuid=project_uuid)

        return [classifier.get("authorization_uuid") for classifier in classifiers]

    def get_authorization_classifier(
        self, project_uuid: str, authorization_uuid: str
    ) -> str:
        """
        Recives a authorization UUID and returns the respective classifier UUID
        """
        classifiers = self.list_classifiers(project_uuid)
        classifier = filter(
            lambda classifier: classifier["authorization_uuid"] == authorization_uuid,
            classifiers,
        )

        return classifier.get("uuid")

    def remove_authorization(
        self, project_uuid: str, authorization_uuid: str, user_email: str
    ):
        classifier_uuid = self.get_authorization_classifier(
            project_uuid, authorization_uuid
        )
        request = requests.delete(
            url=f"{self.base_url}/v2/internal/authorization",
            headers=self.headers,
            json=json.dumps({"uuid": classifier_uuid, "user_email": user_email}),
        )

        return request.json()

    def create_classifier(self, **kwargs):
        request = requests.post(
            url=f"{self.base_url}/v2/internal/classifier/create",
            headers=self.headers,
            json=json.dumps({**kwargs, "classifier_type": "bothub"}),
        )
        return request.json()
