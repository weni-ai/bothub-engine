import grpc

from bothub.protos import organization_pb2_grpc, organization_pb2

with grpc.insecure_channel('localhost:50051') as channel:
    # List Organization
    stub = organization_pb2_grpc.OrgControllerStub(channel)
    for org in stub.List(organization_pb2.OrgListRequest(user_email='user@bothub.it')):
        print(org, end="")

    # # Crete Organization
    # stub = organization_pb2_grpc.OrgControllerStub(channel)
    # response = stub.Create(
    #     organization_pb2.OrgCreateRequest(
    #         name="Daniel",
    #         user_email='user@bothub.it'
    #     )
    # )
    # print(response)

    # Update Organization

    # stub = organization_pb2_grpc.OrgControllerStub(channel)
    # response = stub.Update(
    #     organization_pb2.OrgUpdateRequest(
    #         id=977,
    #         user_email='john.dalton@ilhasoft.com.br',
    #         name='Daniel KKKK'
    #     )
    # )
    # print(response)

    # Destroy Organization
    # stub = organization_pb2_grpc.OrgControllerStub(channel)
    # stub.Destroy(
    #     organization_pb2.OrgDestroyRequest(
    #         id=974,
    #         user_email='john.dalton@ilhasoft.com.br'
    #     )
    # )
