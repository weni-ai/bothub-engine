from typing import List, Dict

import grpc
from django.conf import settings

from bothub.protos import project_pb2_grpc, project_pb2


class ConnectGRPCClient:
    def __init__(self):
        self.channel = self.get_channel()

    def get_channel(self):
        if settings.CONNECT_CERTIFICATE_GRPC_CRT:
            with open(settings.CONNECT_CERTIFICATE_GRPC_CRT, "rb") as f:
                credentials = grpc.ssl_channel_credentials(f.read())
            return grpc.secure_channel(settings.CONNECT_GRPC_SERVER_URL, credentials)
        return grpc.insecure_channel(settings.CONNECT_GRPC_SERVER_URL)

    def list_classifiers(self, project_uuid: str) -> List[Dict[str, str]]:
        result = []
        try:
            stub = project_pb2_grpc.ProjectControllerStub(self.channel)

            for project in stub.Classifier(
                project_pb2.ClassifierListRequest(project_uuid=project_uuid)
            ):
                result.append(
                    {
                        "authorization_uuid": project.authorization_uuid,
                        "classifier_type": project.classifier_type,
                        "name": project.name,
                    }
                )
        except grpc.RpcError as e:
            if e.code() is not grpc.StatusCode.NOT_FOUND:
                raise e
        return result

    def list_authorizations(self, project_uuid: str) -> List[str]:
        classifiers = self.list_classifiers(project_uuid=project_uuid)

        return [classifier.get("authorization_uuid") for classifier in classifiers]
