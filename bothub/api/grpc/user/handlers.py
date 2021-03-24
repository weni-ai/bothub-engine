from bothub.api.grpc.user.services import UserPermissionService, UserService
from bothub.protos import authentication_pb2_grpc


def grpc_handlers(server):
    authentication_pb2_grpc.add_UserControllerServicer_to_server(
        UserService.as_servicer(), server
    )
    authentication_pb2_grpc.add_UserPermissionControllerServicer_to_server(
        UserPermissionService.as_servicer(), server
    )
