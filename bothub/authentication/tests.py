from django.test import TestCase
from django.db import IntegrityError

from .models import User


class AuthenticationTestCase(TestCase):
    def test_new_user(self):
        User.objects.create_user("fake@user.com", "fake")

    def test_new_superuser(self):
        User.objects.create_superuser("fake@user.com", "fake")

    def test_new_user_fail_without_email(self):
        with self.assertRaises(ValueError):
            User.objects._create_user("", "fake")

    def test_new_user_fail_without_nickname(self):
        with self.assertRaises(ValueError):
            User.objects._create_user("fake@user.com", "")

    def test_new_superuser_fail_issuperuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser("fake@user.com", "fake", is_superuser=False)

    def test_user_unique_nickname(self):
        User.objects.create_user("user1@user.com", "fake")
        with self.assertRaises(IntegrityError):
            User.objects.create_user("user2@user.com", "fake")
