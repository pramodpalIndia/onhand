# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

# from allauth.account.views import login

from onhand.subscription.views import login

from onhand.users.views import logout
from onhand.subscription.views import register,validate_discount_code

from django.contrib import admin
from onhand.dashboard.sites import DashboardSite

admin.site = DashboardSite()
admin.sites.site = admin.site  # >= Django 1.9.5
admin.autodiscover()


urlpatterns = [url('^', include('onhand.subscription.urls'))]
urlpatterns +=  [url('^polls', include('onhand.polls.urls'))]
urlpatterns +=  [url('^app/', include('onhand.dashboard.urls',namespace='dashboard'))]
# urlpatterns +=  [url('^service/', include('onhand.compliance.urls',namespace='compliance'))]
urlpatterns +=  [url('^service/', include('onhand.compliance.urls',namespace='compliance'))]


urlpatterns += [
    url(r'^examples/', include('django_select2.urls')),
    url(r'^$', login,  name="login"),
    url(r"^login/$", login, name="account_login"),
    url(r"^logout/$", logout, name="account_logout"),
    # url(r"^login/$", views.login, name="ac_login"),
    # url(r'^registration/$', TemplateView.as_view(template_name='registration/register.html'), name='register'),
    url(r'^registration/$',register , name='register'),

    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    # url(r'^$', TemplateView.as_view(template_name='pages/welcome.html'), name='home'),
    # url(r'^$', ),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('onhand.users.urls', namespace='users')),
    # url(r'^accounts/', include('allauth.urls')),
    # url(r'^admin/', include(admin.site.urls)),



    # Your stuff: custom urls includes go here


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
