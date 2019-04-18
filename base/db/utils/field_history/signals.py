import django.dispatch


fields_changed = django.dispatch.Signal(
    providing_args=[
        "instance",
        "fields_changed",
        "created",
    ]
)
