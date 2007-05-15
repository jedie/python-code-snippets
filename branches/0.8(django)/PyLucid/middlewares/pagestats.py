
"""
Based on http://code.djangoproject.com/wiki/PageStatsMiddleware

it used the old tag!
"""

from operator import add
from time import time
from django.db import connection

start_overall = time()

TAG = "<!-- script_duration -->"

FMT = (
    ' time: %(total_time).3f -'
    ' overall: %(overall_time).1f -'
    ' Queries: %(queries)d'
)

class PageStatsMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        start_time = time()

        # get number of db queries before we do anything
        old_quaries = len(connection.queries)

        # start the view
        response = view_func(request, *view_args, **view_kwargs)

        content = response.content

        # compute the db time for the queries just run
        queries = len(connection.queries) - old_quaries

        # replace the comment if found
        stat_info = FMT % {
            'total_time' : time() - start_time,
            'overall_time' : time() - start_overall,
            'queries' : queries,
        }
        mimetype = response.headers['Content-Type']
#        print mimetype
        if "html" in mimetype:
            content = content.replace(TAG, stat_info)
        else:
            content += "\n---\n%s\n" % stat_info

        response.content = content
        return response
