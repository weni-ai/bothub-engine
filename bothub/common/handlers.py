from bothub.common.services import RepositoryService
from bothub.protos import common_pb2_grpc


def grpc_handlers(server):
    common_pb2_grpc.add_RepositoryControllerServicer_to_server(
        RepositoryService.as_servicer(), server
    )
