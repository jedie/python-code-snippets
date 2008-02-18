
"""
2. update

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from datetime import datetime

from django.db import connection

from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.settings import OLD_TABLE_PREFIX
from PyLucid.models import JS_LoginData, Page, Template, Style, Markup, Preference

from django.contrib.auth.models import User

#______________________________________________________________________________

from PyLucid.install.install import Sync_DB
class Update(Sync_DB):
    """
    Update a old PyLucid installation.
    -Create all model tables
    -copy/convert the data from the old PyLucid installation into the new tables
    """
    def view(self):
        headline="Update PyLucid tables."

        if OLD_TABLE_PREFIX == "PyLucid_":
            # TODO: Must rename the old tables first.
            return self._simple_render(
                output = "Error: Conflict: Table names are the same!",
                headline=headline
            )
        elif OLD_TABLE_PREFIX in ("", None):
            return self._simple_render(
                output = (
                    "Error: OLD_TABLE_PREFIX is empty! Please check your"
                    " settings.py and insert the table prefix from your old"
                    " PyLucid installation."
                ),
                headline=headline
            )

        # self._syncdb are inherited from the Sync_DB class.
        self._redirect_execute(self._syncdb)

        self._redirect_execute(self.move_data)

        self.context["output"] += (
            "\nReady.\n"
            "Now you must run the template update!"
        )

        return self._simple_render(headline=headline)

    def move_data(self):
        """
        move some data from the old PyLucid tables into the new django tables
        """
        cursor = connection.cursor()

        # FIXME: Truncate tables only for Testing!!!
        # So we can call the update routines repeatedly, without "Duplicate
        # entry" errors
        cursor.execute("TRUNCATE TABLE auth_user;")
        cursor.execute("TRUNCATE TABLE PyLucid_js_logindata;")
        cursor.execute("TRUNCATE TABLE PyLucid_template;")
        cursor.execute("TRUNCATE TABLE PyLucid_style;")
        cursor.execute("TRUNCATE TABLE PyLucid_page;")

        user_map = self._convert_users()

        template_map = self._convert_template_style(user_map, "templates")
        style_map = self._convert_template_style(user_map, "styles")
        markup_name_map, markup_id_map = self._convert_markups()

        page_map = self._convert_pages(
            user_map, template_map, style_map, markup_id_map
        )

        try:
            self._setup_preferences(page_map)
        except Exception, e:
            print "Error:", e

    def __to_dict(self, data, keylist):
        """
        small tool for convert a db-tuple-result into a dict
        """
        result = {}
        for item, key in zip(data, keylist):
            result[key] = item
        return result

    def __get_all(self, keys, table_name):
        cursor = connection.cursor()
        SQLcommand = "SELECT %s FROM %s%s;" % (
            ",".join(keys), OLD_TABLE_PREFIX, table_name
        )
        cursor.execute(SQLcommand)
        data = cursor.fetchall()
        result = []
        for line in data:
            result.append(
                self.__to_dict(line, keys)
            )
        return result

    def __fix_datetimes(self, data, keys):
        """
        changes all wrong 00-00-0000 datetime values.
        django problematic: http://code.djangoproject.com/ticket/443

        TODO: Check if this is ok!
        """
        for key in keys:
            if data[key] == None:
                return
            if not isinstance(data[key], datetime):
                data[key] = datetime.now()

    def _convert_template_style(self, user_map, table_name):
        """
        move the templates and styles
        Note: Both tables structures are identical.
        """
        print "_"*80
        print "Move %s..." % table_name
        print
        table_keys = (
            "id", "name", "lastupdateby", "description", "content",
            "lastupdatetime", "createtime"
        )
        items = self.__get_all(table_keys, table_name)

        item_map = {}
        for item in items:
#            self.__fix_datetimes(item, ["createtime", "lastupdatetime"])
            try:
                item["lastupdateby"] = user_map[item["lastupdateby"]]
            except KeyError:
                item["lastupdateby"] = None

            print item

            # With the old version there is no "createby"
            item["createby"] = item["lastupdateby"]

            old_id = item.pop("id")

            if table_name == "templates":
                new_entry = Template(**item)
            elif table_name == "styles":
                new_entry = Style(**item)
            else:
                raise # Should never happen.

            new_entry.save()

            item_map[old_id] = new_entry

        return item_map


    def _convert_markups(self):
        print "_"*80
        print "Move markups..."
        print
        table_keys = ("id", "name")
        markups = self.__get_all(table_keys, "markups")

        markup_name_map = {}
        markup_id_map = {}
        for markup in markups:
            print markup
            new_markup = Markup(**markup)
            new_markup.save()

            markup_name_map[markup["name"]] = new_markup
            markup_id_map[markup["id"]] = new_markup

        return markup_name_map, markup_id_map


    def _convert_pages(self, user_map, template_map, style_map, markup_map):
        """
        move the CMS pages
        """
        print "_"*80
        print "Move the CMS pages..."
        print
        cursor = connection.cursor()

        SQLcommand = (
            "SELECT id FROM %spages;"
        ) % OLD_TABLE_PREFIX
        cursor.execute(SQLcommand)

        page_keys = (
            "name", "shortcut", "title", "parent", "position", "template",
            "style", "createtime", "markup", "content", "keywords",
            "description", "lastupdatetime", "lastupdateby", "showlinks",
            "permitViewPublic", "ownerID"
        )

        page_ids = cursor.fetchall()
        parent_data = []
        page_map = {}
        for id in page_ids:
            id = id[0]
            print id
            SQLcommand = "SELECT %s FROM %spages WHERE id=%s;" % (
                ",".join(page_keys), OLD_TABLE_PREFIX, id
            )
            cursor.execute(SQLcommand)
            page_data = cursor.fetchall()[0]
            print page_data

            page_dict = self.__to_dict(page_data, page_keys)
            print page_dict

#            self.__fix_datetimes(page_dict, ["createtime", "lastupdatetime"])
            old_lastupdateby_id = page_dict["lastupdateby"]
            try:
                page_dict["lastupdateby"] = user_map[old_lastupdateby_id]
            except KeyError, e:
                print "User with ID '%s' unknown!" % e
                page_dict["lastupdateby"] = user_map.values()[0]
                print "Use the first one."

            old_owner_id = page_dict.pop("ownerID")
            try:
                page_dict["createby"] = user_map[old_owner_id]
            except KeyError, e:
                print "User with ID '%s' unknown!" % e
                page_dict["createby"] = user_map.values()[0]
                print "Use the first one."

            print page_dict

            parent_id = page_dict.pop("parent")

            old_template_id = page_dict["template"]
            page_dict["template"] = template_map[old_template_id]

            old_style_id = page_dict["style"]
            page_dict["style"] = style_map[old_style_id]

            old_markup_id = int(page_dict["markup"])
            page_dict["markup"] = markup_map[old_markup_id]

            for key in ("title", "keywords", "description"):
                if page_dict[key] == None:
                    page_dict[key] = ""

            new_page = Page(**page_dict)
            new_page.save()
            page_map[id] = new_page

            parent_data.append(
                (id, parent_id)
            )

        print
        print "_"*80
        # Only now we can rebuild the nested sets hierarchy
        print "rebuild the nested sets hierarchy\n"
        for page_id, parent_id in parent_data:
            if parent_id == 0:
                # there is no parent page
                parent_page = None
                parent_name = "[root]"
            else:
                parent_page = page_map[parent_id]
                parent_name = parent_page.name

            # get the page and assign the parent page
            page = page_map[page_id]

            print "%30s -> %s" % (page.name, parent_name)
            page.parent=parent_page
            page.save()

        print "="*80
        print
        return page_map


    def _convert_users(self):
        """
        convert the user accounts
        """
        print "_"*80
        print "move User accounts..."
        print
        cursor = connection.cursor()

        user_table_keys = (
            "id", "name", "realname", "email", "admin", "createtime"
        )

        SQLcommand = "SELECT %s FROM %smd5users;" % (
            ",".join(user_table_keys), OLD_TABLE_PREFIX
        )
        try:
            cursor.execute(SQLcommand)
        except Exception, msg:
            if "doesn't exist" in str(msg):
                # First time the update routine access to the old tables.
                # If the table was not found, the OLD_TABLE_PREFIX seems to
                # be wrong.
                msg = (
                    '%s - It seems to be, that OLD_TABLE_PREFIX="%s" settings'
                    ' is wrong. Please check your settings.py'
                ) % (msg, OLD_TABLE_PREFIX)
            raise Exception(msg)


        user_map = {}

        user_data = cursor.fetchall()
        for current_user in user_data:
#            print current_user
            user_dict = self.__to_dict(current_user, user_table_keys)
#            print user_dict

            print "Create new django user '%s':" % user_dict["realname"],

            # The pass would be hased. So is it not useable for the User!
            user = User.objects.create_user(
                user_dict["name"], user_dict["email"]
            )

            user.is_staff = True
            user.is_active = True
            user.set_unusable_password()

            if user_dict["admin"] == 1:
                user.is_superuser = True
            else:
                user.is_superuser = False

            realname = user_dict["realname"].rsplit(" ", 1)
            if len(realname) == 1:
                user.first_name = ""
                user.last_name = realname[0]
            else:
                user.first_name = realname[0]
                user.last_name = realname[1]

            print "django user created;",
            user.save()

            # For later using
            old_id = user_dict["id"]
            user_map[old_id] = user

            print "old ID: %s - new ID: %s;" % (old_id, user.id)

        print "\nNote:\n * For all Users a password reset is needed!"

        print "="*80
        print

        return user_map



    def _setup_preferences(self, page_map):
        """
        setup some preferences
        """
        print "_"*80
        print "Setup preferences..."
        print

        cursor = connection.cursor()
        SQLcommand = (
            "SELECT value FROM %spreferences WHERE varName='defaultPage';"
        ) % OLD_TABLE_PREFIX
        cursor.execute(SQLcommand)
        defaultPageID = int(cursor.fetchone()[0])

        print "default page:", defaultPageID

        new_index_page = page_map[defaultPageID]
        print "page:", new_index_page
        id = new_index_page.id
        print "id:", id

        print "Save new page ID...",
        p = Preference.objects.get(name = "index page")
        p.value = id
        p.save()
        print "OK"




def update(request):
    """
    1. update DB tables from v0.7.2 to django PyLucid v0.8
    """
    return Update(request).start_view()

#______________________________________________________________________________

import re

REPLACE_DATA = (
    ("|escapexml ", "|escape "),
    ("<PyLucidInternal:addCode/>", "")
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
    "page_last_modified": "{{ PAGE.lastupdatetime }}",
    "page_datetime": "{{ PAGE.datetime }}",

    "list_of_new_sides": "{% lucidTag page_update_list %}",

    "script_duration": "<!-- script_duration -->",

    "page_style":  "{% lucidTag page_style %}",
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
        from PyLucid.tools.Diff import diff_lines

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
            print diff_lines(old_content, content)

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


def update_templates(request):
    """
    2. update to the new django template engine
    """
    return UpdateTemplates(request).start_view()