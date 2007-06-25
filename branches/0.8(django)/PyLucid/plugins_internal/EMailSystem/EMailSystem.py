#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid EMail system Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A Plugin to send EMails to other installed PyLucid Users.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author:JensDiemer $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:$"

from django import newforms as forms
from django.contrib.auth.models import User
from django.core.mail import send_mail

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid import settings

TEMPLATE = """
<form method="post" action=".">
  <table class="form">
    {% trans 'Select users you a mail wants to send:' %}
    <ul>
    {% for user in user_list %}
      <li>
        <label>
          <input id="id_user_list_{{ user.id }}" value="{{ user.id }}" name="user_list" type="checkbox" {% if user.checked %}checked="checked"{% endif %}>
          {{ user.username }}
        </label>
      </li>
    {% endfor %}
    </ul>
    {{ form }}
  </table>
  <input type="submit" value="{% trans 'send email' %}" />
</form>
"""

class MailForm(forms.Form):
    sender = forms.EmailField()
    subject = forms.CharField(
        help_text=_("(The prefix '%s' would be insert.)") % (
            settings.EMAIL_SUBJECT_PREFIX
        ), min_length=10
    )
    mail_text = forms.CharField(widget=forms.Textarea,
        max_length=1024, min_length=20
    )


class EMailSystem(PyLucidBaseModule):
    def user_list(self):

        user_list = User.objects.values(
            "id", "username", "email",
#            "first_name", "last_name",
        )

        if self.request.method == 'POST':
            mail_form = MailForm(self.request.POST)
            if mail_form.is_valid():
                # Create the new user
                self.page_msg("send mail")
            else:
                self.page_msg(mail_form.errors)
        else:
            host = self.request.META.get("HTTP_HOST", settings.EMAIL_HOST)
            # Cut the port number, if exists
            host = host.split(":")[0]

            form_data = {
                "sender": "%s@%s" % (self.request.user,host),
            }
            mail_form = MailForm(form_data)

        checked_user = self.request.POST.getlist("user_list")
        try:
            checked_user = [int(id) for id in checked_user]
        except:
            self.page_msg("Post error")
        else:
            for user in user_list:
                if user["id"] in checked_user:
                    user["checked"] = True

#        html = mail_form.as_table()
        html = mail_form.as_p()

        context = {
            "form": html,
            "user_list": user_list,
        }

        return self._render_string_template(TEMPLATE, context, debug=True)