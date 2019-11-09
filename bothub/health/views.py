from collections import OrderedDict
from functools import reduce

from django.http import HttpResponse
from rest_framework import status

from .checks import check_database_connection
from .checks import check_accessible_api

CHECKS = [check_database_connection, check_accessible_api]


def ping(request):
    checks_status = OrderedDict(
        map(lambda check: (check.__name__, check(request=request)), CHECKS)
    )
    healthy = reduce(
        lambda current, status: current and status, checks_status.values(), True
    )
    content = "{}\n{}".format(
        "OK" if healthy else "something wrong happened",
        "\n".join(map(lambda x: "{}: {}".format(*x), checks_status.items())),
    )
    status_code = status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return HttpResponse(content=content, content_type="text/plain", status=status_code)


def r200(request):
    return HttpResponse()
