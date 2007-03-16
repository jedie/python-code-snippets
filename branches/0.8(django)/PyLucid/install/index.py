
"""
The index view
 - generate the _install section menu
"""

from PyLucid import install as install_package
from PyLucid.install.BaseInstall import BaseInstall

import inspect


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
{% if bla %}blub{% endif %}
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
class Index(BaseInstall):
    """
    Generate and display the install section menu
    """
    def view(self):
        menu_data = {}
    
        module_list = get_members(
            obj=install_package, predicate=inspect.ismodule,
            skip_name=install_package.SKIP_MODULES
        )
        for no, module_data in enumerate(module_list):
            module_name = module_data["name"]
    
            module_obj = getattr(install_package, module_name)
            members = get_members(
                obj=module_obj, predicate=inspect.isfunction,
                skip_name=[]
            )
    
            module_list[no]["views"] = members
    
        self.context["module_list"] = module_list
        
        # The install_pass variable was set in BaseInstall.__init__
        # If we delete it from the context, the "back to menu"-Links does
        # not rendered ;)
        del self.context["install_pass"]
        
        return self._render(menu_template)


def index(request, install_pass):
    "index view"
    return Index(request, install_pass).view()
    
    
    











