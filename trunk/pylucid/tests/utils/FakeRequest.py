#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   PyLucid.tests.utils.FakeRequest
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Helper functions for creating fake request objects.

   :copyright: 2007 by the PyLucid team.
   :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Fake PyLucid Environment

class FakePageMsg(object):
    def __call__(self, *msg):
        for line in msg:
            print line

class FakeUser(object):
    def is_anonymous(self):
        return True

class FakeRequest(object):
    __fake_http_host = "unitest_HTTP_HOST_fake"
    user = FakeUser()
    META = {"HTTP_HOST": __fake_http_host,}
    debug = True
    def get_host(self):
        """
        django's request.get_host()
        http://www.djangoproject.com/documentation/request_response/#id1
          Returns the originating host of the request using information from
          the HTTP_X_FORWARDED_HOST and HTTP_HOST headers (in that order). If
          they don’t provide a value, the method uses a combination of
          SERVER_NAME and SERVER_PORT as detailed in PEP 333.
        Example: "127.0.0.1:8000"
        """
        return self.__fake_http_host

class FakePage(object):
    id = 1

fakeURLs = {
    "absoluteIndex": "/",
}

#response = sys.stdout
def get_fake_context(page_object=None):
    if not page_object:
        from PyLucid.models import Page
        try:
            page_object = Page.objects.get(id=1)
        except Exception:
            # Does only works, if the PyLucid dump inserted to the database
            page_object = FakePage()

    fake_context = {
        "request": FakeRequest(),
        "page_msg": FakePageMsg(),
        "URLs": fakeURLs,
        "PAGE": page_object,
        "CSS_ID_list": [],

    }

    return fake_context
