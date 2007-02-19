from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^PyLucid/', include('PyLucid.apps.foo.urls.foo')),
    (r'^_syncdb/$', 'PyLucid.install.views_install.syncdb'),
    (r'^_createuser/$', 'PyLucid.install.views_install.create_user'),
    (r'^_update/$', 'PyLucid.install.views_install.update'),
    (r'^_install/(.*?)$', 'PyLucid.install_views.index'),
    (r'^_admin/', include('django.contrib.admin.urls')),

    (r'^(.*?)$', 'PyLucid.display_page.display_page'),
)
