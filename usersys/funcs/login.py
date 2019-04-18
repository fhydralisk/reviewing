# coding=utf-8
from __future__ import unicode_literals

import logging

from django.contrib.auth import authenticate
from base.funcs import AbstractFuncClass
from base.session.login import login
from ..permissions.user import RequireUserIsLoginPermission


logger = logging.getLogger(__name__)


class LoginFunc(AbstractFuncClass):
    def run(self, request, username, password, role, **kwargs):
        user = authenticate(internal_name=username, password=password)
        if user is not None and user.role != role:
            user = None

        kwargs['user'] = user
        RequireUserIsLoginPermission().check(request=request, func=self, **kwargs)

        session_key = login(request, user)
        return {
            'user_sid': session_key
        }
