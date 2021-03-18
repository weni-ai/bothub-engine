# import grpc
# import user_pb2_grpc, user_pb2
#
#
# # with grpc.insecure_channel('localhost:8002') as channel:
# with grpc.insecure_channel('flows-mumbai.weni.ai') as channel:
#     # Retriever User
#     stub = user_pb2_grpc.UserControllerStub(channel)
#     response = stub.Retrieve(user_pb2.UserRetrieveRequest(email="teste@teste.com"))
#     print(response)



import grpc
from bothub.protos import authentication_pb2_grpc, authentication_pb2


# read in certificate
with open('server.crt', 'rb') as f:
    trusted_certs = f.read()

# create credentials
credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

# with grpc.insecure_channel('grpc-development.bothub.it') as channel:
# with grpc.secure_channel('grpc-development.bothub.it', credentials) as channel:
with grpc.secure_channel('google-cloud-virginia-manager-development.bothub.it:8002', credentials) as channel:
    # Retriever User
    stub = authentication_pb2_grpc.UserControllerStub(channel)
    response = stub.Retrieve(authentication_pb2.UserRetrieveRequest(email="daniel.yohan@ilhasoft.com.br"))
    print(response)

    # # Retriever User Permission
    # stub = authentication_pb2_grpc.UserPermissionControllerStub(channel)
    # response = stub.Retrieve(authentication_pb2.UserPermissionRetrieveRequest(org_id=3, user_email='user@bothub.it'))
    # print(response)

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
