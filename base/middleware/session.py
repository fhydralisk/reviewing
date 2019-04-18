import json
from importlib import import_module
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class WLSessionMiddleware(MiddlewareMixin):
    USER_SESSION_KEY = 'user_sid'
    POST_TYPES = {
        'POST', 'DELETE', 'PATCH', 'PUT'
    }

    def __init__(self, get_response=None):
        self.get_response = get_response
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def process_request(self, request):
        # Seek for user session
        session_key = request.GET.get(self.USER_SESSION_KEY, None)
        if session_key is None:
            try:
                if request.method in self.POST_TYPES and 'application/json' in request.META.get('CONTENT_TYPE', []):
                    body = json.loads(request.body.decode('utf-8'))
                    session_key = body.get(self.USER_SESSION_KEY) or body['data'].get(self.USER_SESSION_KEY)

            except (AttributeError, KeyError, ValueError):
                pass

        if session_key is not None:
            request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        return response
