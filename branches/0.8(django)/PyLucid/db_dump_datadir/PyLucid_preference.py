table = 'PyLucid_preference'
fields = ['id', 'plugin_id', 'name', 'description', '_value', '_default_value', 'field_type', 'lastupdatetime', 'lastupdateby_id']
#default item format: "fieldname":("type", "value")
default = {}
records = [
[1L, None, u'index page', u'This is the default page that a site visitor will see if they arrive at your CMS without specifying a particular page.', u'I1\n.', u'I1\n.', u'ForeignKey,Page', '2007-07-06 03:55:09', None]
[2L, None, u'default markup', u'This specifies what the default text markup parser will be for new pages. You can set it to the name of a plugin markup parser ("textile" and "markdown" are currently available), or "none".', u'I2\n.', u'I2\n.', u'ForeignKey,Markup', '2007-07-06 03:55:09', None]
[3L, None, u'default template', u'This is the template that will be assigned to new pages when they are created.', u'I1\n.', u'I1\n.', u'ForeignKey,Template', '2007-07-06 03:55:09', None]
[4L, None, u'default stylesheet', u'This is the stylesheet taht will be assigned to new pages when they are created.', u'I1\n.', u'I1\n.', u'ForeignKey,Stylesheet', '2007-07-06 03:55:09', None]
[5L, None, u'auto shortcuts', u'Auto rebuild the page shortcut on every page edit?', u'I01\n.', u'I01\n.', u'Boolean', '2007-07-06 03:55:09', None]
]
