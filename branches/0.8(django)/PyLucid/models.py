from django.db import models

from PyLucid.settings import TABLE_PREFIX


class Page(models.Model):
    """
    A CMS Page Object
    """
    id = models.IntegerField(primary_key=True)

    content = models.TextField(blank=True, help_text="The CMS page content.")

    parent = models.IntegerField(help_text="the id of the father page")
    position = models.IntegerField(help_text="ordering (number between -10 and 10)")

    name = models.CharField(maxlength=150, help_text="A short page name")
    shortcut = models.CharField(unique=True, maxlength=150, help_text="shortcut to built the URLs")
    title = models.CharField(blank=True, maxlength=150, help_text="A long page title")

    template = models.IntegerField(help_text="ID of the used template.")
    style = models.IntegerField(help_text="ID of the used stylesheet.")
    markup = models.CharField(blank=True, maxlength=150, help_text="ID of the used markup language.")

    keywords = models.TextField(blank=True, maxlength=255, help_text="Keywords for the html header.")
    description = models.TextField(blank=True, maxlength=255, help_text="Text for the html header.")

    createtime = models.DateTimeField()
    lastupdatetime = models.DateTimeField(null=True, blank=True)
    lastupdateby = models.IntegerField(null=True, blank=True)

    showlinks = models.IntegerField(help_text="Put the Link to this page into Menu/Sitemap etc.?")

    permitViewPublic = models.IntegerField(help_text="Does anomymous user see this page?")
    permitViewGroupID = models.IntegerField(null=True, blank=True, help_text="Usergroup how can see this page, if permitViewPublic denied.")

    ownerID = models.IntegerField()
    permitEditGroupID = models.IntegerField(null=True, blank=True, help_text="Usergroup how can edit this page.")

    class Meta:
        db_table = '%spage' % TABLE_PREFIX

    class Admin:
        list_display = ("id", "shortcut", "name", "title", "description")
        list_display_links = ("shortcut",)
        list_filter = ("permitViewPublic","ownerID")
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
                    'showlinks', 'permitViewPublic', 'permitViewGroupID',
                    'ownerID', 'permitEditGroupID'
                ),
            }),
        )
        date_hierarchy = 'lastupdatetime'

    def get_absolute_url(self):
        return "/page/%s" % self.id

    def __str__(self):
        return "CMS page '%s'" % self.shortcut

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

class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    pluginID = models.IntegerField()
    name = models.CharField(unique=True, maxlength=150)
    section = models.CharField(maxlength=150)
    description = models.CharField(maxlength=150)
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField(null=True, blank=True)
    createtime = models.DateTimeField()

    class Admin:
        pass

    class Meta:
        db_table = '%sgroup' % TABLE_PREFIX

class L10N(models.Model):
    id = models.IntegerField(primary_key=True)
    lang = models.TextField()
    varName = models.CharField(maxlength=150)
    value = models.CharField(maxlength=255)
    description = models.CharField(maxlength=255)

    class Admin:
        pass

    class Meta:
        db_table = '%sl10n' % TABLE_PREFIX
        verbose_name_plural = 'L10N'

class Log(models.Model):
    id = models.IntegerField(primary_key=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    sid = models.CharField(maxlength=150)
    user_name = models.CharField(blank=True, maxlength=150)
    ip = models.CharField(blank=True, maxlength=150)
    domain = models.CharField(blank=True, maxlength=150)
    message = models.CharField(maxlength=255)
    typ = models.CharField(maxlength=150)
    status = models.CharField(maxlength=36)

    class Admin:
        list_display = (
            "timestamp", "user_name", "ip", "domain", "message",
            "typ", "status"
        )
        list_display_links = ("message",)
        list_filter = ("sid","user_name", "ip", "domain", "typ", "status")
        ordering = ("-timestamp",)
        date_hierarchy = 'timestamp'

    class Meta:
        db_table = '%slog' % TABLE_PREFIX

class Markup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=150)

    class Admin:
        list_display = ("id", "name")
        list_display_links = ("name",)

    class Meta:
        db_table = '%smarkup' % TABLE_PREFIX

class Md5User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)
    realname = models.CharField(maxlength=150)
    email = models.CharField(maxlength=150)
    md5checksum = models.CharField(maxlength=192)
    salt = models.IntegerField()
    admin = models.IntegerField()
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField(null=True, blank=True)
    createtime = models.DateTimeField()

    class Admin:
        pass

    class Meta:
        db_table = '%smd5user' % TABLE_PREFIX
        verbose_name_plural = 'MD5 Users'

class ObjectCache(models.Model):
    id = models.CharField(primary_key=True, maxlength=120)
    expiry_time = models.DateTimeField()
    request_ip = models.CharField(blank=True, maxlength=45)
    user_id = models.IntegerField(null=True, blank=True)
    pickled_data = models.TextField(blank=True)

    class Admin:
        pass

    class Meta:
        db_table = '%sobject_cache' % TABLE_PREFIX
        verbose_name_plural = 'Object Cache'

class PagesInternal(models.Model):
    name = models.CharField(primary_key=True, maxlength=150)
    plugin_id = models.IntegerField()
    method_id = models.IntegerField()
    template_engine = models.IntegerField(null=True, blank=True)
    markup = models.IntegerField(null=True, blank=True)
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField()
    content_html = models.TextField()
    content_js = models.TextField()
    content_css = models.TextField()
    description = models.TextField()
    createtime = models.DateTimeField()

    class Admin:
        list_display = ("name", "plugin_id", "description")
        ordering = ('plugin_id',"name")
        list_filter = ("plugin_id",)
        date_hierarchy = 'lastupdatetime'
        search_fields = ["name","content_html","content_js","content_css"]        

    class Meta:
        db_table = '%spages_internal' % TABLE_PREFIX
        
    def __str__(self):
        return self.name

class Plugindata(models.Model):
    id = models.IntegerField(primary_key=True)
    plugin_id = models.IntegerField()
    method_name = models.CharField(maxlength=150)
    internal_page_info = models.CharField(blank=True, maxlength=255)
    menu_section = models.CharField(blank=True, maxlength=255)
    menu_description = models.CharField(blank=True, maxlength=255)
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
    SQL_deinstall_commands = models.TextField(blank=True)
    plugin_cfg = models.TextField(blank=True)

    class Admin:
        list_display = ("package_name", "description", "version")
        ordering = ('package_name',)
        list_filter = ("author",)

    class Meta:
        db_table = '%splugin' % TABLE_PREFIX

    def __str__(self):
        return self.package_name

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

class SessionData(models.Model):
    session_id = models.CharField(maxlength=96)
    expiry_time = models.DateTimeField()
    ip = models.CharField(maxlength=45)
    domain_name = models.CharField(maxlength=150)
    session_data = models.TextField()

    class Admin:
        pass

    class Meta:
        db_table = '%ssession_data' % TABLE_PREFIX
        verbose_name_plural = 'Session Data'

class Style(models.Model):
    id = models.IntegerField(primary_key=True)
    createtime = models.DateTimeField()
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField()
    plugin_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(unique=True, maxlength=150)
    description = models.TextField(blank=True)
    content = models.TextField()

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    class Meta:
        db_table = '%sstyle' % TABLE_PREFIX

class TemplateEngine(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)

    class Admin:
        list_display = ("id", "name")
        list_display_links = ("name",)

    class Meta:
        db_table = '%stemplate_engine' % TABLE_PREFIX

class Template(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)
    lastupdateby = models.IntegerField()
    description = models.TextField()
    content = models.TextField()
    lastupdatetime = models.DateTimeField()
    createtime = models.DateTimeField()

    class Admin:
        list_display = ("id", "name", "description")
        list_display_links = ("name",)

    class Meta:
        db_table = '%stemplate' % TABLE_PREFIX

class UserGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    userID = models.IntegerField()
    groupID = models.IntegerField()
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField(null=True, blank=True)
    createtime = models.DateTimeField()

    class Admin:
        pass

    class Meta:
        db_table = '%suser_group' % TABLE_PREFIX
