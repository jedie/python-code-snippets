from django.db import models

from settings import TABLE_PREFIX

class Page(models.Model):
    """
    A CMS Page
    """
    id = models.IntegerField(primary_key=True)
    parent = models.IntegerField()

    content = models.TextField(blank=True)

    position = models.IntegerField()

    name = models.CharField(maxlength=150)
    shortcut = models.CharField(unique=True, maxlength=150)
    title = models.CharField(blank=True, maxlength=150)

    template = models.IntegerField()
    style = models.IntegerField()
    markup = models.CharField(blank=True, maxlength=150)

    keywords = models.TextField(blank=True)
    description = models.TextField(blank=True)

    createtime = models.DateTimeField()
    lastupdatetime = models.DateTimeField(null=True, blank=True)
    lastupdateby = models.IntegerField(null=True, blank=True)

    showlinks = models.IntegerField()

    permitViewPublic = models.IntegerField()
    permitViewGroupID = models.IntegerField(null=True, blank=True)

    ownerID = models.IntegerField()
    permitEditGroupID = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = '%spage' % TABLE_PREFIX

    class Admin:
        pass

    def __str__(self):
        return "CMS page '%s'" % self.shortcut

class Archive(models.Model):
    id = models.IntegerField(primary_key=True)
    userID = models.IntegerField()
    type = models.CharField(maxlength=150)
    date = models.DateTimeField()
    comment = models.CharField(maxlength=255)
    content = models.TextField()
    class Meta:
        db_table = '%sarchive' % TABLE_PREFIX

class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    pluginID = models.IntegerField()
    name = models.CharField(unique=True, maxlength=150)
    section = models.CharField(maxlength=150)
    description = models.CharField(maxlength=150)
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField(null=True, blank=True)
    createtime = models.DateTimeField()
    class Meta:
        db_table = '%sgroup' % TABLE_PREFIX

class L10N(models.Model):
    id = models.IntegerField(primary_key=True)
    lang = models.TextField()
    varName = models.CharField(maxlength=150)
    value = models.CharField(maxlength=255)
    description = models.CharField(maxlength=255)
    class Meta:
        db_table = '%sl10n' % TABLE_PREFIX

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
    class Meta:
        db_table = '%slog' % TABLE_PREFIX

class Markup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=150)
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
    class Meta:
        db_table = '%smd5user' % TABLE_PREFIX

class ObjectCache(models.Model):
    id = models.CharField(primary_key=True, maxlength=120)
    expiry_time = models.DateTimeField()
    request_ip = models.CharField(blank=True, maxlength=45)
    user_id = models.IntegerField(null=True, blank=True)
    pickled_data = models.TextField(blank=True)
    class Meta:
        db_table = '%sobject_cache' % TABLE_PREFIX

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
    class Meta:
        db_table = '%spages_internal' % TABLE_PREFIX

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
    class Meta:
        db_table = '%splugindata' % TABLE_PREFIX

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
    class Meta:
        db_table = '%splugin' % TABLE_PREFIX

class Preference(models.Model):
    id = models.IntegerField(primary_key=True)
    pluginID = models.IntegerField()
    section = models.CharField(maxlength=90)
    varName = models.CharField(maxlength=90)
    name = models.CharField(maxlength=150)
    description = models.TextField()
    value = models.CharField(maxlength=255)
    type = models.CharField(maxlength=90)
    class Meta:
        db_table = '%spreference' % TABLE_PREFIX

class SessionData(models.Model):
    session_id = models.CharField(maxlength=96)
    expiry_time = models.DateTimeField()
    ip = models.CharField(maxlength=45)
    domain_name = models.CharField(maxlength=150)
    session_data = models.TextField()
    class Meta:
        db_table = '%ssession_data' % TABLE_PREFIX

class Style(models.Model):
    id = models.IntegerField(primary_key=True)
    createtime = models.DateTimeField()
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField()
    plugin_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(unique=True, maxlength=150)
    description = models.TextField(blank=True)
    content = models.TextField()
    class Meta:
        db_table = '%sstyle' % TABLE_PREFIX

class TemplateEngine(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=150)
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
    class Meta:
        db_table = '%stemplate' % TABLE_PREFIX

class UserGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    userID = models.IntegerField()
    groupID = models.IntegerField()
    lastupdatetime = models.DateTimeField()
    lastupdateby = models.IntegerField(null=True, blank=True)
    createtime = models.DateTimeField()
    class Meta:
        db_table = '%suser_group' % TABLE_PREFIX
