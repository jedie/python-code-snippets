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
    :license: GNU GPL, see LICENSE for more details.
"""

from django.db import models
from django.contrib.auth.models import User, Group

from PyLucid.tools.shortcuts import getUniqueShortcut


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
                    'showlinks', 'permitViewGroup', 'permitEditGroup'
                ),
            }),
        )

    def _check_parent(self, id):
        """
        Prevents inconsistent data (parent-child-loop).
        Check recusive if a new parent can be attached and is not a loop.
        TODO: This method should used in newform is_valid() ???
        """
        if not self.parent:
            # No parent exist -> root arraived
            return True

        if self.parent.id == id:
            # Error -> parent-loop found.
            raise AssertionError("New parent is invalid. (parent-child-loop)")

        # go a level deeper to the root
        self.parent._check_parent(id)

    def save(self):
        """save a new page"""
        if self.id != None:# A existing page should update
            # check if a new parent is no parent-child-loop:
            self._check_parent(self.id)
            # Exclude the existing shortcut from the "black list":
            exclude_shortcut = Page.objects.get(id=self.id).shortcut
        else: # A new page created
            exclude_shortcut = None

        # Make a new shortcut unique:
        self.shortcut = getUniqueShortcut(self.shortcut, exclude_shortcut)

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


class JS_LoginData(models.Model):
    user = models.ForeignKey(User)

    md5checksum = models.CharField(maxlength=192)
    salt = models.IntegerField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username

    class Admin:
        list_display = (
            'user', 'md5checksum', 'salt', 'createtime', 'lastupdatetime'
        )

    class Meta:
        verbose_name = verbose_name_plural = 'JS-LoginData'


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
    TODO: Should we have a type attribute here?
        (like CharField, TextField, BooleanField)
    """
    plugin = models.ForeignKey(
        "Plugin", help_text="The associated plugin",
        null=True, blank=True
    )
    name = models.CharField(maxlength=150)
    description = models.TextField()
    value = models.CharField(maxlength=255)

    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(
        User, null=True, blank=True,
        related_name="preferences_lastupdateby",
    )

    class Admin:
        list_display = ("plugin", "name", "value", "description")
        list_display_links = ("name",)
        list_filter = ("plugin",)
        ordering = ("name",)
        search_fields = ["name", "value", "description"]


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
