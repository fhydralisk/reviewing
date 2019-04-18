from importlib import import_module

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.timezone import now
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY


session_engine = import_module(settings.SESSION_ENGINE)


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backend = import_string(backend_path)()
        backends.append((backend, backend_path) if return_tuples else backend)

    return backends


def login(request, user, **extra):
    # type: (HttpRequest, UserBase, dict) -> six.string_types
    """
    Login modified from django
    """
    session_auth_hash = ''
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    session = session_engine.SessionStore()
    session.cycle_key()

    try:
        backend = user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    session[BACKEND_SESSION_KEY] = backend
    session[HASH_SESSION_KEY] = session_auth_hash
    session.update(extra)
    # saving into db or cache should be handled by session middleware.
    request.session = session

    user.last_login = now()
    user.save()
    # Rest framework use wrapped request that prevent us modifying the original request's session pointer.
    # So we check it here.
    if hasattr(request, '_request'):
        request._request.session = session
    return session.session_key


def logout(request):
    session = getattr(request, 'session', None)
    if session:
        session[HASH_SESSION_KEY] = ''
