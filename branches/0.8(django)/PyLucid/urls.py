from django.conf.urls.defaults import *

from PyLucid.install.urls import get_urls

urls = (

    #~ (r'^_inspectdb/$', 'PyLucid.install.views.inspectdb'),
    #~ (r'^_syncdb/$', 'PyLucid.install.views.syncdb'),
    #~ (r'^_createuser/$', 'PyLucid.install.views.create_user'),
    #~ (r'^_update/$', 'PyLucid.install.views_install.update'),
    #~ (r'^_info/(.*?)$', 'PyLucid.install.views.info'),

    (r'^_admin/', include('django.contrib.admin.urls')),
)

urls += get_urls(base_url='^_install/(?P<install_pass>[^/]*?)/%s/(.*?)$')

urls += (
    (r'^_install/?(?P<install_pass>[^/]*?)/?$', 'PyLucid.install.index.index'),
    (r'^(.*?)$', 'PyLucid.index.index'),
)

urlpatterns = patterns('', *urls)