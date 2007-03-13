
import os, sys, cgi, inspect

from django.db import connection

from PyLucid.install.tools import render
from PyLucid import settings
from PyLucid.models import Page
from PyLucid.utils import check_pass
from PyLucid import install as install_package



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
        skip_name=["urls", "index", "tools"]
    )
    for no, module_data in enumerate(module_list):
        module_name = module_data["name"]

        module_obj = getattr(install_package, module_name)
        members = get_members(
            obj=module_obj, predicate=inspect.isfunction,
            skip_name=["check_pass", "render"]
        )

        module_list[no]["views"] = members

    context = {
        "module_list": module_list
    }
    return render(context, menu_template)










