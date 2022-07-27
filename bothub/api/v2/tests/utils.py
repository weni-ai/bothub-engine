from bothub.utils import check_module_permission
from rest_framework.authtoken.models import Token

from bothub.authentication.models import User
from bothub.common import languages
from bothub.common.models import Repository


def create_user_and_token(nickname="fake", module=False):
    user = User.objects.create_user("{}@user.com".format(nickname), nickname)
    if module is True:
        check_module_permission({"can_communicate_internally": module}, user)
        user = User.objects.get(email=user.email)
    token, create = Token.objects.get_or_create(user=user)
    return (user, token)


def get_valid_mockups(categories):
    return [
        {
            "name": "Repository 1",
            "slug": "repository-1",
            "description": "",
            "language": languages.LANGUAGE_EN,
            "categories": [category.pk for category in categories],
        },
        {
            "name": "Repository 2",
            "description": "",
            "language": languages.LANGUAGE_PT,
            "categories": [category.pk for category in categories],
        },
    ]


def get_invalid_mockups(categories):
    return [
        {
            "name": "",
            "slug": "repository-1",
            "language": languages.LANGUAGE_EN,
            "categories": [category.pk for category in categories],
        },
        {
            "name": "Repository 3",
            "language": "out",
            "categories": [category.pk for category in categories],
            "is_private": False,
        },
    ]


def create_repository_from_mockup(owner, categories, **mockup):
    r = Repository.objects.create(owner_id=owner.id, **mockup)
    r.current_version()
    for category in categories:
        r.categories.add(category)
    return r
