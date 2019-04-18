# coding=utf-8
from rest_framework import serializers
from rest_framework.fields import get_attribute
from .api import ReadonlySerializer


# A helper serializer for aggregations.
class AggregateListSerializer(ReadonlySerializer):
    aggregates = serializers.ListField(read_only=True)

    def __init__(self, child=None, *args, **kwargs):
        self.child = child

        super(AggregateListSerializer, self).__init__(*args, **kwargs)

    def get_real_instance(self, instance):
        return get_attribute(instance, ['instance'])

    def get_agg_op(self, instance):
        return get_attribute(instance, ['agg_op'])

    def child_serializer_from_op(self, real_instance, agg_op):
        raise NotImplementedError

    def get_aggregate_types_and_defaults(self, real_instance, agg_op):
        """

        :param real_instance: the real instance
        :param agg_op: aggregate operation
        :return: a dictionary: {field_name: (field_serializer, initial_value)}
        """
        raise NotImplementedError

    def resolve_child_type(self, real_instance, agg_op):
        child = self.child
        if child is None:
            child = self.child_serializer_from_op(real_instance, agg_op)

        return child

    def get_aggregate_field_name(self, field, real_instance, agg_op):
        return 'total_%s' % field

    def top_level_reduce(self, lhs, rhs):
        return lhs + rhs

    def to_representation(self, instance):

        agg_op = self.get_agg_op(instance)
        real_instance = self.get_real_instance(instance)
        child = self.resolve_child_type(real_instance, agg_op)

        transformed_instance = {
            'aggregates': real_instance
        }

        for field, (field_serializer, initial) in self.get_aggregate_types_and_defaults(real_instance, agg_op).items():
            transformed_instance[self.get_aggregate_field_name(field, real_instance, agg_op)] = initial
            self.fields[self.get_aggregate_field_name(field, real_instance, agg_op)] = field_serializer

        for obj in real_instance:
            for field in self.get_aggregate_types_and_defaults(real_instance, agg_op):
                value = get_attribute(obj, [field])
                transformed_instance[
                    self.get_aggregate_field_name(field, real_instance, agg_op)
                ] = self.top_level_reduce(
                    transformed_instance[
                        self.get_aggregate_field_name(field, real_instance, agg_op)
                    ],
                    value,
                )

        self.fields['aggregates'] = serializers.ListField(
            child=child,
        )

        return super(AggregateListSerializer, self).to_representation(transformed_instance)
