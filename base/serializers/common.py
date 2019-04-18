"""
Common serializer utilities
"""


class NotSpecified(object):
    pass


class SearchContextMixin(object):

    def node_context_iterator(self):
        node = self
        while node:
            yield node._context
            node = node.parent

        raise StopIteration

    def search_context(self, field, default=NotSpecified, reverse=False):

        if not reverse:
            for ctx in self.node_context_iterator():
                if field in ctx:
                    return ctx[field]
        else:
            for ctx in reversed(list(self.node_context_iterator())):
                if field in ctx:
                    return ctx[field]

        if default is NotSpecified:
            raise LookupError
        else:
            return default
