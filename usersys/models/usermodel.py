# coding=UTF-8
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager

from base.util.misc_validators import validators
from usersys.choices import user_role_choice


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, internal_name, password, **extra_fields):
        if internal_name is None:
            raise ValueError('The openid must be set')

        user = self.model(internal_name=internal_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, internal_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(internal_name, password, **extra_fields)

    def create_superuser(self, internal_name, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(internal_name, password, **extra_fields)

    def set_password(self, internal_name, password):
        user = self.get(internal_name=internal_name)
        user.set_password(password)
        return user


class UserBase(AbstractBaseUser, PermissionsMixin):
    internal_name = models.CharField(_("内部登录名称"), max_length=64, unique=True)
    pn = models.CharField(_('电话号码'), max_length=25, null=True, validators=[
        validators.get_validator("phone number")
    ])
    is_active = models.BooleanField(default=True, verbose_name=_("是否在用"))
    is_staff = models.BooleanField(default=False, verbose_name=_("是否为管理者"))
    role = models.IntegerField(_("用户角色"), choices=user_role_choice.choice)
    registered_date = models.DateTimeField(_("注册时间"), auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'internal_name'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('用户管理')
        verbose_name_plural = _('用户管理')

    def get_short_name(self):
        return u"{} - {}".format(self.internal_name, self.pn)

    def get_full_name(self):
        return u"{} - {}".format(self.internal_name, self.pn)

    def __unicode__(self):
        return self.pn or self.internal_name

