from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator, _lazy_re_compile


user_nickname_re = _lazy_re_compile(r'^[-a-zA-Z0-9_]+\Z')
validate_user_nickname = RegexValidator(
    user_nickname_re,
    _('Enter a valid \'nickname\' consisting of letters, numbers, ' +
        'underscores or hyphens.'),
    'invalid'
)


class UserManager(BaseUserManager):
    def _create_user(self, email, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        if not nickname:
            raise ValueError('The given nick must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, nickname, password, **extra_fields)

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, nickname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    email = models.EmailField(
        _('email'),
        unique=True,
        help_text=_('User\'s e-mail.'))
    name = models.CharField(
        _('name'),
        max_length=32,
        help_text=_('User\'s name.'))
    nickname = models.CharField(
        _('nickname'),
        max_length=16,
        validators=[validate_user_nickname],
        help_text=_('User\'s nickname, using letters, numbers, underscores ' +
                    'and hyphens without spaces.'))
    locale = models.CharField(
        _('locale'),
        max_length=48,
        help_text=_('User\'s locale.'))
    is_staff = models.BooleanField(
        _('staff status'),
        default=False)
    is_active = models.BooleanField(
        _('active'),
        default=True)
    joined_at = models.DateField(
        _('joined at'),
        auto_now_add=True)

    objects = UserManager()
