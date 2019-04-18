from rest_framework import serializers


class CurrencyField(serializers.DecimalField):

    def __init__(self, *args, **kwargs):
        max_digest = kwargs.pop('max_digits', 12)
        decimal_places = kwargs.pop('decimal_places', 3)
        super(CurrencyField, self).__init__(*args, max_digits=max_digest, decimal_places=decimal_places, **kwargs)


class QuantityField(serializers.DecimalField):

    def __init__(self, *args, **kwargs):
        max_digest = kwargs.pop('max_digits', 15)
        decimal_places = kwargs.pop('decimal_places', 6)
        super(QuantityField, self).__init__(*args, max_digits=max_digest, decimal_places=decimal_places, **kwargs)


class LatField(serializers.DecimalField):

    def __init__(self, *args, **kwargs):
        max_digest = kwargs.pop('max_digits', 10)
        decimal_places = kwargs.pop('decimal_places', 7)
        min_value = kwargs.pop('min_value', -90)
        max_value = kwargs.pop('max_value', 90)
        super(LatField, self).__init__(
            *args,
            max_digits=None,
            decimal_places=None,
            min_value=min_value,
            max_value=max_value,
            **kwargs
        )


class LngField(serializers.DecimalField):

    def __init__(self, *args, **kwargs):
        max_digest = kwargs.pop('max_digits', 10)
        decimal_places = kwargs.pop('decimal_places', 7)
        min_value = kwargs.pop('min_value', 0)
        max_value = kwargs.pop('max_value', 360)
        super(LngField, self).__init__(
            *args,
            max_digits=None,
            decimal_places=None,
            min_value=min_value,
            max_value=max_value,
            **kwargs
        )
