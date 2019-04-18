# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'base'
    verbose_name = _("架构")
