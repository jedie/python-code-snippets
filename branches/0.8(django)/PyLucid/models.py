"""
    PyLucid.models
    ~~~~~~~~~~~~~~

    The database models for PyLucid
    based on Django's ORM.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import pickle

from django.db import models
from django.dispatch import dispatcher
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import UNUSABLE_PASSWORD

from PyLucid.tools.shortcuts import getUniqueShortcut
from PyLucid.tools import crypt



class Page(models.Model):
    """
    A CMS Page Object

    TODO: We need a cache system for the parent relation.
    """
    # Explicite id field, so we can insert a help_text ;)
    id = models.AutoField(primary_key=True, help_text="The internal page ID.")

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "self", null=True, blank=True,
        to_field="id", help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default = 0,
        help_text = "ordering weight for sorting the pages in the menu."
    )

    name = models.CharField(maxlength=150, help_text="A short page name")

    shortcut = models.CharField(
        unique=True, maxlength=150, help_text="shortcut to built the URLs"
    )
    title = models.CharField(
        blank=True, maxlength=150, help_text="A long page title"
    )

    template = models.ForeignKey(
        "Template", to_field="id", help_text="the used template for this page"
    )
    style = models.ForeignKey(
        "Style", to_field="id", help_text="the used stylesheet for this page"
    )
    markup = models.ForeignKey("Markup",
        related_name="page_markup",
        help_text="the used markup language for this page"
    )

    keywords = models.CharField(
        blank=True, maxlength=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(
        blank=True, maxlength=255,
        help_text="Short description of the contents. (for the html header)"
    )

    createtime = models.DateTimeField(
        auto_now_add=True, help_text="Create time",
    )
    lastupdatetime = models.DateTimeField(
        auto_now=True, help_text="Time of the last change.",
    )
    createby = models.ForeignKey(
        User, editable=False, related_name="page_createby",
        help_text="User how create the current page.",
    )
    lastupdateby = models.ForeignKey(
        User, editable=False, related_name="page_lastupdateby",
        help_text="User as last edit the current page.",
    )

    showlinks = models.BooleanField(default=True,
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )
    permitViewPublic = models.BooleanField(default=True,
        help_text="Can anonymous see this page?"
    )

    permitViewGroup = models.ForeignKey(
        Group, related_name="page_permitViewGroup", null=True, blank=True,
        help_text="Limit viewable to a group?"
    )

    permitEditGroup = models.ForeignKey(
        Group, related_name="page_permitEditGroup", null=True, blank=True,
        help_text="Usergroup how can edit this page."
    )

    class Admin:
        list_display = (
            "id", "shortcut", "name", "title", "description",
            "lastupdatetime", "lastupdateby"
        )
        list_display_links = ("shortcut",)
        list_filter = (
            "createby","lastupdateby","permitViewPublic", "template", "style"
        )
        date_hierarchy = 'lastupdatetime'
        search_fields = ["content", "name", "title", "description", "keywords"]

        fields = (
            ('basic', {'fields': ('content','parent','position',)}),
            ('meta', {'fields': ('keywords', 'description')}),
            ('name / shortcut / title', {
                'classes': 'collapse',
                'fields': ('name','shortcut','title')
            }),
            ('template / style / markup', {
                'classes': 'collapse',
                'fields': ('template','style','markup')
            }),
            ('Advanced options', {
                'classes': 'collapse',
                'fields' : (
                    'showlinks', 'permitViewPublic',
                    'permitViewGroup', 'permitEditGroup'
                ),
            }),
        )

    def _check_default_page_settings(self):
        """
        The default page must have some settings.
        """
        try:
            entry = Preference.objects.get(name="index page")
        except Preference.DoesNotExist:
            # Update old PyLucid installation?
            return

        index_page_id = entry.value

        if int(self.id) != int(index_page_id):
            # This page is not the default index page
            return

        #______________________________________________________________________
        # Check some settings for the default index page:

        assert self.permitViewPublic == True, (
            "Error save the new page data:"
            " The default page must be viewable for anonymous users."
            " (permitViewPublic must checked.)"
        )
        assert self.showlinks == True, (
            "Error save the new page data:"
            " The default page must displayed in the main menu."
            " (showlinks must checked.)"
        )

    def _check_parent(self, id):
        """
        Prevents inconsistent data (parent-child-loop).
        Check recusive if a new parent can be attached and is not a loop.
        TODO: This method should used in newform is_valid() ???
        """
        if not self.parent:
            # No parent exist -> root arraived
            return

        if self.parent.id == id:
            # Error -> parent-loop found.
            raise AssertionError("New parent is invalid. (parent-child-loop)")

        # go a level deeper to the root
        self.parent._check_parent(id)

    def _prepare_shortcut(self):
        """
        prepare the page shortcut:
        -rebuild shortcut (maybe)
        -make shortcut unique
        """
        try:
            auto_shortcuts = Preference.objects.get(name='auto shortcuts').value
        except Preference.DoesNotExist:
            # Update old PyLucid installation?
            auto_shortcuts = True

        if auto_shortcuts in (1, True, "1"):
            # We should rebuild the shortcut
            self.shortcut = self.name

        #______________________________________________________________________
        # Make a new shortcut unique:

        if self.id != None:# A existing page should update
            # Exclude the existing shortcut from the "black list":
            exclude_shortcut = Page.objects.get(id=self.id).shortcut
        else: # A new page created
            exclude_shortcut = None

        self.shortcut = getUniqueShortcut(self.shortcut, exclude_shortcut)

    def save(self):
        """
        Save a new page or update changed page data.
        before save: check some data consistency to prevents inconsistent data.
        """
        if self.id != None:
            # a existing page should be updated (It's not a new page ;)

            # Check some settings for the default index page:
            self._check_default_page_settings()

            # check if a new parent is no parent-child-loop:
            self._check_parent(self.id)

        # Rebuild shortcut / make shortcut unique:
        self._prepare_shortcut()

        super(Page, self).save() # Call the "real" save() method

    def get_absolute_url(self):
        """
        Get the absolute url (without the domain/host part)
        """
        parent_shortcut = ""
        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            return parent_shortcut + self.shortcut + "/"
        else:
            return "/" + self.shortcut + "/"

    def get_verbose_title(self):
        """
        TODO: Should we handle name and title on a other way...
        """
        if self.title and self.title != self.name:
            return self.name + " - " + self.title
        else:
            return self.name

    def __strftime(self, datetime_obj):
        if datetime_obj == None:
            return "[unknown]"
        else:
            return datetime_obj.strftime(_("%Y-%m-%d - %H:%M"))

    def get_createtime_string(self):
        return self.__strftime(self.createtime)

    def get_lastupdatetime_string(self):
        return self.__strftime(self.lastupdatetime)

    def __unicode__(self):
        return self.shortcut


#______________________________________________________________________________


class RegistrationManager(models.Manager):
    """
    Custom manager for JS_LoginData.
    """
    def create_or_update_user(self, user_data, is_staff=False, is_active=False,
                                                            is_superuser=False):

        raw_password = user_data.pop("password")

        # create the django user account:
        user, created = User.objects.get_or_create(
            username = user_data["username"],
            defaults = user_data
        )
        user.is_staff = is_staff
        user.is_active = is_active
        user.is_superuser = is_superuser
        user.first_name = user_data.get("first_name", "")
        user.last_name = user_data.get("last_name", "")
        user.set_password(raw_password)
        user.save()

        # create the PyLucid JS-LoginData:
        js_login_data = self.get_or_create(user = user)[0]
        js_login_data.set_password_from_raw(raw_password)
        js_login_data.save()

        return created

    def set_unusable_password(self, username):
        user, js_login_data = self.get_user(username)
        user.set_unusable_password()
        user.save()
        js_login_data.set_unusable_password()
        js_login_data.save()

    def set_new_password(self, username, django_salt, django_sha, pylucid_salt,
                                                                pylucid_sha):
        """
        set a new password for the normal django account and for the PyLucid
        SHA1-JS-Login (self.sha_checksum)
        """
        assert django_salt != pylucid_salt
        assert django_sha != pylucid_sha

        user = User.objects.get(username = username)
        js_login_data = self.get_or_create(user = user)[0]

        # Update the django user account:
        django_salt_hash = "sha1$%s$%s" % (django_salt, django_sha)
        user.password = django_salt_hash
        user.save()

        # Update the PyLucid JS-LoginData:
        js_login_data.set_password_from_salt_hash(pylucid_salt, pylucid_sha)
        js_login_data.save()

    def get_user(self, username):
        """
        returns the django user object and the JS-LoginData entry object.
        """
        user = User.objects.get(username = username)
        js_login_data = self.get(user = user)
        return user, js_login_data

    def delete_user(self, username):
        """
        Delete the django user account and the JS-LoginData entry
        """
        user, js_login_data = self.get_user(username)
        js_login_data.delete()
        user.delete()


class JS_LoginData(models.Model):
    user = models.ForeignKey(User)

    sha_checksum = models.CharField(maxlength=192)
    salt = models.CharField(maxlength=5)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    objects = RegistrationManager()

    def set_unusable_password(self):
        self.salt = UNUSABLE_PASSWORD
        self.sha_checksum = UNUSABLE_PASSWORD

    def set_password_from_salt_hash(self, salt, sha):
        self.salt = salt
        sha_checksum = crypt.make_sha_checksum(sha)
        self.sha = sha_checksum

    def set_password_from_raw(self, raw_password):
        raw_password = str(raw_password)
        salt, sha_checksum = crypt.make_sha_checksum2(raw_password)
        self.salt = salt
        self.sha_checksum = sha_checksum

    def __unicode__(self):
        return self.user.username

    class Admin:
        list_display = (
            'user', 'sha_checksum', 'salt', 'createtime', 'lastupdatetime'
        )

    class Meta:
        verbose_name = verbose_name_plural = 'JS-LoginData'

#______________________________________________________________________________


class Markup(models.Model):
    name = models.CharField(maxlength=150)

    class Admin:
        list_display = ("id", "name",)
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name


class PagesInternal(models.Model):
    name = models.CharField(primary_key=True, maxlength=150)
    plugin = models.ForeignKey(
        "Plugin", #to_field="id",
        help_text="The associated plugin"
    )
    markup = models.ForeignKey("Markup",
        related_name="page_internal_markup",
        help_text="the used markup language for this page"
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(
        User, related_name="page_internal_createby",
        null=True, blank=True,
    )
    lastupdateby = models.ForeignKey(
        User, related_name="page_internal_lastupdateby",
        null=True, blank=True,
    )

    content_html = models.TextField()
    content_js = models.TextField(blank=True)
    content_css = models.TextField(blank=True)
    description = models.TextField()

    class Admin:
        list_display = ("name", "description")
        #ordering = ('plugin',"name")
        list_filter = ("plugin",)
        date_hierarchy = 'lastupdatetime'
        search_fields = ["name", "content_html", "content_js", "content_css"]

    def __unicode__(self):
        return self.name


class Plugin(models.Model):
    package_name = models.CharField(maxlength=255)
    plugin_name = models.CharField(maxlength=90, unique=True)
    version = models.CharField(null=True, blank=True, maxlength=45)
    author = models.CharField(blank=True, maxlength=150)
    url = models.CharField(blank=True, maxlength=255)
    description = models.CharField(blank=True, maxlength=255)
    long_description = models.TextField(blank=True)
    can_deinstall = models.BooleanField(default=True,
        help_text=(
            "If false and/or not set:"
            " This essential plugin can't be deinstalled."
        )
    )
    active = models.BooleanField(default=False,
        help_text="Is this plugin is enabled and useable?"
    )

    class Meta:
        permissions = (
            # Permission identifier     human-readable permission name
            ("can_use",                 "Can use the plugin"),
        )

    class Admin:
        list_display = (
            "active", "plugin_name", "description", "version", "can_deinstall"
        )
        list_display_links = ("plugin_name",)
        ordering = ('package_name', 'plugin_name')
        list_filter = ("author",)

    def __unicode__(self):
        return self.plugin_name.replace("_"," ")


class Preference(models.Model):
    """
    Preferences for PyLucid system and all Plugins.
    Any pickleable Python object can be stored.
    Use a small cache, so the pickle.loads() method would only be used on the
    first get_value.

    Note:
        -This model has no editable field. Because it makes no sense to edit
             the pickled data string ;)
        -There is a bug in django, if the users try to edit a entry:
            http://code.djangoproject.com/ticket/3434
    """
    def __init__(self, *args, **kwargs):
        self._cache = {}
        super(Preference, self).__init__(*args, **kwargs)

    plugin = models.ForeignKey(
        "Plugin", help_text="The associated plugin",
        null=True, blank=True, editable=False
    )
    name = models.CharField(maxlength=150, db_index=True, editable=False)
    description = models.TextField(editable=False)

    #__________________________________________________________________________
    # The value of the entry

    def __get_value(self):
        if "value" in self._cache:
            value = self._cache["value"]
        else:
            self._value = str(self._value)
            value = pickle.loads(self._value)
            self._cache["value"] = value
        return value

    def __set_value(self, value):
        self._cache["value"] = value
        self._value = pickle.dumps(value)

    _value = models.TextField(editable=False, help_text="Pickled Python object")
    value = property(__get_value, __set_value)

    #__________________________________________________________________________
    # The default value.

    def __get_default_value(self):
        if "default_value" in self._cache:
            default_value = self._cache["default_value"]
        else:
            self._default_value = str(self._default_value)
            default_value = pickle.loads(self._default_value)
            self._cache["default_value"] = default_value
        return default_value

    def __set_default_value(self, default_value):
        self._cache["default_value"] = default_value
        self._default_value = pickle.dumps(default_value)

    _default_value = models.TextField(editable=False,
        help_text="Pickled Python object"
    )
    default_value = property(__get_default_value, __set_default_value)

    #__________________________________________________________________________

    field_type = models.CharField(maxlength=150, editable=False,
        help_text="The data type for this entry (For building a html form)."
    )

    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(
        User, null=True, blank=True, editable=False,
        related_name="preferences_lastupdateby",
    )

    def save(self):
        """
        Save a new page or update changed page data.
        before save: check some data consistency to prevents inconsistent data.
        """
        if self.id == None:
            # A new preferences should be saved.
            if self._default_value == "":
                # No default value given in the __init__ -> Use current value
                self._default_value = self._value

        super(Preference, self).save() # Call the "real" save() method

    def __unicode__(self):
#        <Preference: Preference object>
        return "%s '%s'" % (self.plugin, self.name)

    class Admin:
        list_display = (
            "plugin", "name", "value", "default_value", "description"
        )
        list_display_links = ("name",)
        list_filter = ("plugin",)
        ordering = ("name",)
        search_fields = ["name", "value", "default_value", "description"]


class Style(models.Model):
    name = models.CharField(unique=True, maxlength=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="style_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="style_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    class Admin:
        list_display = (
            "id", "name", "description", "createtime", "lastupdatetime"
        )
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name


class Template(models.Model):
    name = models.CharField(unique=True, maxlength=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    createby = models.ForeignKey(User, related_name="template_createby",
        null=True, blank=True
    )
    lastupdateby = models.ForeignKey(User, related_name="template_lastupdateby",
        null=True, blank=True
    )

    description = models.TextField()
    content = models.TextField()

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name
