
"""
2. update

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from datetime import datetime

from django.db import connection

from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.settings import TABLE_PREFIX
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
        if TABLE_PREFIX == "PyLucid_":
            # TODO: Must rename the old tables first.
            raise "Conflict: Table names are the same!"

        # self.syncdb is inherited from the Sync_DB class
        self._redirect_execute(self.syncdb)

        self._redirect_execute(self.move_data)
        return self._simple_render(headline="Update PyLucid tables.")

    def move_data(self):
        """
        move some data from the old PyLucid tables into the new django tables
        """
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE auth_user;")
        cursor.execute("TRUNCATE TABLE PyLucid_js_logindata;")
        cursor.execute("TRUNCATE TABLE PyLucid_template;")
        cursor.execute("TRUNCATE TABLE PyLucid_style;")
        cursor.execute("TRUNCATE TABLE PyLucid_page;")
        cursor.execute("TRUNCATE TABLE PyLucid_preference;")

        user_map = self._convert_users()

        template_map = self._convert_template_style(user_map, "templates")
        style_map = self._convert_template_style(user_map, "styles")
        markup_name_map, markup_id_map = self._convert_markups()

        page_map = self._convert_pages(
            user_map, template_map, style_map, markup_id_map
        )

        self._convert_preferences(
            page_map, user_map, template_map, style_map, markup_name_map
        )

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
            ",".join(keys), TABLE_PREFIX, table_name
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
        ) % TABLE_PREFIX
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
                ",".join(page_keys), TABLE_PREFIX, id
            )
            cursor.execute(SQLcommand)
            page_data = cursor.fetchall()[0]
            print page_data

            page_dict = self.__to_dict(page_data, page_keys)
            print page_dict

#            self.__fix_datetimes(page_dict, ["createtime", "lastupdatetime"])
            old_lastupdateby_id = page_dict["lastupdateby"]
            page_dict["lastupdateby"] = user_map[old_lastupdateby_id]

            old_owner_id = page_dict.pop("ownerID")
            page_dict["createby"] = user_map[old_owner_id]

            print page_dict

            parent_id = page_dict.pop("parent")

            old_template_id = page_dict["template"]
            page_dict["template"] = template_map[old_template_id]

            old_style_id = page_dict["style"]
            page_dict["style"] = style_map[old_style_id]

            old_markup_id = page_dict["markup"]
            page_dict["markup"] = markup_map[old_markup_id]

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
            "id", "name", "realname", "email", "md5checksum", "salt", "admin",
            "createtime"
        )

        SQLcommand = "SELECT %s FROM %smd5users;" % (
            ",".join(user_table_keys), TABLE_PREFIX
        )
        cursor.execute(SQLcommand)

        user_map = {}

        user_data = cursor.fetchall()
        for current_user in user_data:
#            print current_user
            user_dict = self.__to_dict(current_user, user_table_keys)
#            print user_dict

            print "Create new django user '%s':" % user_dict["realname"],

            # The pass would be hased. So is it not useable for the User!
            user = User.objects.create_user(
                user_dict["name"], user_dict["email"], user_dict["md5checksum"]
            )

            user.is_staff = True
            user.is_active = True

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
            user_map[user_dict["id"]] = user

            print "Put md5data into DB:",
            if not user_dict["salt"] in (None, 0):
                js_data = JS_LoginData(
                    user=user, md5checksum=user_dict["md5checksum"],
                    salt=user_dict["salt"]
                )
                js_data.save()
                print "OK"
            else:
                print "Skip, no valid data. Passreset needed."

        print "="*80
        print

        return user_map



    def _convert_preferences(self, page_map, user_map, template_map, style_map,
                                                                    markup_map):
        """
        move some preferences
        """
        print "_"*80
        print "Move the preferences..."
        print
        cursor = connection.cursor()

#    plugin = models.ForeignKey(
#        "Plugin", help_text="The associated plugin",
#        null=True, blank=True
#    )
#    name = models.CharField(maxlength=150)
#    description = models.TextField()
#    value = models.CharField(maxlength=255)
#
#    lastupdatetime = models.DateTimeField(auto_now=True)
#    lastupdateby = models.ForeignKey(User, related_name="page_lastupdateby")


        table_keys = (
            "name", "description", "value"
        )
        needed = {
            "Default Page": "index page",
            "Preferred Text Markup": "default markup",
            "Default Template Name": "default template",
            "Default Style Name": "default stylesheet",
        }
        where = " OR ".join(["name='%s'" % i for i in needed.keys()])
        SQLcommand = "SELECT %s FROM %spreferences WHERE %s;" % (
            ",".join(table_keys), TABLE_PREFIX, where
        )
        cursor.execute(SQLcommand)

        preferences = cursor.fetchall()
        for p in preferences:
            p_dict = self.__to_dict(p, table_keys)
            print p_dict
            old_value = p_dict["value"]
            old_name = p_dict["name"]

            # get it a short new name
            p_dict["name"] = name = needed[old_name]

            # update the value
            if name == "index page":
                page_obj = page_map[int(old_value)]
                new_value = page_obj.id
            elif name == "default markup":
                markup_obj = markup_map[old_value]
                new_value = markup_obj.id
            elif name == "default template":
                template_obj = template_map[int(old_value)]
                new_value = template_obj.id
            elif name == "default stylesheet":
                style_obj = style_map[int(old_value)]
                new_value = style_obj.id
            else:
                raise # Should never happen.


#    plugin = models.ForeignKey(
#        "Plugin", help_text="The associated plugin",
#        null=True, blank=True
#    )
#    name = models.CharField(maxlength=150)
#    description = models.TextField()
#    value = models.CharField(maxlength=255)
#
#    lastupdatetime = models.DateTimeField(auto_now=True)
#    lastupdateby = models.ForeignKey(
#        User, null=True, blank=True,
#        related_name="preferences_lastupdateby",
#    )

            p = Preference(
                plugin=None, name=name,
                description = p_dict["description"],
                value = new_value,
            )
            p.save()







class UpdateOLD(Sync_DB):
    def view(self):
#        self._redirect_execute(self.update_structure)
#        self._redirect_execute(self.update_data)
#        self.context["output"] += (
#            "\nupdate done.\n"
#            "You must execute 'syncdb'!"
#        )
#
#        # self.syncdb is inherited from Sync_DB
#        self._redirect_execute(self.syncdb)

        self._redirect_execute(self.convert_data)

        return self._simple_render(headline="Update PyLucid tables.")

    def update_structure(self):
        print "update PyLucid database:"

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
#            ("md5users", "md5user"),
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

    #___________________________________________________________________________

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

    #___________________________________________________________________________




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