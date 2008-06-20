#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unitest for plugin API
    ~~~~~~~~~~~~~~~~~~~~~~

    TODO: We can test here many other things, e.g.:
        - plugin rights
        - plugin install/activate/deactivate

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, re

import tests
from tests.utils.FakeRequest import FakePageMsg

from django.conf import settings

from PyLucid.models import Page, Plugin
from PyLucid.system.plugin_manager import install_plugin


TEST_PLUGIN_NAME = "unittest_plugin"
CONTENT_START = "<pre>"
CONTENT_END = "</pre>"
CONTENT_RE = re.compile("<pre>(.*?)<\/pre>(?usm)")

MODEL_TEST = """Test the plugin models
Create TestArtist
entry with ID '%(no)s' created
Create TestAlbum
entry with ID '%(no)s' created:
TestAlbum 'A test Album', ID %(no)s, createby: superuser"""




class PluginAPI_Base(tests.TestCase):
    """
    Unit tests for detect_page function.
    """
    def setUp(self):
        self.login("superuser") # login client as superuser

        Page.objects.all().delete() # Delete all existins pages

        self.template = tests.create_template(
            content = (
                "<!-- page_messages -->\n"
                "{{ PAGE.content }}"
            )
        )

        # Create one page
        self.test_page = tests.create_page(
            content = "{% lucidTag unittest_plugin %}",
            template=self.template
        )

        self.command = "/%s/%s/%s/%%s/" % (
            settings.COMMAND_URL_PREFIX,
            self.test_page.id,
            TEST_PLUGIN_NAME,
        )
        self.test_url = self.test_page.get_absolute_url()

    #___________________________________________________________________________
    # SHARED UTILS

    def _get_plugin_content(self, url, regex=CONTENT_RE, debug=False):
        """
        request the url and returns with regex=CONTENT_RE: the plugin output
        """
        response = self.client.get(url)
        # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)

        raw_content = response.content
        if debug:
            print "--- url: ---"
            print url
            print "--- content: ---"
            print raw_content
            print "-"*79

        content = regex.findall(raw_content)
        if len(content) == 1:
            return content[0].strip()

        msg = (
            "Content not found in:\n"
            "----------------------------------------------------------------\n"
            "%s"
            "----------------------------------------------------------------"
        ) % raw_content
        self.fail(msg)

    def _get_plugin(self):
        return Plugin.objects.get(plugin_name=TEST_PLUGIN_NAME)

    #___________________________________________________________________________
    # PRETESTS

    def test_plugin_exist(self):
        """
        Test if the unittest plugin is normal installed and active
        """
        try:
            self.plugin = self._get_plugin()
        except Plugin.DoesNotExist, err:
            self.fail("Plugin doesn't exist: %s" % err)

        self.failUnless(self.plugin.active, True)
        #print "Plugin exists ID:", self.plugin.id

    def test_hello_world(self):
        """
        Checks via _command url the hello world response as a anonymous user
        """
        self.client.logout()

        url = self.command % "hello_world"
        response = self.client.get(url)
        # Check that the respose is 200 Ok.
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual2(
            response.content.strip(),
            (
                '<div class="PyLucidPlugins unittest_plugin"'
                ' id="unittest_plugin_hello_world">\n'
                'Hello world!\n'
                '</div>'
            )
        )


class PluginModel(PluginAPI_Base):
    """
    Tests around the plugin models.
    """
    def test_plugin_models(self):
        """
        Test the plugin models.
        Request three times the plugin_models view. This view creates on
        every request a new model entry in both test models and display
        some informations around this.
        After this, we request a view with a list of all existing model entries.
        """
        url = self.command % "plugin_models"

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 1}
        )

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 2}
        )

        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 3}
        )

        # Test all models view: A list of all existing models.
        url = self.command % "all_models"
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            (
                "All Albums:\n"
                "1: TestAlbum 'A test Album', ID 1, createby: superuser\n"
                "2: TestAlbum 'A test Album', ID 2, createby: superuser\n"
                "3: TestAlbum 'A test Album', ID 3, createby: superuser"
            )
        )

    def test_reinit(self):
        """
        reinit the plugin and check if the plugin model tabels would be
        droped and re-created.
        """
        url = self.command % "plugin_models"

        plugin = self._get_plugin()

        package_name = plugin.package_name
        plugin_name = plugin.plugin_name

        page_msg = FakePageMsg()

        # remove the plugin completely from the database
        # plugin model tables should be droped
        plugin.delete(page_msg, verbosity=2)

        # install the plugin
        # plugin model tables should be re-created, too.
        install_plugin(
            package_name, plugin_name, page_msg, verbosity=2, active=True
        )

        # Check 1:
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            MODEL_TEST % {"no": 1}
        )

        # Check 2:
        url = self.command % "all_models"
        content = self._get_plugin_content(url)#, debug=True)
        self.assertEqual2(
            content,
            (
                "All Albums:\n"
                "1: TestAlbum 'A test Album', ID 1, createby: superuser"
            )
        )


class PluginArgsTest(PluginAPI_Base):
    """
    Test for pass parameters to the plugin method...
        ...via lucidTag, handled in PyLucid.template_addons.lucidTag
        ...via url, handled in the plugin_manager
    """
    def test_lucidTag(self):
        """
        Request the lucidTag method from the test plugin.
        It display all args and kwargs.
        """
        content = self._get_plugin_content(self.test_url)
        self.assertEqual2(content, "args:\n()\npformarted kwargs:\n{}")

    def test_url_args(self):
        """
        Test arguments in a _command url
        """
        url = self.command % "lucidTag"
        url += "some/stuff/here/1/2/3/"
        content = self._get_plugin_content(url, debug=False)
        self.assertEqual2(
            content,
            "args:\n"
            "(u'some/stuff/here/1/2/3/',)\n"
            "pformarted kwargs:\n"
            "{}"
        )

    #__________________________________________________________________________
    # lucidTag KWARGS tests

    def _get_args_info(self, page_content):
        self.test_page.content = page_content
        self.test_page.save()
        content = self._get_plugin_content(self.test_url, debug=False)
        args_info = content.split("\n")
        return (args_info[1], args_info[3])

    def test_tag_no_args(self):
        """
        Tag without arguments
        """
        args, kwargs = self._get_args_info('{% lucidTag unittest_plugin %}')
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{}")

    def test_string_arg(self):
        """
        One string kwarg
        """
        args, kwargs = self._get_args_info(
            '{% lucidTag unittest_plugin arg1="test1" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{'arg1': u'test1'}")

    def test_tag_more_args(self):
        """
        More string kwargs
        """
        args, kwargs = self._get_args_info(
            '{% lucidTag unittest_plugin a="0" b="1" c="2" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs, "{'a': u'0', 'b': u'1', 'c': u'2'}")

    def test_tag_bool_args1(self):
        """
        The current implementation converts strings to bool if it found
        the bool words.
        """
        args, kwargs = self._get_args_info(
            '{% lucidTag unittest_plugin'
            ' t1="True" f1="False" t2="true" f2="false" %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs,
            "{'f1': False, 'f2': False, 't1': True, 't2': True}"
        )

    #__________________________________________________________________________
    # Problems with the current implementation.
    # We can't pass other things than string.
    """
    Importtant: All follow test will failed!
    See:
        http://pylucid.net:8080/pylucid/ticket/202
        http://pylucid.org/phpBB2/viewtopic.php?t=228
    """
    def test_tag_bool_args2(self):
        """
        Faild in the current implementation!
        """
        args, kwargs = self._get_args_info(
            '{% lucidTag unittest_plugin t1=True f1=False %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs,
            "{'f1': False, 'f2': False}",
            error_msg="Faild in the current implementation!"
        )

    def test_non_string_args(self):
        """
        Faild in the current implementation!
        """
        args, kwargs = self._get_args_info(
            '{% lucidTag unittest_plugin arg1=1 arg2=2.0 %}'
        )
        self.assertEqual2(args, "()")
        self.assertEqual2(kwargs,
            "{'arg1': 1, 'args2': 2.0}",
            error_msg="Faild in the current implementation!"
        )





if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])