from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from bothub.common.models import (ZeroShotOptions)


class OptionZeroShotAPIView(APIView):

    queryset = ZeroShotOptions.objects

    def post(self, request):
        user = request.user
        data = request.data

        


