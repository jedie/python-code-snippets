
"""
get_urls() for appending _install section views.
"""

import inspect

#~ from django.conf.urls.defaults import *

from PyLucid import install as install_package


def get_members(obj, predicate, skip_names=[]):
    """
    filtered inspect.getmembers() with predicate
    """
    member_list = inspect.getmembers(obj, predicate)
    member_list = [i for i in member_list if i[0] not in skip_names]
    return member_list


def get_urls(base_url):
    """
    generate the django urlpatterns for all install views.
    """
    module_list = get_members(
        obj=install_package, predicate=inspect.ismodule, skip_names=[]
    )
    url_list = []

    for module_name, module in module_list:
        method_list = get_members(
            obj=module, predicate=inspect.isfunction, skip_names=[]
        )
        for method_name,_ in method_list:
            url = "%s/%s" % (module_name, method_name)
            url = base_url % url
            view = "%s.%s" % (module.__name__, method_name)

            url_list.append((url,view))

    return tuple(url_list)

#~ urls = get_urls(base_url='^_install/%s/(.*?)$')
#~ urlpatterns = patterns('', *urls)