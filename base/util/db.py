"""
Database utilities
"""
import logging
from django.db.models import Model, QuerySet, Q, Manager
from django.db.models.signals import post_save, post_delete


default_logger = logging.getLogger(__name__)


def update_instance_from_dict(instance, dic, save=False):
    for k, v in dic.items():
        # Related Field cannot be found via hasattr(instance, k)
        if hasattr(instance, k) or hasattr(instance.__class__, k):
            if isinstance(v, dict):
                update_instance_from_dict(getattr(instance, k), v, save)
            else:
                setattr(instance, k, v)

    if save:
        instance.save()


def append_filter_to_qs(qs, filter_list, remove_none_filter=False):

    def append_filter(qs, filter_key, filter_value):
        # type: (QuerySet, str, object) -> QuerySet
        if filter_key.startswith('-'):
            qs = qs.exclude(**{filter_key[1:]: filter_value})
        else:
            qs = qs.filter(**{filter_key: filter_value})

        return qs

    if remove_none_filter:
        filter_list = [(k, v) for k, v in filter_list if v is not None]

    for k, v in filter_list:
        if isinstance(k, (str, unicode)):
            qs = append_filter(qs, k, v)
        elif isinstance(k, (tuple, list, set)):
            qs = qs.filter(
                reduce(
                    lambda a, b: a | b,
                    map(lambda key: Q(**{key: v}), k)
                )
            )
        else:
            raise TypeError("key of filter_list must be string or iterable")

    return qs


class LastLineConfigManager(object):

    CLZ_MODEL = None
    _instance = None
    cls_logger = None

    def __init__(self, reload_callback=None, logger=None):
        if not issubclass(self.CLZ_MODEL, Model):
            raise TypeError
        if callable(reload_callback):
            self.reload_callback = reload_callback
        elif reload_callback is not None:
            raise TypeError("reload callback must be None or callable")
        else:
            self.reload_callback = None

        if isinstance(logger, logging.Logger):
            self.cls_logger = logger
        elif logger is None:
            if self.cls_logger is None:
                self.cls_logger = default_logger
            else:
                if not isinstance(self.cls_logger, logging.Logger):
                    raise TypeError("logger must be a Logger class.")
        else:
            raise TypeError("logger must be a Logger class.")

        post_save.connect(self.reload, sender=self.CLZ_MODEL)
        post_delete.connect(self.reload, sender=self.CLZ_MODEL)

    def reload(self, **kwargs):
        self.cls_logger.info("%s is reloading due to signals" % self.CLZ_MODEL.__name__)
        self.do_load()
        if self.reload_callback is not None:
            self.reload_callback(self._instance)

    def do_load(self):
        try:
            self._instance = self.extra_filter(self.CLZ_MODEL.objects).last()
        except NotImplementedError:
            self._instance = self.CLZ_MODEL.objects.last()

    def extra_filter(self, qs):
        # type: (QuerySet) -> QuerySet
        raise NotImplementedError

    @property
    def instance(self):
        if self._instance is None:
            self.do_load()

        return self._instance


class UsedObjectManager(Manager):
    def get_queryset(self):
        return super(UsedObjectManager, self).get_queryset().filter(in_use=True)
