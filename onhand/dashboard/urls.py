# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from onhand.dashboard.views import filter_completed_items_list
from . import views

urlpatterns = [
    # url(
    #     regex=r'^$',
    #     view=views.UserListView.as_view(),
    #     name='list'
    # ),
    # url(
    #     regex=r'^~redirect/$',
    #     view=views.UserRedirectView.as_view(),
    #     name='redirect'
    # ),
    url(
        regex=r'^$',
        # regex=r'^(?P<username>[\w.@+-]+)/$',
        # view=views.UserDetailView.as_view(),
        view=views.HomeView.as_view(),
        name='home'
    ),
    # url(r'^customers/$', views.customers, name='customers'),
    url(r'^alerts/$', views.alerts, name='alerts'),
    url(r'^dismiss-alert/$', views.customer_management_dismiss_alert,
        name='dismiss-alert'),
    url(r'^ajax_completion_filter$', filter_completed_items_list, name="getfilteredservicelist"),
    url(r'^schedule/$', views.popupschedule, name="scheduleservice"),
    url(r'^newvendor/$', views.popupschedulenewvendor, name="newvendor"),
    # url(
    #     regex=r'^~update/$',
    #     view=views.UserUpdateView.as_view(),
    #     name='update'
    # ),

# E-mail
#     url(r"^email/$", views.email, name="account_email"),
#     url(r"^confirm-email/$", views.email_verification_sent,
#         name="account_email_verification_sent"),
]
