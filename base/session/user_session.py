from django.utils.module_loading import import_string
from django.conf import settings


def _build_session_getter():
    module_name_session_getter = getattr(settings, 'WL_SESSION_GETTER', None)
    if module_name_session_getter is None:
        _session_getter = None
    else:
        _session_getter = import_string(module_name_session_getter)

    return _session_getter


session_getter = _build_session_getter()
