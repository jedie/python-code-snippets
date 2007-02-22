from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^PyLucid/', include('PyLucid.apps.foo.urls.foo')),
    (r'^_inspectdb/$', 'PyLucid.install.views.inspectdb'),
    (r'^_syncdb/$', 'PyLucid.install.views.syncdb'),
    (r'^_createuser/$', 'PyLucid.install.views.create_user'),
    (r'^_update/$', 'PyLucid.install.views_install.update'),
    (r'^_info/(.*?)$', 'PyLucid.install.views.info'),
    (r'^_install/(.*?)$', 'PyLucid.install.views.index'),
    (r'^_admin/', include('django.contrib.admin.urls')),

    (r'^(.*?)$', 'PyLucid.display_page.display_page'),
)
