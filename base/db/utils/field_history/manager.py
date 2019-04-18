import copy
from functools import partial
from django.db import models
from .signals import fields_changed


class ChangedFieldRecorder(object):
    def update_original(self, sender, instance, calc_changed, **kwargs):
        fields = instance._meta.fields
        original_value = {field.get_attname(): getattr(instance, field.get_attname()) for field in fields}
        fields_obj = getattr(instance, self.manager_name, None)
        if fields_obj is None:
            fields_obj = ChangedFields()
            setattr(instance, self.manager_name, fields_obj)
        fields_obj.update_original(original_value, calc_changed)
        if calc_changed:
            if fields_obj:
                fields_changed.send(
                    sender=sender,
                    instance=instance,
                    fields_changed=fields_obj,
                    created=kwargs.get('created', True),
                )

    def contribute_to_class(self, cls, name):
        self.manager_name = name
        self.module = cls.__module__
        self.cls = cls
        models.signals.class_prepared.connect(self.finalize, sender=cls, weak=False)

    def finalize(self, sender, **kwargs):
        models.signals.post_init.connect(partial(self.update_original, calc_changed=False), sender=sender, weak=False)
        models.signals.post_save.connect(partial(self.update_original, calc_changed=True), sender=sender, weak=False)


class ChangedFields(dict):
    def __init__(self, *args, **kwargs):
        self.original = dict()
        super(ChangedFields, self).__init__(*args, **kwargs)

    def update_original(self, original, calc_changed=True):
        if calc_changed:
            self.clear()
            for k, v in original.items():
                last_o = self.original.get(k, None)
                if v != last_o:
                    self[k] = (copy.copy(last_o), copy.copy(v))

        self.original.update(**original)
