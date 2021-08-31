from .services import RepositoryService
from bothub.protos.inteligence import repository_pb2_grpc


def grpc_handlers(server):
    repository_pb2_grpc.add_RepositoryControllerServicer_to_server(
        RepositoryService.as_servicer(), server
    )
