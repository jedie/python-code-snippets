
"""
get_urls() for appending _install section views.
"""

from PyLucid import install as install_package

import inspect



def get_members(obj, predicate, skip_names=[], skip_secret=True):
    """
    filtered inspect.getmembers() with predicate
    """
    member_list = inspect.getmembers(obj, predicate)

    result = []
    for member in member_list:
        if skip_secret and member[0].startswith("_"):
            continue
        if member[0] in skip_names:
            continue
        result.append(member)
        
    return result


def get_install_view_urls(base_url):
    """
    generate the django urlpatterns for all install views.
    """
    module_list = get_members(
        obj=install_package, predicate=inspect.ismodule, skip_names=["urls"]
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

#            print view
            url_list.append((url,view))

    return tuple(url_list)
