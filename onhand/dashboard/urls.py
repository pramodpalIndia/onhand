# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from onhand.compliance.views import add_new_vendor_compliance, add_new_vendor_compliance_valid, \
    add_new_schedule_compliance, add_new_responsible_compliance, get_vendorcontactlist, get_vendorcontactdetails, \
    add_new_vendor_contact_compliance, add_new_compliance_action, add_new_complianceservice_upload
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
    url(r'^service/$', views.ohsrvrecordspop, name="ohservice"),
    url(r'^schedule/$', views.popupschedule, name="scheduleservice"),
    url(r'^serviceaction/$', views.popupserviceaction, name="serviceaction"),
    url(r'^coordinator/$', views.popupcoordinate, name="coordinateservice"),
    url(r'^newvendor/$', views.popupschedulenewvendor, name="newvendor"),
    url(r'^newvendorcontact/$', views.popupschedulenewvendorcontact, name="newvendorcontact"),
    url(r'^newvendor/ajax_complianceservice_addnewvendor/$', add_new_vendor_compliance, name="complianceservice_addnewvendor"),
    url(r'^newvendorcontact/ajax_complianceservice_addnewvendorcontact/$', add_new_vendor_contact_compliance, name="complianceservice_addnewvendorcontact"),
    url(r'^newvendor/ajax_complianceservice_newvendorvalid/$', add_new_vendor_compliance_valid, name="complianceservice_addnewvendor"),
    url(r'^schedule/ajax_complianceservice_addnewschedule/$', add_new_schedule_compliance, name="complianceservice_addnewschedule"),
    url(r'^schedule/ajax_complianceservice_addnewresponsible/$', add_new_responsible_compliance, name="complianceservice_addnewresponsible"),
    url(r'^schedule/ajax_vendorcontactlist/$', get_vendorcontactlist, name="complianceservice_getvendorcontactlist"),
    url(r'^schedule/ajax_vendorcontactdetails/$', get_vendorcontactdetails, name="complianceservice_getvendorcontactdetails"),
    url(r'^serviceaction/ajax_complianceservice_addnewaction/$', add_new_compliance_action, name="complianceservice_addnewaction"),
    url(r'^service/ajax_complianceservice_upload/$', add_new_complianceservice_upload, name="complianceservice_upload"),

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
