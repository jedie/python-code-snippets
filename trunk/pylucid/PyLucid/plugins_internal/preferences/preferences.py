# -*- coding: utf-8 -*-

"""
    Preferences
    ~~~~~~~~~~~

    A low level editor for the preferences.
    Using data_eval and pprint. Supports only Constants, Dicts, Lists, Tuples.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author: JensDiemer $

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev: $"

from pprint import pformat

from django import newforms as forms
from django.newforms.util import ValidationError
from django.utils.translation import ugettext as _

from PyLucid.models import Preference
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.data_eval import data_eval, DataEvalError

SELECT_TEMPLATE = """
{% for plugin, data in preferences.items %}
<fieldset><legend>{{ plugin }}</legend>
<ul>
  {% for pref in data %}
  <li><a href="{{ pref.link }}">{{ pref.name }}</a><br />
  {{ pref.description }}</li>
  {% endfor %}
</ul>
</fieldset>
{% endfor %}
"""

EDIT_TEMPLATE = """
<fieldset><legend>{{ plugin_name }} - {{ pref_name }}</legend>
<form method="post" action=".">
{{ form.as_p }}
<input type="submit" name="save" value="{% trans 'save' %}" />
<input type="submit" name="validate" value="{% trans 'validate' %}" />
<input onclick="self.location.href='{{ url_abort }}'" name="abort" value="{% trans 'abort' %}" type="reset" />
</form>
</fieldset>
"""

INTERNAL_NAME = "[system]"


class DataEvalField(forms.CharField):
    def clean(self, raw_value):
        raw_value = super(DataEvalField, self).clean(raw_value)
        try:
            value = data_eval(raw_value)
        except DataEvalError, e:
            raise ValidationError(_(u"data eval error: %s") % e)
        else:
            print "clean", value, type(value)
            return value

class PformatWidget(forms.Textarea):
    def __init__(self, attrs=None):
        self.attrs={'rows': '15'}

    def render(self, name, value, attrs=None):
        print "pformat", repr(value), type(value)
        if not isinstance(value, basestring):
            value = pformat(value)
        return super(PformatWidget, self).render(name, value, attrs=None)

class EditForm(forms.Form):
    """
    Form for editing a preferences
    """
    raw_value = DataEvalField(widget=PformatWidget())



class preferences(PyLucidBasePlugin):

    def _vebose_plugin_name(self, pref):
        if pref.plugin == None:
            return INTERNAL_NAME
        else:
            pref.plugin

    def select(self):
        """
        Display the sub menu
        """
        preferences = {}
        for pref in Preference.objects.all():
            plugin_name = self._vebose_plugin_name(pref)

            pref.link = self.URLs.methodLink("edit", args=(pref.id, pref.name))

            if plugin_name not in preferences:
                preferences[plugin_name] = [pref]
            else:
                preferences[plugin_name].append(pref)

        context = {
            "preferences": preferences,
        }
#        self._render_template("sub_menu", context)#, debug=True)
        self._render_string_template(SELECT_TEMPLATE, context)#, debug=True)

    def edit(self, url_args=None):
        try:
            url_args = url_args.strip("/").split("/",1)[0]
            pref_id = int(url_args)
        except Exception, e:
            self.page_msg.red("url error:", e)
            return

        p = Preference.objects.get(id = pref_id)

        if self.request.method == 'POST':
            form = EditForm(self.request.POST)
            if form.is_valid():
                value = form.cleaned_data["raw_value"]
                if "validate" in self.request.POST:
                    # rebuild the form for pformat with the eval data
                    form = EditForm({"raw_value": value})
                    self.page_msg("validate only...")
                else:
                    # save the form
                    p.value = value
                    p.save()
                    self.page_msg.green("new value saved!")
                    return self.select() # Display the menu
        else:
            form = EditForm({"raw_value": p.value})

        context = {
            "plugin_name": self._vebose_plugin_name(p),
            "pref_name": p.name,
            "form": form,
            "url_abort": self.URLs.methodLink("select"),
        }
#        self._render_template("sub_menu", context)#, debug=True)
        self._render_string_template(EDIT_TEMPLATE, context)#, debug=True)















