import grpc

from bothub.protos import authentication_pb2_grpc, authentication_pb2

with grpc.insecure_channel('localhost:50051') as channel:
    # # Retriever User
    # stub = authentication_pb2_grpc.UserControllerStub(channel)
    # response = stub.Retrieve(authentication_pb2.UserRetrieveRequest(email="user@bothub.it"))
    # print(response)

    # Retriever User Permission
    stub = authentication_pb2_grpc.UserPermissionControllerStub(channel)
    response = stub.Retrieve(authentication_pb2.UserPermissionRetrieveRequest(org_id=3, user_email='user@bothub.it'))
    print(response)

    # # Update User Permission
    #
    # stub = authentication_pb2_grpc.UserPermissionControllerStub(channel)
    # response = stub.Update(
    #     authentication_pb2.UserPermissionUpdateRequest(
    #         org_id=3,
    #         user_email='user@bothub.it',
    #         permission=3
    #     )
    # )
    # print(response)

    # # Remove User Permission
    # stub = authentication_pb2_grpc.UserPermissionControllerStub(channel)
    # stub.Remove(
    #     authentication_pb2.UserPermissionRemoveRequest(
    #         org_id=3,
    #         user_email='user@bothub.it'
    #     )
    # )
