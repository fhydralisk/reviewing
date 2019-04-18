import urllib
import json
import logging
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseNotAllowed
from django.conf import settings
from django.http.response import HttpResponse, FileResponse
from base.exceptions import WLException
from base.util.serializer_helper import errors_summery
from base.funcs import AbstractFuncClass
from base.authentication import SessionAuthenticationWoCsrf


logger = logging.getLogger(__name__)


class WLAPIView(object):
    API_VERSION = "0.1"
    parser_classes = (JSONParser, )
    DEFAULT_VALIDATE_EXC_CODE = 400
    ERROR_HTTP_STATUS = False
    http_method_names = ['get', 'post', 'options']

    authentication_classes = [
        SessionAuthenticationWoCsrf
    ]

    def generate_response(self, data, context):
        return Response(data={
            "response": dict(
                {"result": 200},
                **data
            ),
            "version": self.API_VERSION,
            "context": context
        })

    def get_request_obj(self, request, method=None):
        if method is None:
            method = request.method

        if method in {"POST", "PUT", "PATCH"}:
            try:
                context = request.data.get("context", None)
                data = request.data["data"]
                return data, context
            except KeyError:
                raise WLException(code=400, message="Request format incorrect, data field is missing.")
        elif method in {"GET", "DELETE"}:
            objs = request.GET
            if "context" in objs:
                context = objs.pop("context")
                try:
                    context = json.loads(urllib.unquote(context))
                except ValueError:
                    context = None
            else:
                context = None

            data = objs
            return data, context
        else:
            raise WLException(code=500, message="Unexpected call of get request object method.")

    def validate_serializer(self, serializer, exc_code=None):

        if not serializer.is_valid():
            message = errors_summery(serializer)

            raise WLException(
                message=message,
                code=exc_code if exc_code is not None else self.DEFAULT_VALIDATE_EXC_CODE
            )

    def handle_exception(self, exc):
        if isinstance(exc, WLException):
            reason = exc.message
            code = exc.code
            if exc.code == 500:
                logger.exception("WLException 500", extra={"request": self.request})
            else:
                logger.warn("WLException: %d, %s" % (code, reason), extra={"request": self.request})
        elif isinstance(exc, MethodNotAllowed):
            return HttpResponseNotAllowed(self.http_method_names)
        else:
            if settings.DEBUG:
                reason = "%s %s" % (str(exc.__class__), str(exc))
            else:
                reason = "Internal Error"

            code = 500
            # Log the detailed exception
            logger.exception("Exception not handled", extra={"request": self.request})

        if self.ERROR_HTTP_STATUS:
            return HttpResponse(content=reason, status=code)
        else:
            return Response(data={
                "response": {
                    "result": code,
                    "reason": reason
                },
                "version": self.API_VERSION,
            })


class WLBinaryView(WLAPIView):

    ERROR_HTTP_STATUS = True

    def get(self, request):
        data, context = self.get_request_obj(request)

        io_stream, content_type = self.get_io_stream(data, context)

        return FileResponse(io_stream, content_type=content_type)

    def get_io_stream(self, data, context):
        """

        :param data:
        :param context:
        :return: BinaryIO, content_type
        """
        raise NotImplementedError


class WLAPIGenericView(WLAPIView, APIView):
    API_VERSION = "2.0"
    API_SERIALIZER = None
    RESULT_SERIALIZER = None
    FUNC_CLASS = None
    EXTRA_ARGS = None
    USE_VALIDATE_DATA = True
    USER_SESSION_KEY = 'user_sid'

    authentication_classes = [
        SessionAuthenticationWoCsrf
    ]

    def __init__(self, **kwargs):
        super(WLAPIGenericView, self).__init__(**kwargs)
        self._func = self.init_func_class()

    @staticmethod
    def _check_func_class(clz):
        if not issubclass(clz, AbstractFuncClass):
            raise TypeError("FUNC_CLASS must be subclass of AbstractFuncClass")

    def init_func_class(self):

        def check_and_return(c):
            self._check_func_class(c)
            return c

        set_http_methods = set(self.http_method_names)
        if isinstance(self.FUNC_CLASS, dict):
            class_dict = {
                k: v() for k, v in self.FUNC_CLASS.items() if k in set_http_methods and check_and_return(v) is not None
            }

            for method in set_http_methods:
                if method != "options" and method not in self.FUNC_CLASS:
                    raise KeyError("FUNC_CLASS dict must contain a key of %s" % method)

            return class_dict
        elif isinstance(self.FUNC_CLASS, type):
            self._check_func_class(self.FUNC_CLASS)
            fc = self.FUNC_CLASS()
            return {
                k: fc
                for k in set_http_methods if k != "options"
            }

    def __getattr__(self, item):
        if item == 'options':
            return self.options
        elif item in self.http_method_names:
            return self.proceed
        else:
            return super(WLAPIGenericView, self).__getattribute__(item)

    def get_user(self, request):
        user = getattr(request, 'user', None)
        if isinstance(user, AnonymousUser):
            user = None
        return user

    def get_args(self, request, data):
        api_serializer = self.get_api_serializer(request)
        if api_serializer is not None:
            serializer = api_serializer(data=data)
            self.validate_serializer(serializer)

            if self.USE_VALIDATE_DATA:
                args = serializer.validated_data
            else:
                args = serializer.data
        else:
            serializer = None
            args = {}

        extra_args = self.get_extra_args(request)

        if extra_args is not None:
            args = dict(args, **extra_args)

        return args, serializer

    def run_func(self, request, user, args, serializer):

        result = self._func[request.method.lower()](request, user, args, serializer)

        return result

    def generate_data(self, request, result):
        result_serializer = self.get_result_serializer(request)
        if result_serializer is not None:
            data = result_serializer(result).data
        elif isinstance(result, dict):
            data = result
        else:
            data = {}

        return data

    def http_response(self, request, result, data, context):
        return self.generate_response(
            data=data,
            context=context
        )

    def proceed(self, request):
        data, context = self.get_request_obj(request)

        user = self.get_user(request)

        args, serializer = self.get_args(request, data)

        result = self.run_func(request, user, args, serializer)

        data = self.generate_data(request, result)

        return self.http_response(request, result, data, context)

    def get_api_serializer(self, request):
        return self.determine_serializer(request, self.API_SERIALIZER)

    def get_result_serializer(self, request):
        return self.determine_serializer(request, self.RESULT_SERIALIZER)

    def get_extra_args(self, request):
        return self.EXTRA_ARGS

    @staticmethod
    def _request_method_to_serializer(request, serializer_dict):
        serializer = serializer_dict.get(request.method.lower())
        return serializer if callable(serializer) else None

    def determine_serializer(self, request, s):
        if callable(s):
            return s
        elif isinstance(s, dict):
            return self._request_method_to_serializer(request, s)
        else:
            return None
