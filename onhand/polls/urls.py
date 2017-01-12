from django.conf.urls import url
from django.conf.urls import  include, url
from django.contrib import admin
from onhand.polls.admin import user_admin_site


from . import views

admin.autodiscover()

# urlpatterns = patterns('',
#     url(r'^admin/', include(admin.site.urls)),
#     url(r'^', include(user_admin_site.urls)),
#     url(r'^', include('myapp.urls')),
# )

app_name = 'polls'
urlpatterns = [
    url(r'^', include(user_admin_site.urls)),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
