import requests
from typing import List, Dict

from django.conf import settings


class ConnectRESTClient:
    def __init__(self):
        self.base_url = settings.CONNECT_API_URL
        self.headers = {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": self.get_auth_token(),
        }

    def get_auth_token(self) -> str:
        request = requests.post(
            url=settings.OIDC_OP_TOKEN_ENDPOINT,
            data={
                "client_id": settings.OIDC_RP_CLIENT_ID,
                "client_secret": settings.OIDC_RP_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )
        token = request.json().get("access_token")
        return f"Bearer {token}"

    def list_classifiers(
        self, project_uuid: str, user_email: str
    ) -> List[Dict[str, str]]:
        params = {"user_email": user_email}
        if settings.USE_CONNECT_V2:
            suffix_url = f"v2/projects/{project_uuid}/list-classifier"
        else:
            suffix_url = "v1/organization/project/list_classifier/"
            params.update({"project_uuid": project_uuid})
        request = requests.get(
            url=f"{self.base_url}/{suffix_url}", headers=self.headers, params=params
        )

        return request.json()["data"]

    def list_authorizations(self, project_uuid: str, user_email: str) -> List[str]:
        classifiers = self.list_classifiers(
            project_uuid=project_uuid, user_email=user_email
        )

        return [classifier.get("authorization_uuid") for classifier in classifiers]

    def get_authorization_classifier(
        self, project_uuid: str, authorization_uuid: str, user_email: str
    ) -> str:
        """
        Recives a authorization UUID and returns the respective classifier UUID
        """
        classifiers = self.list_classifiers(project_uuid, user_email)
        classifier = filter(
            lambda classifier: classifier["authorization_uuid"] == authorization_uuid,
            classifiers,
        )

        return next(classifier).get("uuid")

    def remove_authorization(
        self, project_uuid: str, authorization_uuid: str, user_email: str
    ):
        classifier_uuid = self.get_authorization_classifier(
            project_uuid, authorization_uuid, user_email
        )

        if settings.USE_CONNECT_V2:
            suffix_url = f"v2/projects/{project_uuid}/delete-classifier"
        else:
            suffix_url = "v1/organization/project/destroy_classifier/"
        request = requests.delete(
            url=f"{self.base_url}/{suffix_url}",
            headers=self.headers,
            params={"uuid": classifier_uuid, "user_email": user_email},
        )

        return request.json()

    def create_classifier(self, **kwargs):
        project_uuid = kwargs.get("project_uuid")
        if settings.USE_CONNECT_V2:
            suffix_url = f"v2/projects/{project_uuid}/create-classifier"
        else:
            suffix_url = "v1/organization/project/create_classifier/"
        request = requests.post(
            url=f"{self.base_url}/{suffix_url}",
            headers=self.headers,
            params={**kwargs, "classifier_type": "bothub"},
        )
        return request.json()

    def create_recent_activity(self, recent_activity_data):
        requests.post(
            url=f"{self.base_url}/v1/recent-activity",
            headers=self.headers,
            json=recent_activity_data,
        )
