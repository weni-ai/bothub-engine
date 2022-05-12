# import json

# from django.test import RequestFactory
# from django.test import TestCase, override_settings
# from django.test.client import MULTIPART_CONTENT
# from django.utils.translation import ugettext_lazy as _
# from rest_framework import status

# from bothub.authentication.models import User
# from bothub.common import languages
# from bothub.common.models import Repository
# from bothub.utils import create_user_and_token

# class InternalRepositoryListTestCase(TestCase):

#     def setUp(self):
#         self.factory = RequestFactory()

#         self.owner, self.owner_token = create_user_and_token("owner")

#         self.repository = Repository.objects.create(
#             owner=self.owner,
#             name="Testing",
#             slug="test",
#             language=languages.LANGUAGE_EN,
#         )

#         self.example_intent_1 = RepositoryIntent.objects.create(
#             text="bias",
#             repository_version=self.repository.current_version().repository_version,
#         )
#         self.example = RepositoryExample.objects.create(
#             repository_version_language=self.repository.current_version(),
#             text="hi",
#             intent=self.example_intent_1,
#         )

#         self.repository_auth = RepositoryAuthorization.objects.create(
#             user=self.owner, repository=self.repository, role=3
#         )


# InternalRepository

#     List
#         setup
#             user, token
#             fail_user, fail_token
#             repositories

#         testok >
#             GET with both user and module authorization
#             GET with name filter
#             GET with org_id filter
#             compare response to database query data that should be returned
#         testnotuser >
#             GET without user authorization
#         testnotmodule >
#             GET without module authorization
#         testwrong >
#             GET with module/user authorization that does not have permission on the repository


#     RetrieveAuthorization
#         testok >
#             GET with both user and module authorization
#             compare response to database query data that should be returned
#         testnotuser >
#             GET without user authorization
#         testnotmodule >
#             GET without module authorization
#         testwrong >
#             GET with module/user authorization that does not have permission on the repository
