
from PyLucid import settings

class StaticTags(object):
    """
    A dict like object with tag information who not generated by plugins/modules
    """
    def __init__(self, request):
        self.request = request
        
        self.page_msg = request.page_msg
        self.current_page = request.current_page
        
        self.tags = {
            "page_title": self.current_page.title,
            "page_keywords": self.current_page.keywords,
            "page_description": self.current_page.description,
            "page_datetime": self.current_page.get_createtime_string(),
            "page_last_modified": self.current_page.get_lastupdatetime_string(),
            "powered_by": self.get_powered_by,
            "script_login": self.get_login_link,
        }
        
        if getattr(request, "must_login", False):
            # The module_manager set this attribute
            self.tags["robots"] = "NONE,NOARCHIVE"
        else:
            self.tags["robots"] = "index,follow"


    def __contains__(self, key):
        if not key in self.tags:
            return False
        else:
            return True
        
    def __getitem__(self, key):
        value = self.tags[key]
        if isinstance(value, basestring):
            return value
        else:
            return value()
        
    def __setitem__(self, key, value):
        self.tags[key] = value
    
    def get_powered_by(self):
        html = (
            '<a href="http://www.pylucid.org">PyLucid v%s</a>'
        ) % settings.PYLUCID_VERSION_STRING
        return html
    
    def get_login_link(self):
        if self.request.user.username != "":
            # User is loged in
            return '<a href="/_admin/logout">logout [%s]</a>' % self.request.user.username
        else:
            return '<a href="/_admin">login</a>'