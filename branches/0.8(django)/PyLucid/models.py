from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group


def lazy_date(obj):
    if isinstance(obj, datetime):
        return obj
    return models.LazyDate()


class Page(models.Model):
    """
    A CMS Page Object

    TODO: We need a cache system for the parent relation.
    """
    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "self", null=True, blank=True,
        to_field="id", help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default = 0,
        help_text = "ordering (number between -10 and 10)"
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
        blank=True, maxlength=255, help_text="Keywords for the html header."
    )
    description = models.CharField(
        blank=True, maxlength=255, help_text="Text for the html header."
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    createby = models.ForeignKey(User, related_name="page_createby")
    lastupdateby = models.ForeignKey(User, related_name="page_lastupdateby")

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
            "id", "shortcut", "name", "title", "description", "lastupdatetime"
        )
        list_display_links = ("shortcut",)
        list_filter = (
            "createby","lastupdateby","permitViewPublic", "template", "style"
        )
        search_fields = ["content","name", "title", "description","keywords"]
        fields = (
            ('basic', {'fields': ('content','parent','position',)}),
            ('identification', {'fields': ('name','shortcut','title')}),
            ('internal', {'fields': ('template','style','markup')}),
            ('meta', {'fields': ('keywords', 'description')}),
            ('update information', {
                'fields': ('createtime','lastupdatetime','lastupdateby')
            }),
            ('Advanced options', {
                #'classes': 'collapse',
                'fields' : (
                    'showlinks', 'permitViewGroup', 'permitEditGroup'
                ),
            }),
        )
        date_hierarchy = 'lastupdatetime'

    def get_absolute_url(self):
        """
        permanent link?
        """
        return "/_goto/%s" % self.shortcut

    def __unicode__(self):
        return self.shortcut

    def get_style_name(self):
        """
        returns the name of the current stylesheet
        """
        style_id = self.style
        style = Style.objects.get(id__exact=style_id)
        return style.name

    def __strftime(self, datetime_obj):
        if datetime_obj == None:
            return "[unknown]"
        else:
            return datetime_obj.strftime(_("%Y-%m-%d - %H:%M"))

    def get_createtime_string(self):
        return self.__strftime(self.createtime)

    def get_lastupdatetime_string(self):
        return self.__strftime(self.lastupdatetime)

#______________________________________________________________________________

"""
Not used yet.
class Archive(models.Model):
    user = models.ForeignKey(User)

    type = models.CharField(maxlength=150)
    date = models.DateTimeField()
    comment = models.CharField(maxlength=255)
    content = models.TextField()

    class Admin:
        pass

    class Meta:
        verbose_name_plural = 'Archive'
"""

#______________________________________________________________________________

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

#______________________________________________________________________________

class Markup(models.Model):
    name = models.CharField(maxlength=150)

    class Admin:
        list_display = ("id", "name",)
        list_display_links = ("name",)

    def __unicode__(self):
        return self.name

#______________________________________________________________________________

"""
obsolete???
class ObjectCache(models.Model):
    id = models.CharField(primary_key=True, maxlength=120)
    expiry_time = models.DateTimeField(null=True)
    request_ip = models.CharField(blank=True, maxlength=45)
    user_id = models.IntegerField(null=True, blank=True)
    pickled_data = models.TextField(blank=True)

    class Admin:
        pass

    class Meta:
        db_table = '%sobject_cache' % TABLE_PREFIX
        verbose_name_plural = 'Object Cache'
"""

#______________________________________________________________________________

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
        search_fields = ["name","content_html","content_js","content_css"]

    def __unicode__(self):
        return self.name

#______________________________________________________________________________

"""
obsolete???
class Plugindata(models.Model):
    id = models.IntegerField(primary_key=True)
    plugin_id = models.IntegerField()
    method_name = models.CharField(maxlength=150)
    internal_page_info = models.CharField(null=True, blank=True, maxlength=255)
    menu_section = models.CharField(null=True, blank=True, maxlength=255)
    menu_description = models.CharField(null=True, blank=True, maxlength=255)
    must_admin = models.IntegerField()
    must_login = models.IntegerField()
    has_Tags = models.IntegerField()
    no_rights_error = models.IntegerField()
    direct_out = models.IntegerField()
    sys_exit = models.IntegerField()

    class Admin:
        list_display = ("id", "method_name", "plugin_id")
        list_display_links = ("method_name",)
        ordering = ('plugin_id',"method_name")
        list_filter = ("plugin_id",)

    class Meta:
        db_table = '%splugindata' % TABLE_PREFIX
        verbose_name_plural = 'Plugin Data'

    def __unicode__(self):
        return self.method_name

    def __repr__(self):
        return "<Plugindata: %s, id:%s>" % (self.method_name, self.plugin_id)
"""

#______________________________________________________________________________

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

    class Admin:
        list_display = (
            "active", "plugin_name", "description", "version", "can_deinstall"
        )
        list_display_links = ("plugin_name",)
        ordering = ('package_name',"plugin_name")
        list_filter = ("author",)

    def __unicode__(self):
        return self.plugin_name.replace("_"," ")

#______________________________________________________________________________

class Preference(models.Model):
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
        ordering = ("plugin","name")
        search_fields = ["name", "value", "description"]

#    def __unicode__(self):
#        return self.name

#______________________________________________________________________________

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

#______________________________________________________________________________

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
