# coding=utf-8
from base.views import WLAPIGenericView
from ..funcs import login as login_funcs
from ..serializers import login as login_serializers


class LoginView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    API_SERIALIZER = login_serializers.LoginApiSerializer
    FUNC_CLASS = login_funcs.LoginFunc
