from bothub.api.grpc.organization.services import OrgService
from bothub.protos.inteligence import organization_pb2_grpc


def grpc_handlers(server):
    organization_pb2_grpc.add_OrgControllerServicer_to_server(
        OrgService.as_servicer(), server
    )
