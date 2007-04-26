from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group

from PyLucid.settings import TABLE_PREFIX

def lazy_date(obj):
    if isinstance(obj, datetime):
        return obj
    return models.LazyDate()

class Page(models.Model):
    """
    A CMS Page Object
    """
    id = models.IntegerField(primary_key=True)

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.ForeignKey(
        "self", to_field="id", help_text="the higher-ranking father page"
    )
    position = models.IntegerField(
        help_text="ordering (number between -10 and 10)"
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
    markup = models.ForeignKey(
        "Markup", to_field="id",
        help_text="the used markup language for this page"
    )

    keywords = models.TextField(
        blank=True, maxlength=255, help_text="Keywords for the html header."
    )
    description = models.TextField(
        blank=True, maxlength=255, help_text="Text for the html header."
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(User, related_name="page_lastupdateby")

    showlinks = models.IntegerField(
        help_text="Put the Link to this page into Menu/Sitemap etc.?"
    )

    permitViewPublic = models.IntegerField(
        help_text="Does anomymous user see this page?"
    )
    permitViewGroup = models.ForeignKey(
        Group, related_name="page_permitViewGroup", blank=True,
        help_text="Usergroup how can see this page, if permitViewPublic denied."
    )

    owner = models.ForeignKey(
        User, help_text="The owner of this page (only information.)"
    )
    permitEditGroup = models.ForeignKey(
        Group, related_name="page_permitEditGroup", blank=True,
        help_text="Usergroup how can edit this page."
    )

    class Meta:
        db_table = '%spage' % TABLE_PREFIX

    class Admin:
        list_display = ("id", "shortcut", "name", "title", "description")
        list_display_links = ("shortcut",)
        list_filter = ("permitViewPublic","owner")
        search_fields = ["content","name", "title", "description","keywords"]
        fields = (
            ('basic', {'fields': ('id', 'content','parent','position',)}),
            ('identification', {'fields': ('name','shortcut','title')}),
            ('internal', {'fields': ('template','style','markup')}),
            ('meta', {'fields': ('keywords', 'description')}),
            ('update information', {
                'fields': ('createtime','lastupdatetime','lastupdateby')
            }),

            ('Advanced options', {
                'classes': 'collapse',
                'fields' : (
                    'showlinks', 'permitViewPublic', 'permitViewGroup',
                    'owner', 'permitEditGroup'
                ),
            }),
        )
        date_hierarchy = 'lastupdatetime'

    def get_absolute_url(self):
        return "/page/%s" % self.id

    def __str__(self):
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

class Archive(models.Model):
    id = models.IntegerField(primary_key=True)
    userID = models.IntegerField()
    type = models.CharField(maxlength=150)
    date = models.DateTimeField()
    comment = models.CharField(maxlength=255)
    content = models.TextField()

    class Admin:
        pass

    class Meta:
        db_table = '%sarchive' % TABLE_PREFIX
        verbose_name_plural = 'Archive'

#______________________________________________________________________________

#class Group(models.Model):
#    id = models.IntegerField(primary_key=True)
#    pluginID = models.IntegerField()
#    name = models.CharField(unique=True, maxlength=150)
#    section = models.CharField(maxlength=150)
#    description = models.CharField(maxlength=150)
#    lastupdatetime = models.DateTimeField()
#    lastupdateby = models.IntegerField(null=True, blank=True)
#    createtime = models.DateTimeField(default=models.LazyDate())
#
#    def save(self):
#        print "save..."
#        print self.lastupdatetime
#        print self.createtime
#        self.lastupdatetime = lazy_date(self.lastupdatetime)
#        self.createtime = lazy_date(self.createtime)
#
#        super(Group, self).save()
#
#    class Admin:
#        pass
#
#    class Meta:
#        db_table = '%sgroup' % TABLE_PREFIX

#______________________________________________________________________________

class Markup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=150)

    class Admin:
        list_display = ("id", "name")
        list_display_links = ("name",)

    class Meta:
        db_table = '%smarkup' % TABLE_PREFIX
        
    def __str__(self):
        return self.name

#______________________________________________________________________________

class Md5User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)
    realname = models.CharField(maxlength=150)
    email = models.CharField(maxlength=150)
    md5checksum = models.CharField(maxlength=192)
    salt = models.IntegerField()
    admin = models.IntegerField()

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)

    lastupdateby = models.IntegerField(null=True, blank=True)

    class Admin:
        pass

    class Meta:
        db_table = '%smd5user' % TABLE_PREFIX
        verbose_name_plural = 'MD5 Users'

#______________________________________________________________________________

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

#______________________________________________________________________________

class PagesInternal(models.Model):
    name = models.CharField(primary_key=True, maxlength=150)
    plugin = models.ForeignKey(
        "Plugin", to_field="id",
        help_text="The associated plugin"
    )
    
    method_id = models.IntegerField()
    
    template = models.ForeignKey(
        "Template", to_field="id",
        help_text="the used template for this internal page"
    )
    markup = models.ForeignKey(
        "Markup", to_field="id",
        help_text="the used markup language for this page"
    )

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(
        User, related_name="page_internal_lastupdateby"
    )
    
    content_html = models.TextField()
    content_js = models.TextField()
    content_css = models.TextField()
    description = models.TextField()

    class Admin:
        list_display = ("name", "description")
        #ordering = ('plugin',"name")
        list_filter = ("plugin",)
        date_hierarchy = 'lastupdatetime'
        search_fields = ["name","content_html","content_js","content_css"]        

    class Meta:
        db_table = '%spages_internal' % TABLE_PREFIX
        
    def __str__(self):
        return self.name

#______________________________________________________________________________

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

    def __str__(self):
        return self.method_name

    def __repr__(self):
        return "<Plugindata: %s, id:%s>" % (self.method_name, self.plugin_id)

#______________________________________________________________________________

class Plugin(models.Model):
    id = models.IntegerField(primary_key=True)
    package_name = models.CharField(maxlength=255)
    module_name = models.CharField(maxlength=90)
    version = models.CharField(blank=True, maxlength=45)
    author = models.CharField(blank=True, maxlength=150)
    url = models.CharField(blank=True, maxlength=255)
    description = models.CharField(blank=True, maxlength=255)
    long_description = models.TextField(blank=True)
    active = models.IntegerField()
    debug = models.IntegerField()
    SQL_deinstall_commands = models.TextField(null=True, blank=True)

    class Admin:
        list_display = ("package_name", "description", "version")
        ordering = ('package_name',)
        list_filter = ("author",)

    class Meta:
        db_table = '%splugin' % TABLE_PREFIX

    def __str__(self):
        return self.module_name.replace("_"," ")

#______________________________________________________________________________

class Preference(models.Model):
    id = models.IntegerField(primary_key=True)
    pluginID = models.IntegerField()
    section = models.CharField(maxlength=90)
    varName = models.CharField(maxlength=90)
    name = models.CharField(maxlength=150)
    description = models.TextField()
    value = models.CharField(maxlength=255)
    type = models.CharField(maxlength=90)

    class Admin:
        list_display = ("id", "pluginID", "section", "varName", "name", "value", "type", "description")
        list_display_links = ("varName",)
        list_filter = ("section",)
        ordering = ('section',"varName")
        search_fields = ["varName", "value", "description"]

    class Meta:
        db_table = '%spreference' % TABLE_PREFIX

    def __str__(self):
        return "%s (%s)" % (self.varName, self.name)

#______________________________________________________________________________

class Style(models.Model):
    id = models.IntegerField(primary_key=True)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(User, related_name="style_lastupdateby")
    
    plugin_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(unique=True, maxlength=150)
    description = models.TextField(null=True, blank=True)
    content = models.TextField()

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    class Meta:
        db_table = '%sstyle' % TABLE_PREFIX
        
    def __str__(self):
        return self.name

#______________________________________________________________________________

class TemplateEngine(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)

    class Admin:
        list_display = ("id", "name")
        list_display_links = ("name",)

    class Meta:
        db_table = '%stemplate_engine' % TABLE_PREFIX
        
    def __str__(self):
        return self.name

#______________________________________________________________________________

class Template(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)

    createtime = models.DateTimeField(auto_now_add=True)
    lastupdatetime = models.DateTimeField(auto_now=True)
    lastupdateby = models.ForeignKey(User, related_name="template_lastupdateby")
        
    description = models.TextField()
    content = models.TextField()

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    class Meta:
        db_table = '%stemplate' % TABLE_PREFIX

    def __str__(self):
        return self.name
