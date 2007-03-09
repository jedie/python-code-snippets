
import os, sys, cgi, inspect


from django.http import HttpResponse
from django.db import connection
from django.template import Template, Context, loader

from PyLucid.models import Page
#~ import __init__ as install_package
from PyLucid import install as install_package



from PyLucid.utils import check_pass



def get_members(obj, predicate, skip_name=[], skip_secret=True):
    result = []

    module_list = inspect.getmembers(obj, predicate)
    module_list = [i[0] for i in module_list]
    for module_name in module_list:
        if skip_secret and module_name.startswith("_"):
            continue
        if module_name in skip_name:
            continue

        module_obj = getattr(obj, module_name)

        doc = module_obj.__doc__
        if doc:
            doc = doc.strip()
            doc = doc.splitlines()[0]

        result.append((doc, module_name))

    result.sort()

    for no,data in enumerate(result):
        result[no] = {"doc": data[0], "name": data[1]}

    return result



menu_template = """
{% extends "PyLucid/install/base.html" %}

{% block content %}
<h1>menu</h1>
<ul>
{% for item in module_list %}
    <li><h2>{{ item.doc }}</h2>
    <ul>
    {% for sub_item in item.views %}
        <li>
            <a href="{{ item.name }}/{{ sub_item.name }}/">{{ sub_item.doc }}</a>
        </li>
    {% endfor %}
    </ul>
    </li>
{% endfor %}
</ul>
<h1>URL Info for '{{ domain }}':</h1>
<table>
{% for item in url_info %}
    <tr>
        <td>{{ item.0|escape }}</td>
        <td>{{ item.1|escape }}</td>
    </tr>
{% endfor %}
</table>

{% endblock %}
"""
#
def index(request, install_pass):
    """
    Generate and display the install section menu
    """
    check_pass(install_pass)
    menu_data = {}

    module_list = get_members(
        obj=install_package, predicate=inspect.ismodule,
        skip_name=["urls", "index"]
    )
    for no, module_data in enumerate(module_list):
        module_name = module_data["name"]

        module_obj = getattr(install_package, module_name)
        members = get_members(
            obj=module_obj, predicate=inspect.isfunction,
            skip_name=["check_pass"]
        )

        module_list[no]["views"] = members

    from PyLucid.urls import urls

    t = Template(menu_template)
    c = Context({
        "module_list": module_list,
        "url_info": urls,
    })
    html = t.render(c)
    return HttpResponse(html)










