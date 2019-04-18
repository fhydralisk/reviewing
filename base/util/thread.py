import threading


class LocalThreadContextMixin(object):
    CTX_NAME = 'wl_local_context'

    def get_context_dict(self):
        context = getattr(threading.local(), self.CTX_NAME, None)
        if context is None:
            context = self.clean_context()

        return context

    def get_context(self, key):
        return self.get_context_dict()[key]

    def set_context(self, key, value):
        ctx = self.get_context_dict()
        ctx[key] = value
        return ctx

    def clean_context(self):
        ctx = dict()
        setattr(threading.local(), self.CTX_NAME, ctx)
        return ctx
