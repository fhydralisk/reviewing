# coding=utf-8
from __future__ import unicode_literals

import logging

from base.funcs import MethodRoutedFuncClass
from base.util.db import update_instance_from_dict
from usersys.permissions import user as user_perms


logger = logging.getLogger(__name__)


class UserFunc(MethodRoutedFuncClass):
    PERMISSIONS = [
        user_perms.RequireUserIsLoginPermission(),
    ]

    def get(self, user, **kwargs):
        return {
            'user': user
        }

    def patch(self, user, update, **kwargs):
        old_password = update.get('old_password')
        new_password = update.get('password')
        if new_password is not None:
            user_perms.RequirePasswordMatchPermission().check(user=user, password=old_password, func=self, **kwargs)

        update_instance_from_dict(user, update, True)
