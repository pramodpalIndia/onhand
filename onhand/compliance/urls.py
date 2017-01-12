# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from onhand.dashboard.views import filter_completed_items_list
from . import views

urlpatterns = [
    url(r"^register$", views.registercompliance, name="compliance_addnew"),
]
