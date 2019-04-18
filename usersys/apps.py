# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class UsersysConfig(AppConfig):
    name = 'usersys'
    verbose_name = _("用户管理")
