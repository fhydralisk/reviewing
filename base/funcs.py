# coding=utf_8

from django.db import transaction
from django.contrib.auth import get_user_model
from base.exceptions import WLException
from base.util.pages import get_page_info
from base.util.thread import LocalThreadContextMixin


class AbstractPermission(LocalThreadContextMixin):
    FAIL = {"code": 401, "message": "Permission Denied"}
    EXCEPTION = WLException

    def fail(self):
        raise self.EXCEPTION(**self.FAIL)

    def check(self, func, request, user, serializer, **kwargs):
        if not self.check_permission(func=func, request=request, user=user, serializer=serializer, **kwargs):
            self.fail()

    def check_permission(self, func, request, user, serializer, **kwargs):
        raise NotImplementedError

    def __or__(self, other):
        return LogicOrPermissions((self, other))


class ConditionalPermission(AbstractPermission):

    def __init__(self, cond_func, permission):
        if callable(cond_func):
            self._cond_func = cond_func
        else:
            raise TypeError("cond_func of Conditional Permission must be callable.")

        self._permission = permission

    def check(self, **kwargs):
        if self._cond_func(**kwargs):
            self._permission.check(**kwargs)
        else:
            pass

    def check_permission(self, func, request, user, serializer, **kwargs):
        # Do nothing because we override check method.
        pass


class LogicOrPermissions(AbstractPermission):
    def __init__(self, permissions):
        if isinstance(permissions, (list, tuple, set)):
            self._permissions = list(permissions)
        else:
            raise TypeError("permissions must be list, tuple or set")

    def check(self, **kwargs):
        last_exc = None
        for perm in self._permissions:
            try:
                perm.check(**kwargs)
            except perm.EXCEPTION as e:
                last_exc = e
            else:
                return

        raise last_exc

    def check_permission(self, func, request, user, serializer, **kwargs):
        # Do nothing because we override check method.
        pass


class RequireUserLoginPermission(AbstractPermission):
    FAIL = {
        "code": 404,
        "message": u"用户不存在或未登录"
    }

    def check_permission(self, func, request, user, **kwargs):
        return isinstance(user, get_user_model()) and user.is_active


class AbstractFuncClass(LocalThreadContextMixin):
    PERMISSIONS = []
    DB_TRANSACTION = False

    def __call__(self, request, user, kwargs, serializer):
        def real_call():
            self.check_permission(request=request, user=user, serializer=serializer, kwargs=kwargs)
            return self.run(request=request, user=user, serializer=serializer, **kwargs)

        self.clean_context()
        if self.DB_TRANSACTION:
            with transaction.atomic():
                return real_call()
        else:
            return real_call()

    def get_permissions(self, request, user, serializer, kwargs):
        return self.PERMISSIONS

    def check_permission(self, request, user, serializer, kwargs):
        for permission in self.get_permissions(request=request, user=user, serializer=serializer, kwargs=kwargs):
            permission.check(func=self, request=request, user=user, serializer=serializer, **kwargs)

    def run(self, request, user, serializer, **kwargs):
        raise NotImplementedError


class MethodRoutedFuncClass(AbstractFuncClass):

    def __init__(self, *args, **kwargs):
        self._cached_permission_dict = {}
        super(MethodRoutedFuncClass, self).__init__(*args, **kwargs)

    def get_permissions_for_method(self, method):
        perms = []
        for perm in self.PERMISSIONS:
            if isinstance(perm, (tuple, list)):
                if perm[0] == method:
                    perms.append(perm[1])
            else:
                perms.append(perm)
        return perms

    def get_permissions(self, request, user, serializer, kwargs):
        method = request.method.lower()
        if method not in self._cached_permission_dict:
            self._cached_permission_dict[method] = \
                self.get_permissions_for_method(method)

        return self._cached_permission_dict[method]

    def run(self, request, user, serializer, **kwargs):
        func = getattr(self, request.method.lower(), None)
        if callable(func):
            return func(request=request, user=user, serializer=serializer, **kwargs)
        else:
            raise AssertionError("Method {} not implemented.".format(request.method.lower()))


class PagedAbstractFuncClass(AbstractFuncClass):
    def run(self, page, count_per_page, **kwargs):
        qs, field_name, extra = self.get_paged_qs(page=page, count_per_page=count_per_page, **kwargs)

        if extra is None:
            extra = {}

        start, end, n_pages = get_page_info(
            qs, count_per_page, page,
            index_error_excepiton=self.out_of_range_exception(page=page, count_per_page=count_per_page, **kwargs)
        )
        qs_paged = qs[start:end]
        qs_transformed = self.transform_queryset(qs_paged, page=page, count_per_page=count_per_page, **kwargs)
        return dict({
            field_name: [
                self.transform_element(obj, page=page, count_per_page=count_per_page, **kwargs)
                for obj in qs_transformed
            ],
            'n_pages': n_pages,
        }, **extra)

    def get_paged_qs(self, **kwargs):
        """

        :param kwargs:
        :return: queryset, field name, extra fields.
        """
        raise NotImplementedError

    def out_of_range_exception(self, **kwargs):
        return WLException(400, u"页码超出范围")

    def transform_element(self, obj, **kwargs):
        return obj

    def transform_queryset(self, queryset, **kwargs):
        return queryset
