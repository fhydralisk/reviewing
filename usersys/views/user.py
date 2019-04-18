from base.views import WLAPIGenericView
from ..serializers import user as user_serializers
from ..funcs import user as user_funcs


class UserView(WLAPIGenericView):
    http_method_names = ['get', 'patch', 'options']
    API_SERIALIZER = {
        'patch': user_serializers.UserPartialUpdateSerializer
    }
    RESULT_SERIALIZER = {
        'get': user_serializers.UserDetailSerializer
    }
    FUNC_CLASS = user_funcs.UserFunc
