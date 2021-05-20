import grpc
from concurrent import futures
from django_grpc_framework.management.commands.grpcrunserver import (
    Command as BaseCommand,
)
from django_grpc_framework.settings import grpc_settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--server-key", dest="server_key", help="Server Key Certificate path"
        )
        parser.add_argument(
            "--server-crt", dest="server_crt", help="Server CTR Certificate path"
        )

    def handle(self, *args, **options):
        self.server_key = options["server_key"]
        self.server_crt = options["server_crt"]
        super().handle(*args, **options)

    def _serve(self):
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers),
            interceptors=grpc_settings.SERVER_INTERCEPTORS,
        )
        grpc_settings.ROOT_HANDLERS_HOOK(server)

        if self.server_crt and self.server_key:
            # read in key and certificate
            private_key = open(self.server_key, "rb").read()
            certificate_chain = open(self.server_crt, "rb").read()

            # create server credentials
            server_credentials = grpc.ssl_server_credentials(
                ((private_key, certificate_chain),)
            )

            # add secure port using crendentials
            server.add_secure_port(self.address, server_credentials)
        else:
            server.add_insecure_port(self.address)
        server.start()
        server.wait_for_termination()
