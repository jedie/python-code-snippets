#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information
__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "JS-SHA-Login/-Logout"
__long_description__ = """The JS-SHA-Login handler"""

#_____________________________________________________________________________
# plugin administration data

plugin_manager_data = {
    "login" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "name"              : "input_username",
            "description"       : "Login Step-1: Username input form",
            "markup"            : None
        },
    },
    "_plaintext_login": { # Fake Methode, only for the internal page.
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "name"              : "plaintext_login",
            "description"       : "Login Step-2: input plaintext password",
            "markup"            : None
        },
    },
    "logout" : {
        "must_login"    : False,
        "must_admin"    : False,
    },


#    "insecure_login": {
#        "must_login"    : False,
#        "must_admin"    : False,
#        "internal_page_info" : {
#            "description"       : "insecure non-JS Login form",
#            "template_engine"   : "jinja",
#            "markup"            : None
#        },
#    },
#    "pass_reset_form" : {
#        "must_login"    : False,
#        "must_admin"    : False,
#        "internal_page_info" : {
#            "description"       : "The password reset html form page",
#            "template_engine"   : "jinja",
#            "markup"            : None
#        },
#    },
#    "check_pass_reset" : {
#        "must_login"    : False,
#        "must_admin"    : False,
#        "internal_page_info" : {
#            "name"              : "pass_reset_email",
#            "description"       : "The email with the password reset link",
#            "template_engine"   : "jinja",
#            "markup"            : None
#        },
#    },
#    "pass_reset" : {
#        "must_login"    : False,
#        "must_admin"    : False,
#    },
}
