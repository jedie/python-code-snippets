from django.conf.urls.defaults import include, patterns

from PyLucid import settings
from PyLucid.install.urls import get_install_view_urls

# all available install views
urls = get_install_view_urls(
    '^%s/(?P<install_pass>[^/]*?)/%%s/(.*?)$' % settings.INSTALL_URL_PREFIX
)
urls += (
    (r'^%s/' % settings.ADMIN_URL_PREFIX, include('django.contrib.admin.urls')),
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
            '(?P<url_args>.*?)$'
        ) % settings.COMMAND_URL_PREFIX,
        'PyLucid.index.handle_command'
    ),
    (r'^(.*?)$', 'PyLucid.index.index'),
)

urlpatterns = patterns('', *urls)
