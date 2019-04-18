from django.db import models


def get_model_class(obj):
    if isinstance(obj, models.Model):
        return obj.__class__
    elif isinstance(obj, type) and issubclass(obj, models.Model):
        return obj
    else:
        return None


def find_related_field(source, related, fk_name=None):
    """
    Find the foreign key name of related model to the source model.
    E.g.
        Model R --> r_to_b --> Model S
        Then find_related_object(S, R) will return "r_to_b"
    :return:
    """
    source_class = get_model_class(source)
    related_class = get_model_class(related)
    if source_class is None or related_class is None:
        raise TypeError("source or related must be instance or subclass of Model")

    remote_objects = list(filter(
        lambda o: o.related_model is related_class,
        source_class._meta.related_objects
    ))

    if len(remote_objects) == 0:
        raise AttributeError("%s has no relationship with %s" % (
            related_class.__name__,
            source_class.__name__,
        ))
    elif len(remote_objects) > 1:
        if fk_name is None:
            raise ValueError("Cannot determine relation between %s and %s" % (
                related_class.__name__,
                source_class.__name__
            ))
        else:
            if fk_name in map(lambda x: x.field.name, remote_objects):
                field_name = fk_name
            else:
                raise ValueError("%s is not a valid relation field between %s and %s" % (
                    fk_name,
                    related_class.__name__,
                    source_class.__name__
                ))
    else:
        if fk_name is None or fk_name == remote_objects[0].field.name:
            field_name = remote_objects[0].field.name
        else:
            raise ValueError("%s is not a valid relation field between %s and %s" % (
                fk_name,
                related_class.__name__,
                source_class.__name__
            ))

    return field_name
