from rest_framework import serializers


class PageApiSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=0, min_value=0)
    count_per_page = serializers.IntegerField(default=10, min_value=1, max_value=100)


class PagedListSerializerMixin(serializers.Serializer):
    n_pages = serializers.IntegerField()
