# coding=utf-8

import copy
from rest_framework import serializers


def set_deep_dict(root, key_tuple, value, dict_type=dict):
    # type: (dict, tuple, object, type) -> None
    assert(issubclass(dict_type, dict))
    p = root
    for key in key_tuple[:-1]:
        if key not in p:
            p[key] = dict_type()
        p = p[key]
    p[key_tuple[-1]] = value


class FlatSerializeMixin(serializers.BaseSerializer):
    splitter = '__'

    def to_internal_value(self, data):
        if self.context.get('flatten_api', True):
            data = self.reverse_flat_dict(data)

        return super(FlatSerializeMixin, self).to_internal_value(data)

    def reverse_flat_dict(self, data):
        # type: (dict) -> dict
        data_result = {}
        for k, v in data.items():
            if isinstance(v, list):
                v = self.reverse_flat_list(v)
            set_deep_dict(data_result, k.split(self.splitter), v, dict)

        return data_result

    def reverse_flat_list(self, data):
        # type: (list) -> list
        data_result = []
        for v in data:
            if isinstance(v, dict):
                v_dict = self.reverse_flat_dict(v)
                data_result.append(v_dict)
            elif isinstance(v, list):
                data_result.append(v)
            else:
                data_result.append(v)

        return data_result

    def to_representation(self, instance):
        rep = super(FlatSerializeMixin, self).to_representation(instance)
        if self.context.get('flatten', True):
            return self.flat_dict(rep)
        else:
            return rep

    def flat_dict(self, rep):
        # type: (dict) -> dict
        rep_result = {}
        for k, v in rep.items():
            if isinstance(v, dict):
                v_dict = self.flat_dict(v)
                for ks, vs in v_dict.items():
                    rep_result[
                        '{}{}{}'.format(k, self.splitter, ks)
                    ] = vs
            elif isinstance(v, list):
                v_list = self.flat_list(v)
                rep_result[k] = v_list
            else:
                rep_result[k] = v

        return rep_result

    def flat_list(self, rep):
        # type: (list) -> list
        rep_result = []
        for v in rep:
            if isinstance(v, dict):
                v_dict = self.flat_dict(v)
                rep_result.append(v_dict)
            elif isinstance(v, list):
                rep_result.append(v)
            else:
                rep_result.append(v)

        return rep_result


class DynamicFieldsMixin(serializers.BaseSerializer):

    DYNAMIC_FIELD_ARG_KEY = 'fields'
    DYNAMIC_EXCLUDE_ARG_KEY = 'exclude'
    DYNAMIC_FIELD_CONTEXT_KEY = 'fields'
    DYNAMIC_EXCLUDE_CONTEXT_KEY = 'exclude'
    CONTEXT_KEY_SPLITTER = '.'

    def filter_fields(self, fields):
        for field in self.fields.keys():
            if field not in fields:
                self.fields.pop(field)

    def exclude_fields(self, fields):
        for field in fields:
            if field in self.fields:
                self.fields.pop(field)

    def context_key(self, postfix):
        sources = [postfix]
        node = self
        while node:
            if node.source and node.parent is not None:
                sources.insert(0, node.source)
            node = node.parent
        return self.CONTEXT_KEY_SPLITTER.join(sources)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop(self.DYNAMIC_FIELD_ARG_KEY, None)
        exclude = kwargs.pop(self.DYNAMIC_EXCLUDE_ARG_KEY, None)

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        if fields is not None:
            self.filter_fields(fields)

        if exclude is not None:
            self.exclude_fields(exclude)

    def filter_field_context(self):
        if self.DYNAMIC_FIELD_CONTEXT_KEY:
            context_key = self.context_key(self.DYNAMIC_FIELD_CONTEXT_KEY)
            if context_key in self.context:
                self.filter_fields(self.context[context_key])

        if self.DYNAMIC_EXCLUDE_CONTEXT_KEY:
            context_key = self.context_key(self.DYNAMIC_EXCLUDE_CONTEXT_KEY)
            if context_key in self.context:
                self.exclude_fields(self.context[context_key])

    def to_representation(self, instance):
        self.filter_field_context()
        return super(DynamicFieldsMixin, self).to_representation(instance)

    def to_internal_value(self, data):
        self.filter_field_context()
        return super(DynamicFieldsMixin, self).to_internal_value(data)


class FakeRootMixin(object):
    @property
    def root(self):
        return self

    @property
    def parent(self):
        return None

    @parent.setter
    def parent(self, parent):
        pass


class PartialSerializerWrapper(object):
    fac_args = ()
    fac_kwargs = {}
    fac_args_sequence_partial_first = True
    fac_kwargs_partial_primary = False
    fac_kwargs_context_update = True

    @classmethod
    def update_args(cls, args, kwargs):
        kwargs = copy.copy(kwargs)
        if cls.fac_args_sequence_partial_first:
            cls.fac_args = cls.fac_args + args
        else:
            cls.fac_args = args + cls.fac_args

        if cls.fac_kwargs_context_update:
            if 'context' in kwargs and 'context' in cls.fac_kwargs:
                cls.fac_kwargs['context'] = dict(cls.fac_kwargs['context'], **kwargs.pop(str('context')))

        if cls.fac_kwargs_partial_primary:
            kwargs.update(cls.fac_kwargs)
            cls.fac_kwargs = kwargs
        else:
            cls.fac_kwargs = dict(cls.fac_kwargs, **kwargs)

    def update_args_init(self, args, kwargs):
        kwargs = copy.copy(kwargs)
        if self.fac_args_sequence_partial_first:
            self.fac_args = self.fac_args + args
        else:
            self.fac_args = args + self.fac_args

        if self.fac_kwargs_context_update:
            if 'context' in kwargs and 'context' in self.fac_kwargs:
                self.fac_kwargs['context'] = dict(self.fac_kwargs['context'], **kwargs.pop(str('context')))

        if self.fac_kwargs_partial_primary:
            kwargs.update(self.fac_kwargs)
            self.fac_kwargs = kwargs
        else:
            self.fac_kwargs = dict(self.fac_kwargs, **kwargs)

    def __init__(self, *args, **kwargs):
        self.update_args_init(args, kwargs)
        super(PartialSerializerWrapper, self).__init__(*self.fac_args, **self.fac_kwargs)


def partial_serializer(serializer, *args, **kwargs):
    # return functools.partial(serializer, *args, **kwargs)
    attrs = {
        'fac_args': args,
        'fac_kwargs': kwargs,
    }
    if issubclass(serializer, PartialSerializerWrapper):
        attrs_father = {
            'fac_args': copy.copy(serializer.fac_args),
            'fac_kwargs': copy.copy(serializer.fac_kwargs),
        }
        t = type('PartialWrapped' + serializer.__name__, (serializer, ), attrs_father)
        t.update_args(args, kwargs)
        return t
    else:
        return type('PartialWrapped' + serializer.__name__, (PartialSerializerWrapper, serializer), attrs)


def transform_to_flat(serializer):
    return type('Flatten' + serializer.__name__, (FlatSerializeMixin, serializer), {})


def transform_to_dynamic_field(serializer):
    # In some case the serializer class override its init method to remove some fields.
    # And it might be ambiguous with the behaviour of DynamicFieldsMixin.
    # So we here let the init function run after the serializer's __init__ with the following trick.
    return type(
        'Dynamic' + serializer.__name__,
        (serializer, type('DynamicFieldsMixinTemp', (DynamicFieldsMixin, ) + serializer.__bases__, {})),
        {}
    )


def make_fake_root(serializer):
    return type(
        'FakeRoot' + serializer.__name__,
        (serializer, FakeRootMixin),
        {}
    )
