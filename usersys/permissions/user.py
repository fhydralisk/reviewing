from base.funcs import AbstractPermission


class RequireUserIsLoginPermission(AbstractPermission):
    FAIL = {
        'code': 401,
        'message': 'User must login.'
    }

    def check_permission(self, func, request, user, serializer, **kwargs):
        return user is not None and user.is_active


class RequirePasswordMatchPermission(AbstractPermission):
    def check_permission(self, user, password, **kwargs):
        return user is not None and user.check_password(password)
