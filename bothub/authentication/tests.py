from django.test import TestCase

from .models import User

class AuthenticationTestCase(TestCase):
    def test_new_user(self):
        User.objects.create_user('fake@user.com', 'fake')
    
    def test_new_superuser(self):
        User.objects.create_superuser('fake@user.com', 'fake')
    
    def test_new_user_fail_without_email(self):
        with self.assertRaises(ValueError):
            User.objects._create_user('', 'fake')
    
    def test_new_user_fail_without_nick(self):
        with self.assertRaises(ValueError):
            User.objects._create_user('fake@user.com', '')
    
    def test_new_superuser_fail_issuperuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser('fake@user.com', 'fake', is_superuser=False)
