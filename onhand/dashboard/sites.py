# -*- coding: utf-8 -*-
# dashboard/sites.py

from __future__ import unicode_literals
from django.contrib.admin.sites import AdminSite
from django.conf.urls import url
from suit_dashboard.urls import get_refreshable_urls

from .views import HomeView


class DashboardSite(AdminSite):
  """A Django AdminSite to allow registering custom dashboard views."""
  def get_urls(self):
    urls = super(DashboardSite, self).get_urls()
    custom_urls = [
        url(r'^$', self.admin_view(HomeView.as_view()), name='index')
    ]

    del urls[0]
    # return custom_urls + urls
    return custom_urls + urls + get_refreshable_urls(self.admin_view)
