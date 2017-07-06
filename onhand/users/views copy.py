# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from onhand.compliance.models import ServiceJurisdiction
from onhand.dashboard.boxes import BoxMachine
from onhand.dashboard.userservicelist import Userservicelist
from onhand.examples.admin import CountryExampleForm, KitchenSinkForm
from onhand.examples.models import CountryExample
from onhand.subscription import app_settings
from onhand.users.admin import MyUserAdmin
from onhand.users.forms import ServiceJurisdictionForm
from onhand.users.utils import get_next_redirect_url, get_request_param
from .models import User

from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from onhand.subscription.adapter import get_adapter
# from onhand.subscription import app_settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _
from suit_dashboard.layout import Grid, Row, Column
from suit_dashboard.views import DashboardView
from suit_dashboard.box import Box


from allauth.account.views import CloseableSignupMixin
from crispy_forms.tests import test_settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import (HttpResponseRedirect, Http404,
                         HttpResponsePermanentRedirect)
from django.http import JsonResponse
from django.shortcuts  import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.contrib.sites.models import Site

from onhand.compliance.models import ComplianceService, ServiceJurisdiction

from .utils import (get_next_redirect_url, get_current_site)

# from . import app_settings





def _ajax_response(request, response, form=None):
    if request.is_ajax():
        if (isinstance(response, HttpResponseRedirect) or isinstance(
                response, HttpResponsePermanentRedirect)):
            redirect_to = response['Location']
        else:
            redirect_to = None
        response = get_adapter(request).ajax_response(
            request,
            response,
            form=form,
            redirect_to=redirect_to)
    return response

class AjaxCapableProcessFormViewMixin(object):

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        print('Class AjaxCapableProcessFormViewMixin -form_class:',form_class)
        # print('Class AjaxCapableProcessFormViewMixin -form.is_valid():',form.is_valid())
        if form.is_valid():
            response = self.form_valid(form)
        else:
            response = self.form_invalid(form)
            print('self.form_invalid(form) : ', self.form_invalid(form),self)
        # print(response)
        return _ajax_response(self.request, response, form=form)


class DashboardStatisticsView(DashboardView):
    template_name = 'dashboard/main.html'
    # model = User
    # These next two lines tell the view to index lookups by username
    # slug_field = 'username'
    # slug_url_kwarg = 'username'
    # grid = Grid(Row(Column(BoxMachine(), width=12)))
    grid = Grid(
      Row(
        Column(
          Box(html_id='allitems',title=1,description='All Items'),
          width=1),
        Column(
          Box(html_id='services',title=1,description='Services'),
          width=1),
        Column(
              Box(html_id='insurance',title='2',description='Insurance'),
              width=1),
        Column(
              Box(html_id='filing',title='3',description='Filings & Permits'),
              width=1),
        Column(
              Box(html_id='violation',title='1',description='Violations & Suits'),
              width=1),
        Column(
              Box(html_id='current',title='20',description='Current'),
              width=1),
        Column(
              Box(html_id='attention',title='0',description='Coming Due'),
              width=1),
        Column(
              Box(html_id='pastdue',title='0',description='Past Due'),
              width=1),
      ),
        Row(
            Column(
                Box(),
                width=12),
        ),
        Row(
            Column(Row(
                Column(
                    Box(html_id='filtertitle', title='Showing :', description=''),
                    width=1),
                Column(
                    Box(html_id='showfilters', title='All Items'),
                    width=1))),
        ),

    )

# class HomeView(LoginRequiredMixin, DashboardStatisticsView, TemplateView):
class HomeView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/main.html'
    # template_name = 'examples/city/change_list.html'
    # form = KitchenSinkForm
    # form_class = MyUserAdmin
    # grid = Grid(Row(Column(BoxMachine(), width=12)))
    # model = User
    # These next two lines tell the view to index lookups by username
    # slug_field = 'username'
    # slug_url_kwarg = 'username'
    # model = ServiceJurisdiction
    success_url = 'accounts/signup/'
    form = ServiceJurisdictionForm
    # form_class = ServiceJurisdictionForm
    # inlines = []

    # def get(self, request, *args, **kwargs):
    #     """
    #     Handles GET requests and instantiates blank versions of the form
    #     and its inline formsets.
    #     """
    #     self.object = None
    #     form_class = self.form_class
    #     form = form_class.get_f
    #
    #     return self.render_to_response(
    #         self.get_context_data(form=form,
    #                               ingredient_form=ServiceJurisdictionForm
    #                             ))

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        # result_count = 0
        return CountryExample.objects.all()

    def get_context_data(self, **kwargs):

        print('SignupServiceView_get_context_data')
        # ret = super(HomeView, self).get_context_data(**kwargs)
        # ret = SignupServiceView.get_context_data(**kwargs)
        # form = ret['form']
        # defaultservicetable = NameTable(data)
        # ret.update({"ServiceJurisdiction": ServiceJurisdiction.objects.all()})
        # ret.update({"InsuranceJurisdiction": InsuranceTypeJurisdiction.objects.all()})
        # ret.update({"SubmissionJurisdiction": SubmissionTypeJurisdiction.objects.all()})
        # ret.update({"defaultservicetable": defaultservicetable})
        return None

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        # return reverse('dashboard:home',
        #                kwargs={'username': self.request.user.username})
        # print('Users , get_redirect_url')
        return reverse('dashboard:home',None)
        # return None


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['user_id', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'



class LogoutView(TemplateResponseMixin, View):

    template_name = "account/logout.html"
    redirect_field_name = "next"

    def get(self, *args, **kwargs):
        if app_settings.LOGOUT_ON_GET:
            return self.post(*args, **kwargs)
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        url = self.get_redirect_url()
        if self.request.user.is_authenticated():
            self.logout()
        return redirect(url)

    def logout(self):
        get_adapter(self.request).add_message(
            self.request,
            messages.SUCCESS,
            'account/messages/logged_out.txt')
        auth_logout(self.request)

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_value = get_request_param(self.request,
                                                 self.redirect_field_name)
        ctx.update({
            "redirect_field_name": self.redirect_field_name,
            "redirect_field_value": redirect_field_value})
        return ctx

    def get_redirect_url(self):
        return (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or get_adapter(
                    self.request).get_logout_redirect_url(
                        self.request))

logout = LogoutView.as_view()
