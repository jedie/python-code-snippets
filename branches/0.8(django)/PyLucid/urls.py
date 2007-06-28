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

if settings.INSTALL_PASS and len(settings.INSTALL_PASS)>=8:
    # The _install section is activated
    urls = (
        (
            (
                '^%s/'
                '(?P<module_name>[^/]*?)/'
                '(?P<method_name>[^/]*?)/'
                '(?P<url_args>.*?)$'
            ) % settings.INSTALL_URL_PREFIX,
            "PyLucid.install.index.run_method",
        ),
        (
            '^%s/logout/$' % settings.INSTALL_URL_PREFIX,
            'PyLucid.install.index.logout'
        ),
    )
else:
    urls = ()

urls += (
    (r'^%s/' % settings.ADMIN_URL_PREFIX, include('django.contrib.admin.urls')),
    (
        '^%s/$' % settings.INSTALL_URL_PREFIX,
        'PyLucid.install.index.menu'
    ),
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
    # For the cach system we make a hash from the url and in a normal
    # cms page request the url contains only the cms page shortcuts.
    # The shortcuts contains only these chars: [a-zA-Z0-9_/]
    (r'^([\w/]*?)/?$', 'PyLucid.index.index'),
)

#print urls

urlpatterns = patterns('', *urls)