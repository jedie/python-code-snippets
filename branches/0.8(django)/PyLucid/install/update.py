
"""
2. update

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from datetime import datetime

from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.settings import TABLE_PREFIX



#______________________________________________________________________________

class Update(BaseInstall):
    def view(self):
        self._redirect_execute(self.update_structure)
        self._redirect_execute(self.update_data)
        self.context["output"] += (
            "\nupdate done.\n"
            "You must execute 'syncdb'!"
        )
        return self._simple_render(headline="Update PyLucid tables.")

    def update_structure(self):
        print "update PyLucid database:"

        from django.db import connection
        cursor = connection.cursor()

        def display_info(txt):
            print "\n"
            print "%s:" % txt
            print "-"*79
            print

        def verbose_execute(SQLcommand):
            print "%s..." % SQLcommand,
            try:
                cursor.execute(SQLcommand)
            except Exception, e:
                print "Error: %s" % e
            else:
                print "OK"

        #_______________________________________________________________________
        display_info("Drop obsolete tables")

        tables = (
            "l10n", "group", "groups", "user_group", "log", "session_data",
            "plugindata", "template_engines", "template_engine"
        )
        for tablename in tables:
            tablename = TABLE_PREFIX + tablename
            SQLcommand = "DROP TABLE %s;" % tablename
            verbose_execute(SQLcommand)

        #_______________________________________________________________________
        display_info("rename tables")

        tablenames = (
            ("pages",  "page"),
            ("styles", "style"),
            ("templates", "template"),
            ("markups", "markup"),
            ("md5users", "md5user"),
            ("plugins", "plugin"),
            ("preferences", "preference"),
            ("styles", "style"),
            ("templates", "template"),
        )
        for source, destination in tablenames:
            source = TABLE_PREFIX + source
            destination = TABLE_PREFIX + destination

            SQLcommand = "RENAME TABLE %s TO %s;" % (source, destination)
            verbose_execute(SQLcommand)

        #_______________________________________________________________________
        display_info("Drop some obsolete columns")

        column_delete = (
            ("page", "permitViewPublic"),
        )

        for item in column_delete:
            SQLcommand = "ALTER TABLE %s%s DROP COLUMN %s;" % (
                TABLE_PREFIX, item[0], item[1]
            )
            verbose_execute(SQLcommand)

        #_______________________________________________________________________
        display_info("Change some column names (for SQL constraints)")
        column_rename = (
            # Because of the development version are here "double" Statements.
            ("page", "parent parent_id INTEGER NULL"),
            ("page", "parent_id parent_id INTEGER NULL"),

            ("page", "template template_id INTEGER NOT NULL"),
            ("page", "template_id template_id INTEGER NOT NULL"),

            ("page", "style style_id INTEGER NOT NULL"),
            ("page", "style_id style_id INTEGER NOT NULL"),

            ("page", "markup markup_id INTEGER NOT NULL"),
            ("page", "markup_id markup_id INTEGER NOT NULL"),

            ("page", "lastupdateby lastupdateby_id INTEGER NOT NULL"),
            ("page", "lastupdateby_id lastupdateby_id INTEGER NOT NULL"),

            ("page", "ownerID owner_id INTEGER NOT NULL"),
            ("page", "owner_id owner_id INTEGER NOT NULL"),

            ("page", "permitEditGroupID permitEditGroup_id INTEGER NULL"),
            ("page", "permitEditGroup_id permitEditGroup_id INTEGER NULL"),

            ("page", "permitViewGroupID permitViewGroup_id INTEGER NULL"),
            ("page", "permitViewGroup_id permitViewGroup_id INTEGER NULL"),

            ("page", "showlinks showlinks bool NOT NULL"),

            ("pages_internal", "template_engine template_id INTEGER NOT NULL"),
            ("pages_internal", "template_id template_id INTEGER NOT NULL"),

            ("pages_internal", "lastupdateby lastupdateby_id INTEGER NOT NULL"),
            ("pages_internal", "lastupdateby_id lastupdateby_id INTEGER NOT NULL"),

            ("pages_internal", "markup markup_id INTEGER NOT NULL"),
            ("pages_internal", "markup_id markup_id INTEGER NOT NULL"),

            ("style", "lastupdateby lastupdateby_id INTEGER NOT NULL"),
            ("style", "lastupdateby_id lastupdateby_id INTEGER NOT NULL"),

            ("template", "lastupdateby lastupdateby_id INTEGER NOT NULL"),
            ("template", "lastupdateby_id lastupdateby_id INTEGER NOT NULL"),
        )
        for item in column_rename:
            SQLcommand = "ALTER TABLE %s%s CHANGE %s;" % (
                TABLE_PREFIX, item[0], item[1]
            )
            verbose_execute(SQLcommand)

        #_______________________________________________________________________

        display_info(
            "Delete 'plugin' table (must be recreated with 'syncdb'!)"
        )
        verbose_execute("DROP TABLE %splugin" % TABLE_PREFIX)

        display_info(
            "Delete 'pages_internal' table (must be recreated with 'syncdb'!)"
        )
        verbose_execute("DROP TABLE %spages_internal" % TABLE_PREFIX)

    #____________________________________________________________________________

    def update_data(self):
        """
        Update some data in tables
        -parent relation:
            old model: root parent = 0
            new model: root parent = None
        """
        from PyLucid.models import Page
        print
        print "="*80
        print " *** Update some PyLucid table data ***"
        print "="*80
        print
        for page in Page.objects.all():
            print page
            # Update parent relation
            try:
                parent = page.parent
            except Page.DoesNotExist:
                print " - Update parent page to None"
                page.parent = None
                page.save()
            else:
                print " - Parent relation OK"
            print


def update(request, install_pass):
    """
    1. update DB tables from v0.7.2 to django PyLucid v0.8
    """
    return Update(request, install_pass).view()

#______________________________________________________________________________

import re

REPLACE_DATA = (
    ("|escapexml ", "|escape "),
)

UNSUPPORTED_TAGS = ("{% recurse ",)

LUCID_TAG_RE = re.compile(
    "<lucid(Tag):(.*?)/>"
    "|"
    "<lucid(Function):(.*?)>(.*?)</lucidFunction>"
)
PAGE_MSG_TAG = """\
  {% if messages %}
    <fieldset id="page_msg"><legend>page message</legend>
    {% for message in messages %}
      {{ message }}<br />
    {% endfor %}
    </fieldset>
  {% endif %}\
"""
CHANGE_TAGS = {
    "page_msg": PAGE_MSG_TAG,
    "script_login": "{{ login_link }}",
    "robots": "{{ robots }}",
    "powered_by": "{{ powered_by }}",

    "page_body": "{{ PAGE.content }}",
    "page_title": "{{ PAGE.title|escape }}",
    "page_keywords": "{{ PAGE.keywords }}",
    "page_description": "{{ PAGE.description }}",
    "page_last_modified": "{{ PAGE.last_modified }}",
    "page_datetime": "{{ PAGE.datetime }}",

    "script_duration": "<!-- script_duration -->",
}

class UpdateTemplates(BaseInstall):
    def view(self):
        self._redirect_execute(self.start_update)
#        self._redirect_execute(self.update_internalpage)
        return self._simple_render(headline="update templates")

    #___________________________________________________________________________

    def start_update(self):
        """
        Update the template, page internal and all CMS pages.
        """
        from PyLucid.models import Template, PagesInternal, Page

        self._update(Template, "content", "Templates")
        self._update(PagesInternal, "content_html", "internal pages")
        self._update(Page, "content", "CMS pages")

    def _update(self, model, content_attr_name, info_text):
        """
        Update all Entries from the given model.
        """
        from PyLucid.tools.Diff import display_plaintext_diff

        print "\n"*3
        print "*"*79
        print " **** Update all %s ****" % info_text
        print "*"*79
        print "\n"*2

        model_objects = model.objects.all()
        for model_item in model_objects:
            name = model_item.name
            print "\n================[ %s ]================" % name

            old_content = getattr(model_item, content_attr_name)

            content = self._update_content(old_content)

            if model_item.createtime == None:
                # Should be normaly not None :)
                # Is from a old PyLucid installation
                model_item.createtime = datetime.now()
                print "Update 'createtime' to now. (Time was not set.)"
            else:
                if content == old_content:
                    print "\t - Nothing to change."
                    continue

            print "\t - changed!\n\nthe diff:"
            display_plaintext_diff(old_content, content)

            # assign new content to model
            setattr(model_item, content_attr_name, content)

            # save the new content
            model_item.save()

    def _update_content(self, content):
        content = self._convert_lucidTags(content)
        content = self._update_filters(content)
        self._display_warnings(content)
        return content

    #___________________________________________________________________________

    def _convert_lucidTags(self, content):
        """
        change PyLucid tags:
        <lucidTag:page_title/> -> {% lucidTag page_title %}

        <lucidFunction:IncludeRemote>localhost</lucidFunction>

        {% lucidTag IncludeRemote url="localhost" %}

        <lucidTag:RSS>http://sourceforge.net/export/rss2_projnews.php?group_id=146328&rss_fulltext=1</lucidTag>
        """
        content = LUCID_TAG_RE.sub(self._handleTag, content)
        return content

    def _handleTag(self, matchobj):
        matches = matchobj.groups()
        #~ print matches
        if matches[0] == "Tag":
            return self._changeTag(matches[1])
        elif matches[2] == "Function":
            return '{%% lucidTag %s url="%s" %%}' % (
                matches[3], matches[4]
            )
        else:
            print "Error: Wrong RE-match:"
            print matchobj.group(0)
            print matches
            return matchobj.group(0)

    def _changeTag(self, tag_name):
        try:
            return CHANGE_TAGS[tag_name]
        except KeyError:
            return "{%% lucidTag %s %%}" % tag_name

    #___________________________________________________________________________

    def _update_filters(self, content):
        """
        simple replace some tags
        """
        for source, destination in REPLACE_DATA:
            if source in content:
                content = content.replace(source, destination)
        return content

    #___________________________________________________________________________

    def _display_warnings(self, content):
        """
        Waring if there is some unsupportet tags in the template
        """
        for tag in UNSUPPORTED_TAGS:
            if tag in content:
                print "\t - WARNING: unsupportet tag '%s' in Template!" % tag

    #___________________________________________________________________________



#    def update_internalpage(self):
#        from PyLucid.tools.Diff import display_plaintext_diff
#        from PyLucid.models import PagesInternal
#
#        for internal_page in PagesInternal.objects.all():
#            name = internal_page.name
#            old_content = internal_page.content_html
#
#            print "\n==================[ %s ]==================\n" % name
#            _display_warnings(old_content)
#            content = _convert_internalpage(old_content)
#            if not content:
#                print "\t - Nothing to change."
#                continue
#
#            print "\t - changed!\n\nthe diff:"
#            display_plaintext_diff(old_content, content)
#
#            internal_page.content_html = content
#            internal_page.save()
#            print "\t - updated and saved."
#            print
#            print


def update_templates(request, install_pass):
    """
    2. update to the new django template engine
    """
    return UpdateTemplates(request, install_pass).view()