
"""
tests

Test PyLucid environment.
"""

def inspectdb(request):
    """
    django.core.management.instectdb
    """
    response = HttpResponse()
    response.write(HTML_head)
    response.write("<h1>inspectdb</h1>")
    response.write("<pre>")

    from django.core.management import inspectdb

    for line in inspectdb():
        response.write("%s\n" % line)

    response.write("</pre>")
    response.write(HTML_bottom)
    return response

def db_info():
    """
    Information about the database
    """
    pass