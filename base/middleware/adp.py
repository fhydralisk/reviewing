import logging

from django.conf import settings
from django.core.cache import caches, cache


logger = logging.getLogger(__name__)


class AntiDuplicatePostMiddleware(object):

    def __init__(self, get_response):
        self.post_uuid_key = getattr(settings, 'ANTI_DUP_POST_UUID_KEY', 'adp_uuid')
        cache_use = getattr(settings, 'ANTI_DUP_POST_CACHE_USE', None)
        if cache_use is not None:
            self.cache = caches[cache_use]
        else:
            self.cache = cache
        self.cache_appendix = getattr(settings, 'ANTI_DUP_POST_CACHE_APPENDIX', 'adp')
        self.process_methods = getattr(settings, 'ANTI_DUP_POST_PROCESS_METHODS', ['post', 'put', 'patch'])
        self.cache_duration = getattr(settings, 'ANTI_DUP_POST_CACHE_DURATION', 100)

        self.get_response = get_response

    def __call__(self, request):
        involved = request.method.lower() in self.process_methods and self.post_uuid_key in request.GET

        if involved:
            adp_uuid = "{}_{}".format(self.cache_appendix, request.GET[self.post_uuid_key])
            cached = self.cache.get(adp_uuid)
            if cached is not None:
                if cached['path'] == request.path:
                    logger.debug('ADPM: cache is involved.')
                    return cached['response']

        response = self.get_response(request)

        if involved:
            adp_uuid = "{}_{}".format(self.cache_appendix, request.GET[self.post_uuid_key])
            self.cache.set(adp_uuid, {'path': request.path, 'response': response}, self.cache_duration)

        return response
