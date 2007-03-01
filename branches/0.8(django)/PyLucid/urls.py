from django.conf.urls.defaults import *

from PyLucid import settings
from PyLucid.install.urls import get_install_view_urls

urls = (
    (r'^_admin/', include('django.contrib.admin.urls')),
)

    # insert all available install views
urls += get_install_view_urls(
    '^%s/(?P<install_pass>[^/]*?)/%%s/(.*?)$' % settings.INSTALL_URL_PREFIX
)

urls += (
    (
        (
            '^%s/'
            '(?P<install_pass>[^/]*?)/$'
        ) % settings.INSTALL_URL_PREFIX,
        'PyLucid.install.index.index'
    ),
    (
        (
            '^%s/'
            '(?P<page_id>\d+)/'
            '(?P<module_name>[^/]*?)/'
            '(?P<method_name>[^/]*?)/'
            '(?P<url_info>.*?)$'
        ) % settings.COMMAND_URL_PREFIX,
        'PyLucid.index.handle_command'
    ),
    (r'^(.*?)$', 'PyLucid.index.index'),
)

urlpatterns = patterns('', *urls)