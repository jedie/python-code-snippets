
"""
A small page statistic middleware.

replace the >TAG< with some stats. But only in HTML pages.

Based on http://code.djangoproject.com/wiki/PageStatsMiddleware
"""

from django.core.cache import cache
CACHE_KEY = "page_cache"

class PageCache(object):
    def process_view(self, request, view_func, view_args, view_kwargs):

        if (not request.user.is_anonymous()) or view_func.func_name != "index":
            # Cache only for anonymous users the normal page view
            # start a uncached view
            response = view_func(request, *view_args, **view_kwargs)

            return response

        #______________________________________________________________________
        # Using caching

        url = view_args[0]
        cache_key = "%s_%s" % (CACHE_KEY, url)

        response = cache.get(cache_key)

        if response != None:
            # Cache hit
            print "Cached page response!"
            return response

        response = view_func(request, *view_args, **view_kwargs)
        cache.set(cache_key, response, 240)

        return response




