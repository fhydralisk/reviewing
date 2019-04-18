from django.test import TestCase

# Create your tests here.


from .. import serializers


class FlatSerializeMixinTest(TestCase):
    def test_flat_serialize_mixin(self):
        class InnerSerializer(serializers.Serializer):
            int_field = serializers.IntegerField()
            char_field = serializers.CharField()
            json_field = serializers.JSONField()
            list_field = serializers.ListField(
                child=serializers.IntegerField()
            )

        class TestOuterSerializer(serializers.Serializer):
            json_field = serializers.JSONField()
            int_field = serializers.IntegerField()
            inner_field = InnerSerializer()
            list_field = serializers.ListField(
                child=InnerSerializer()
            )
            many_field = InnerSerializer(many=True, source='many')

        TestSerializer = serializers.utils.transform_to_flat(TestOuterSerializer)

        json_field = {
            'inner_integer': 1,
            'inner_dict': {
                'inner_inner_integer': 2,
                'inner_inner_list': [1, 2, 3]
            },
            'inner_list': [1, 2, 3]
        }
        inner_instance = {
            'int_field': 1,
            'char_field': '1',
            'json_field': json_field,
            'list_field': [1, 2, 3]
        }
        instance = {
            'json_field': json_field,
            'int_field': 1,
            'inner_field': inner_instance,
            'list_field': [inner_instance, inner_instance],
            'many': [inner_instance, inner_instance]
        }

        test_serializer = TestSerializer(instance)
        test_result = test_serializer.data
        expected_data = {
            'inner_field__json_field__inner_list': [1, 2, 3],
            'int_field': 1,
            'inner_field__list_field': [1, 2, 3],
            'json_field__inner_dict__inner_inner_integer': 2,
            'inner_field__json_field__inner_dict__inner_inner_integer': 2,
            'inner_field__json_field__inner_dict__inner_inner_list': [1, 2, 3],
            'inner_field__json_field__inner_integer': 1,
            'inner_field__int_field': 1,
            'json_field__inner_list': [1, 2, 3],
            'json_field__inner_integer': 1,
            'many_field': [
                {
                    'int_field': 1,
                    'char_field': '1',
                    'json_field__inner_dict__inner_inner_integer': 2,
                    'json_field__inner_list': [1, 2, 3],
                    'json_field__inner_integer': 1,
                    'list_field': [1, 2, 3],
                    'json_field__inner_dict__inner_inner_list': [1, 2, 3]
                },
                {
                    'int_field': 1,
                    'char_field': '1',
                    'json_field__inner_dict__inner_inner_integer': 2,
                    'json_field__inner_list': [1, 2, 3],
                    'json_field__inner_integer': 1,
                    'list_field': [1, 2, 3],
                    'json_field__inner_dict__inner_inner_list': [1, 2, 3]
                }
            ],
            'list_field': [
                {
                    'int_field': 1,
                    'char_field': '1',
                    'json_field__inner_dict__inner_inner_integer': 2,
                    'json_field__inner_list': [1, 2, 3],
                    'json_field__inner_integer': 1,
                    'list_field': [1, 2, 3],
                    'json_field__inner_dict__inner_inner_list': [1, 2, 3]
                },
                {
                    'int_field': 1,
                    'char_field': '1',
                    'json_field__inner_dict__inner_inner_integer': 2,
                    'json_field__inner_list': [1, 2, 3],
                    'json_field__inner_integer': 1,
                    'list_field': [1, 2, 3],
                    'json_field__inner_dict__inner_inner_list': [1, 2, 3]
                }
            ],
            'inner_field__char_field': '1',
            'json_field__inner_dict__inner_inner_list': [1, 2, 3]
        }
        self.assertEqual(expected_data, test_result)
        test_deserializer = TestSerializer(data=test_result)
        test_deserializer.is_valid(raise_exception=True)
        self.assertEqual(test_deserializer.validated_data, instance)


class DynamicFieldsMixinTest(TestCase):
    @classmethod
    def setUpClass(cls):
        class TestInnerSerializer(serializers.DynamicFieldsMixin, serializers.Serializer):
            f1 = serializers.IntegerField()
            f2 = serializers.CharField()
            f3 = serializers.CharField()
            f4 = serializers.CharField()

            def __init__(self, *args, **kwargs):
                super(TestInnerSerializer, self).__init__(*args, **kwargs)

        class TestOuterSerializer(serializers.Serializer):
            inner = TestInnerSerializer()
            inner2 = TestInnerSerializer()
            f1 = serializers.IntegerField()
            f2 = serializers.CharField()
            f3 = serializers.IntegerField()
            f4 = serializers.CharField()

        class TestOuter2Serializer(serializers.DynamicFieldsMixin, serializers.Serializer):
            inner = TestInnerSerializer(fields=['f1', 'f3'])
            inner2 = TestInnerSerializer(exclude=['f1', 'f3'])
            f1 = serializers.IntegerField()
            f2 = serializers.CharField()
            f3 = serializers.IntegerField()
            f4 = serializers.CharField()

        cls.test_kwarg_serializer = TestOuter2Serializer
        cls.test_context_serializer = TestOuterSerializer
        cls.test_instance = {
            'f1': 1,
            'f2': '2',
            'f3': 3,
            'f4': '4',
            'inner': {
                'f1': 1,
                'f2': '2',
                'f3': '3',
                'f4': '4',
            },
            'inner2': {
                'f1': 1,
                'f2': '2',
                'f3': '3',
                'f4': '4',
            }
        }
        return super(DynamicFieldsMixinTest, cls).setUpClass()

    def test_kwargs(self):
        s1 = self.test_kwarg_serializer(self.test_instance, fields=['f1', 'f2'])
        self.assertIn('f1', s1.data)
        self.assertNotIn('f3', s1.data)
        s2 = self.test_kwarg_serializer(self.test_instance, fields=['inner', 'inner2'])
        self.assertIn('inner', s2.data)
        self.assertIn('inner2', s2.data)
        self.assertIn('f1', s2.data['inner'])
        self.assertNotIn('f2', s2.data['inner'])
        self.assertNotIn('f1', s2.data['inner2'])
        self.assertIn('f2', s2.data['inner2'])

    def test_context(self):
        s1 = self.test_context_serializer(self.test_instance)
        self.assertIn('f1', s1.data)
        self.assertIn('f2', s1.data)
        self.assertIn('f3', s1.data)
        self.assertIn('f4', s1.data)
        self.assertIn('inner', s1.data)

        s2 = serializers.utils.transform_to_dynamic_field(
            serializers.utils.partial_serializer(
                serializers.utils.partial_serializer(
                    self.test_context_serializer,
                    context={
                        'fields': ['f1', 'f2', 'inner', 'inner2'],
                    }
                ),
                context={
                    'inner.fields': ['f3', 'f4'],
                    'inner2.exclude': ['f1', 'f2'],
                }
            )
        )(self.test_instance)

        self.assertIn('f1', s2.data)
        self.assertIn('f2', s2.data)
        self.assertNotIn('f3', s2.data)
        self.assertIn('inner', s2.data)
        self.assertNotIn('f1', s2.data['inner'])
        self.assertNotIn('f2', s2.data['inner'])
        self.assertIn('f3', s2.data['inner'])
        self.assertIn('f4', s2.data['inner'])
        self.assertNotIn('f1', s2.data['inner2'])
        self.assertNotIn('f2', s2.data['inner2'])
        self.assertIn('f3', s2.data['inner2'])
        self.assertIn('f4', s2.data['inner2'])
