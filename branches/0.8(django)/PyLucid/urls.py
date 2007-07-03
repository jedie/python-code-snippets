"""
    PyLucid.urls
    ~~~~~~~~~~~~

    The urls, manage the PyLucid CMS.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL, see LICENSE for more details.
"""

from django.conf.urls.defaults import include, patterns

from PyLucid import settings

if settings.ENABLE_INSTALL_SECTION == True:
    # The _install section is activated.
    # -> insert all available _install views
    urls = (
        # RUN A VIEW
        (
            (
                '^%s/'
                '(?P<module_name>[^/]*?)/'
                '(?P<method_name>[^/]*?)/'
                '(?P<url_args>.*?)$'
            ) % settings.INSTALL_URL_PREFIX,
            "PyLucid.install.index.run_method",
        ),
        # LOGOUT
        (
            '^%s/logout/$' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.logout'
        ),
        # INSTALL MENU
        (
            '^%s/$' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.menu'
        ),
    )
else:
    # _install section is deactivated.
    urls = ()

urls += (
    # DJANGO ADMIN PANEL
    (
        r'^%s/' % settings.ADMIN_URL_PREFIX,
        include('django.contrib.admin.urls')
    ),
    # COMMAND VIEW
    (
        (
            '^%s/'
            '(?P<page_id>\d+)/'
            '(?P<module_name>[^/]*?)/'
            '(?P<method_name>[^/]*?)/'
            '(?P<url_args>.*?)$'
        ) % settings.COMMAND_URL_PREFIX,
        'PyLucid.index.handle_command'
    ),
    # CMS PAGE VIEW
    # For the cach system we make a hash from the url and in a normal
    # cms page request the url contains only the cms page shortcuts.
    # The shortcuts contains only these chars: [a-zA-Z0-9_/]
    (r'^([\w/]*?)/?$', 'PyLucid.index.index'),
    # STATIC FILES
    # Using this method is inefficient and insecure.
    # Do not use this in a production setting. Use this only for development.
    # http://www.djangoproject.com/documentation/static_files/
    (
        '^%s(?P<path>.*)$' % settings.MEDIA_URL,
        'django.views.static.serve',
        {'document_root': './%s' % settings.MEDIA_URL}
    ),
)

urlpatterns = patterns('', *urls)
