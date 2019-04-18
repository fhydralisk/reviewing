"""
Field Choice

Created by Hangyu Fan, May 5, 2018

Last modified: Mar 25, 2019
"""
import six
import copy


class FieldChoice(object):
    """
    Abstract class for describing the enumeration of model fields.
    """

    CHOICE_DISPLAY = (
        ('real_enum_data', 'verbose_name', 'PARAM_NAME'),
    )

    MAX_LENGTH = None

    def __init__(self):
        self.choice = self._build_django_choice()
        param_map = self._build_parameter_name()
        self._verbose_name_map = self._build_verbose_map()
        self._set_parameters(param_map)

        self._choice_values = [v[0] for v in self.CHOICE_DISPLAY]

    def _build_django_choice(self):
        return tuple(map(lambda x: (x[0], x[1]), self.CHOICE_DISPLAY))

    def _build_verbose_map(self):
        return dict(map(lambda x: (x[0], x[1]), self.CHOICE_DISPLAY))

    def _build_parameter_name(self):
        return dict(map(lambda x: (x[2], x[0]), self.CHOICE_DISPLAY))

    def _set_parameters(self, param_map):
        for k, v in param_map.items():
            self.__setattr__(k, v)

    def validate(self, v):
        return v in self._choice_values

    def get_choices(self):
        return list(self._choice_values)

    def get_verbose_name(self, choice):
        return six.text_type(self._verbose_name_map[choice])


class AbstractFieldChoiceSelection(object):
    def __init__(self, real_data, verbose_name=None, alias=None):
        self._real_data = real_data
        self._verbose_name = verbose_name
        if alias is not None and not isinstance(alias, six.string_types):
            raise TypeError("alias must be string.")
        self.alias = alias
        self.resolved = False

    def resolve_field(self, name, attr_name, bases, attrs, fields, resolved_by=None):
        if not self.resolved:
            if self._verbose_name is None:
                self._verbose_name = attr_name
            if self.alias is None:
                self.alias = attr_name.lower()
            self.resolved = True
        return self

    @property
    def real_data(self):
        raise NotImplementedError

    @property
    def verbose_name(self):
        return self._verbose_name

    @property
    def for_select(self):
        raise NotImplementedError


class FieldChoiceSelection(AbstractFieldChoiceSelection):

    ALLOWED_DATA_TYPES = six.string_types + six.integer_types

    def resolve_field(self, name, attr_name, bases, attrs, fields, resolved_by=None):
        if not isinstance(self._real_data, self.ALLOWED_DATA_TYPES):
            raise TypeError("Invalid data types.")

        self.alias = self.alias or attr_name

        for attr, field in fields.items():
            if attr != attr_name and field.for_select:
                if field.real_data == self.real_data:
                    raise ValueError("%s and %s have duplicated choice value %s" % (
                        attr, attr_name, str(self.real_data)
                    ))
                if field.resolved and field.alias == self.alias:
                    raise ValueError("%s and %s have duplicated alias value %s" % (
                        attr, attr_name, str(self.alias)
                    ))

        return super(FieldChoiceSelection, self).resolve_field(
            name, attr_name, bases, attrs, resolved_by
        )

    @property
    def real_data(self):
        return self._real_data

    @property
    def verbose_name(self):
        return self._verbose_name

    @property
    def for_select(self):
        return True


class SetFieldChoiceSelection(FieldChoiceSelection):
    ALLOWED_DATA_TYPES = (set, )


class FieldsetContainer(set):
    def __init__(self, fieldset, *args, **kwargs):
        self._fieldset = fieldset
        super(FieldsetContainer, self).__init__(*args, **kwargs)

    def __hash__(self):
        return tuple(self).__hash__()

    @property
    def sub_choice(self):
        if not hasattr(self, '_choice_instance'):
            attrs = {
                field_name: FieldChoiceSelection(
                    real_data=field.real_data,
                    verbose_name=field.verbose_name,
                    alias=field.alias,
                )
                for field_name, field in self._fieldset._fieldset_fields.items()
            }
            sub_choice_instance = FieldChoiceMetaclass(
                self._fieldset._attr_name + 'SubChoice',
                (FieldChoice2, ),
                attrs,
            )()
            self._choice_instance = sub_choice_instance

        return self._choice_instance


class Fieldset(AbstractFieldChoiceSelection):
    def __init__(self, real_data, *args, **kwargs):
        super(Fieldset, self).__init__(real_data, *args, **kwargs)
        self._real_data = None
        self._fieldset_fields = None
        # check real data
        if isinstance(real_data, (tuple, list, set)):
            self._data_unresolved = real_data
        elif isinstance(real_data, six.string_types):
            self._data_unresolved = [real_data]
        else:
            raise TypeError('real_data must be tuple, list, set or string.')

    def resolve_field(self, name, attr_name, bases, attrs, fields, resolved_by=None):

        if not self.resolved:
            if self._verbose_name is None:
                self._verbose_name = attr_name

            self._attr_name = attr_name

            if resolved_by is not None and self in resolved_by:
                raise RuntimeError(
                    "Field set contains cycling reference: %s->%s" % ("->".join(
                        list(map(lambda x: x.verbose_name, resolved_by))
                    ), self.verbose_name)
                )

            self._real_data = FieldsetContainer(fieldset=self)
            self._fieldset_fields = {}

            for s in self._data_unresolved:
                if s not in fields and s not in fields.values():
                    raise ValueError("%s is not a name or value of field." % s)
                if isinstance(s, six.string_types):
                    field_to_resolve = fields[s]
                    s_attr_name = s
                elif isinstance(s, AbstractFieldChoiceSelection):
                    field_to_resolve = s
                    s_attr_name = self.find_field_name(fields, s)
                else:
                    raise AssertionError('real data of fieldset must be string or field.')

                resolved_sub_field = field_to_resolve.resolve_field(
                    name, s_attr_name, bases, attrs, fields,
                    resolved_by=[self] if resolved_by is None else resolved_by + [self]
                )
                if resolved_sub_field.for_select:
                    self._real_data.add(resolved_sub_field.real_data)
                elif isinstance(resolved_sub_field, Fieldset):
                    self._real_data.update(resolved_sub_field.real_data)
                    self._fieldset_fields.update(**resolved_sub_field._fieldset_fields)
                else:
                    pass

                self._fieldset_fields[s_attr_name] = resolved_sub_field

        return super(Fieldset, self).resolve_field(name, attr_name, bases, attrs, fields, resolved_by)

    def find_field_name(self, fields, field):
        for k, v in fields.items():
            if v is field:
                return k

    @property
    def real_data(self):
        if self.resolved:
            return self._real_data
        else:
            raise RuntimeError("Fieldset is not resolved.")

    @property
    def for_select(self):
        return False

    @property
    def sub_choice(self):
        return self._real_data.sub_choice


FieldSet = Fieldset


class FieldChoiceMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        bases_reversed = reversed(bases)
        fields = reduce(
            lambda x1, x2: dict(x1, **x2),
            map(lambda x: copy.copy(x._fields) if isinstance(x, FieldChoiceMetaclass) else {}, bases_reversed)
        )
        choice_display = []
        params = {}
        for attr, obj in attrs.items():
            if isinstance(obj, AbstractFieldChoiceSelection):
                fields[attr] = attrs.pop(attr)

        field_alias_map = {}
        field_data_map = {}
        for attr_name, field in fields.items():  # type: (str, AbstractFieldChoiceSelection)
            field_resolved = field.resolve_field(name, attr_name, bases, attrs, fields)
            fields[attr_name] = field_resolved
            if field_resolved.for_select:
                choice_display.append((field_resolved.real_data, field_resolved.verbose_name, attr_name))
                field_data_map[field_resolved.real_data] = field_resolved
            if hasattr(field_resolved, 'alias'):
                field_alias_map[field_resolved.alias] = field_resolved
            params[attr_name] = field_resolved.real_data

        attrs['_fields'] = fields
        attrs['_field_alias'] = field_alias_map
        attrs['_field_data'] = field_data_map
        attrs['CHOICE_DISPLAY'] = choice_display
        attrs.update(**params)
        return super(FieldChoiceMetaclass, mcs).__new__(mcs, name, bases, attrs)


@six.add_metaclass(FieldChoiceMetaclass)
class FieldChoice2(FieldChoice):
    def get_verbose_name(self, choice, use_field_name=False):
        if use_field_name:
            return unicode(self._fields[choice].verbose_name)
        else:
            return super(FieldChoice2, self).get_verbose_name(choice)

    def get_alias_real_data(self, alias):
        return self._field_alias[alias].real_data

    def get_alias(self, data, use_field_name=False):
        """
        Get alias of data or field name
        :param data: data or field name
        :param use_field_name: if using field name, set this to true.
        :return: alias
        """
        if use_field_name:
            return self._fields[data].alias
        else:
            return self._field_data[data].alias

    @property
    def alias_choice(self):
        """
        Alias Choice Uses alias of each data field as the choice value.
        :return: the alias choice.
        """
        if hasattr(self, '_alias_choice_instance'):
            return self._alias_choice_instance
        else:
            attrs = {
                field_name: FieldChoiceSelection(
                    real_data=field.alias,
                    verbose_name=field.verbose_name,
                    alias=field.alias,
                )
                for field_name, field in self._fields.items()
                if isinstance(field, FieldChoiceSelection)
            }
            alias_choice_instance = FieldChoiceMetaclass(
                self.__class__.__name__ + 'AliasChoice',
                (FieldChoice2, ),
                attrs,
            )()
            self._alias_choice_instance = alias_choice_instance
            return alias_choice_instance

    def get_set_choice(self, fields=None):
        if fields is None:
            fields = [k for k, v in self._fields.items() if isinstance(v, Fieldset)]

        attrs = {}
        for field_name in fields:
            field = self._fields[field_name]
            attrs[field_name] = SetFieldChoiceSelection(
                real_data=field.real_data,
                verbose_name=field.verbose_name,
                alias=field.alias,
            )

        return FieldChoiceMetaclass(
            self.__class__.__name__ + 'SetChoice',
            (FieldChoice2,),
            attrs,
        )()
