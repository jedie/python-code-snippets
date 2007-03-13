
"""
Based on http://code.djangoproject.com/wiki/PageStatsMiddleware
"""

from operator import add
from time import time
from django.db import connection

from PyLucid.system.response import PyLucidResponse

start_overall = time()

TAG = "script_duration"

FMT = (
    ' time: %(total_time).3f -'
    ' overall: %(overall_time).1f -'
    ' Queries: %(queries)d'
)

class PageStatsMiddleware(object):
    def __init__(self):
        self.bla = 1

    def process_view(self, request, view_func, view_args, view_kwargs):
        start_time = time()

        # get number of db queries before we do anything
        old_quaries = len(connection.queries)
        
        # time the view
        response = view_func(request, *view_args, **view_kwargs)
        
        if isinstance(response, PyLucidResponse):
            # compute the db time for the queries just run
            queries = len(connection.queries) - old_quaries
    
            # replace the comment if found
            if response and response.content:
                stat_info = FMT % {
                    'total_time' : time() - start_time,
                    'overall_time' : time() - start_overall,
                    'queries' : queries,
                }
                try:
                    response.replace_tag(TAG, stat_info)
                except KeyError:
                    # _install section
                    mimetype = response.headers['Content-Type']
                    if mimetype == "text/html":
                        info = "\n<hr /><small><p>%s</p></small>\n" % stat_info
                    else:
                        info = "\n---\n%s\n" % stat_info
                    response.write(info)

        return response
