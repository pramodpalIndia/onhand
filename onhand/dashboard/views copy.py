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
from onhand.subscription.utils import complete_signup_prelim_user
from onhand.users.admin import MyUserAdmin
from onhand.users.exceptions import ImmediateHttpResponse
from onhand.users.forms import ServiceJurisdictionForm
from onhand.users.utils import get_next_redirect_url, get_request_param
# from .models import User

from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from onhand.subscription.adapter import get_adapter
from onhand.subscription import app_settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _
from suit_dashboard.layout import Grid, Row, Column
from suit_dashboard.views import DashboardView
from suit_dashboard.box import Box


from allauth.account.views import CloseableSignupMixin, RedirectAuthenticatedUserMixin, sensitive_post_parameters_m
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

from onhand.users.utils import (get_next_redirect_url, get_current_site)

# from . import app_settings
from .forms import DashboardForm


from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from suit_dashboard.layout import Grid, Row, Column
from suit_dashboard.views import DashboardView
from suit_dashboard.box import Box

from onhand.dashboard.boxes import BoxMachine


# class HomeView(DashboardView):
#     template_name = 'dashboard/main.html'
#     crumbs = (
#         {'url': 'admin:index', 'name': _('Home')},
#     )
#     grid = Grid(Row(Column(BoxMachine(), width=12)))
#
#     # grid = Grid(
#     #   Row(
#     #     Column(
#     #       Box(title='Row 1 column 1 box 1'),
#     #       Box(title='Row 1 column 1 box 2'),
#     #       width=6),
#     #     Column(
#     #       Box(title='Row 1 column 2 box 1'),
#     #       Box(title='Row 1 column 2 box 2'),
#     #       width=6),
#     #   ),
#     #   Row(
#     #     Column(
#     #       Box(title='Row 2 column 1 box 1'),
#     #       Box(title='Row 2 column 1 box 2'),
#     #       width=3),
#     #     Column(
#     #       Box(title='Row 2 column 2 box 1'),
#     #       Box(title='Row 2 column 2 box 2'),
#     #       width=5),
#     #     Column(
#     #       Row(
#     #         Column(
#     #           Box(title='R2 C3 R1 C1 B1'),
#     #           Box(title='R2 C3 R1 C1 B2'),
#     #           width=12)
#     #       ),
#     #       Row(
#     #         Column(
#     #           Box(title='R2 C3 R2 C1 B1'),
#     #           Box(title='R2 C3 R2 C1 B2'),
#     #           width=12)
#     #       ),
#     #       width=4),
#     #   )
#     # )
#




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
            print('self.form_valid(form) : ', self.form_invalid(form), self)

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
class HomeView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                FormView):
    template_name = "dashboard/main.html"
    form_class = DashboardForm
    redirect_field_name = "next"
    success_url = None


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        print('HomeView_dispatch', request.session.get('account_person', None))
        # args =[defaultservicetable]
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):

        print('HomeView_self.form_class', self.form_class)
        return self.form_class
        # return SignupForm

    def get_form_kwargs(self):
        print('HomeView_get_form_kwargs')
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        print('HomeView_get_success_url')
        ret = (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or self.success_url)
        print('def get_success_url(self):', self.redirect_field_name, self.success_url)
        return ret

    def form_valid(self, form):
        print('HomeView_valid')
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance

        self.user = form.save(self.request)
        try:
            return complete_signup_prelim_user(self.request, self.user, signal_kwargs=None)
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        print('HomeView_get_context_data')
        ret = super(HomeView, self).get_context_data(**kwargs)
        form = ret['form']
        return ret

home = HomeView.as_view()

# class UserRedirectView(LoginRequiredMixin, RedirectView):
#     permanent = False
#
#     def get_redirect_url(self):
#         return reverse('dashboard:home',
#                        kwargs={'username': self.request.user.username})
