# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from onhand.compliance.models import ServiceJurisdiction, ComplianceServiceSchedule, v_provider_jurisdiction, \
    ComplianceResponsibility, v_last_compliance_service_action, Factor, FactorValue
from onhand.dashboard.boxes import BoxMachine
from onhand.dashboard.tables import ServicesTable, SubscribedServicesTable
from onhand.dashboard.userservicelist import Userservicelist
from onhand.examples.admin import CountryExampleForm, KitchenSinkForm
from onhand.examples.models import CountryExample
from onhand.management.models import v_SubscribedServicesTable, v_dashboard_service, v_company_people, Basis
from onhand.subscription.models import Subscription, CompanyPersonRole
from onhand.users.admin import MyUserAdmin
from onhand.users.exceptions import ImmediateHttpResponse
# from onhand.users.forms import ServiceJurisdictionForm, DashboardForm
from onhand.users.models import UserPreference, User
from .forms import DashboardForm, ExampleForm, ScheduleForm
from onhand.users.utils import get_next_redirect_url, get_request_param, get_login_redirect_url
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

from onhand.management import app_settings

from .models import Alert
from .tables import AlertsTable
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context, loader, TemplateDoesNotExist
from django.template.context import RequestContext
from django_tables2 import RequestConfig

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password1', 'password2'))


def _ajax_response(request, response, form=None):
    if request.is_ajax():
        if (isinstance(response, HttpResponseRedirect) or isinstance(
                response, HttpResponsePermanentRedirect)):
            redirect_to = response['Location']
            print('Dashboard _ajax_response -redirect_to',redirect_to)
        else:
            redirect_to = None
            print('Dashboard _ajax_response -request,response,form,redirect_to', request,response,form,redirect_to)
        response = get_adapter(request).ajax_response(
            request,
            response,
            form=form,
            redirect_to=redirect_to)
    return response


class RedirectAuthenticatedUserMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        # if request.user.is_authenticated() and \
        #             app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
        #     self.request = request
        #     print('RedirectAuthenticatedUserMixin - dispatch', self.request)
        #     # (end WORKAROUND)
        #     response = super(RedirectAuthenticatedUserMixin,
        #                      self).dispatch(request,
        #                                     *args,
        #                                     **kwargs)
        #     print('RedirectAuthenticatedUserMixin kwargs.items():', kwargs , response)
        #     for key, value in kwargs.items():
        #         print("%s = %s") % (key, value)
        # else:
        #     response=None
        #
        # return response
        if request.user.is_authenticated() and \
                app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
            redirect_to = self.get_authenticated_redirect_url()
            print('RedirectAuthenticatedUserMixin - redirect_to', redirect_to)
            # response = HttpResponseRedirect(redirect_to)
            response = super(RedirectAuthenticatedUserMixin,
                             self).dispatch(request,
                                            *args,
                                            **kwargs)
            print('RedirectAuthenticatedUserMixin - response', response)
            print('_ajax_response(request, response)', _ajax_response(request, response))
            # return _ajax_response(request, response)
            # for key, value in kwargs.items():
            #     print("%s = %s") % (key, value)
        else:
            print('RedirectAuthenticatedUserMixin', )
            redirect_to = reverse('login')
            print('RedirectAuthenticatedUserMixin - redirect_to', redirect_to)
            response = HttpResponseRedirect(redirect_to)
            # response = super(RedirectAuthenticatedUserMixin,
            #                     self).dispatch(request,
            #                                     *args,
            #                                   **kwargs)
            # print('RedirectAuthenticatedUserMixin kwargs.items():',kwargs)
            # for key, value in kwargs.items():
            #     print("%s = %s") % (key, value)
        return response

    def get_authenticated_redirect_url(self):
        print('get_authenticated_redirect_url', self.redirect_field_name )
        redirect_field_name = self.redirect_field_name
        return get_login_redirect_url(self.request,
                                      url=self.get_success_url(),
                                      redirect_field_name=redirect_field_name)



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


class DashboardStatisticsView(DashboardView):
    # template_name = 'dashboard/main.html'
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

# class HomeView(DashboardView):
#     template_name = 'dashboard/main.html'
#     crumbs = (
#         {'url': 'admin:index', 'name': _('Home')},
#     )
#     # grid = Grid(
#     #             Row(
#     #                 Column(
#     #                     Box(html_id='allitems', title=1, description='All Items'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='services', title=1, description='Services'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='insurance', title='2', description='Insurance'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='filing', title='3', description='Filings & Permits'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='violation', title='1', description='Violations & Suits'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='current', title='20', description='Current'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='attention', title='0', description='Coming Due'),
#     #                     width=1),
#     #                 Column(
#     #                     Box(html_id='pastdue', title='0', description='Past Due'),
#     #                     width=1),
#     #             ),
#     #             Row(
#     #                 Column(
#     #                     Box(),
#     #                     width=12),
#     #             ),
#     #             Row(
#     #                 Column(Row(
#     #                     Column(
#     #                         Box(html_id='filtertitle', title='Showing :', description=''),
#     #                         width=1),
#     #                     Column(
#     #                         Box(html_id='showfilters', title='All Items'),
#     #                         width=1))),
#     #             ),
#     #
#     #         )


class HomeView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                TemplateView):
    # grid = Grid(Row(Column(BoxMachine(), width=12)))
    print('HomeView -Class')

    form_class = DashboardForm
    # form_class = ExampleForm
    # template_name = "Regsitration/register." + app_settings.TEMPLATE_EXTENSION
    template_name = 'dashboard/main.html'
    context_object_name = 'onhand_dashborad'
    success_url = None
    redirect_field_name = "next"
    loged_user_subscription_id = None
    loged_user_default_company = None


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        print('HomeView -Dispatch' ,self.get_success_url(), request )
        print(request.session['_auth_user_id']);
        print('Printing Default Company for user')

        print( UserPreference.objects.get(user = request.session['_auth_user_id'],uprt_code= 'DFTCMP').uprf_value)
        # subscription_id_user = Subscription.objects.get()
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        print('HomeView - get_form_kwargs')
        kwargs = super(HomeView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_class(self):
        print('HomeView - get_form_class()')
        # return get_form_class(app_settings.FORMS, 'register', self.form_class)

        return DashboardForm

    def form_valid(self, form):
        success_url = self.get_success_url()
        print('HomeView - form_valid')
        try:
            print('Save')
            return form.save(self.request, redirect_url=success_url)
        except ImmediateHttpResponse as e:
            return e.response

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        print('HomeView -get_sucess_url ' ,self, self.request,
            self.redirect_field_name, self.success_url)
        ret = (get_next_redirect_url(
            self.request,
            self.redirect_field_name) or self.success_url)
        print('Dashboard - get_success_url' , ret)
        return ret

    def get_context_data(self, **kwargs):
        print('HomeView - get_context_data')
        print(self.request.session.get('user'))
        ret = super(HomeView, self).get_context_data(**kwargs)
        # example_form = ExampleForm
        # grid = Grid(Row(Column(BoxMachine(), width=12)))

        # ret.update({"dashboard_grid": grid})
        # ret.update({"example_form": example_form})
        # ret = HomeView.get_context_data(**kwargs)
        # form = ret['form']
        # search = None
        # print('req.session[form_data]') , self.req.session['form_data']

        service_count_current = v_dashboard_service.objects.filter(subscriber=316, due_status='current').count()
        service_count_coming_due = v_dashboard_service.objects.filter(subscriber=316, due_status='coming due').count()
        service_count_past_due = v_dashboard_service.objects.filter(subscriber=316, due_status='past due').count()

        subscription_count_current =service_count_current
        subscription_count_coming_due = service_count_coming_due
        subscription_count_past_due  = service_count_past_due
        subscription_count_all = subscription_count_current +subscription_count_coming_due+subscription_count_past_due

        defaultservicetable = SubscribedServicesTable(v_dashboard_service.objects.filter(subscriber=316,csac_service_date__isnull=True).order_by('ctyp_desc','csac_service_date','csrv_due_date'))
        # defaultservicetable = SubscribedServicesTable(v_SubscribedServicesTable.objects.filter(csac_date__isnull=True))
        # defaultservicetable = ServicesTable(ServiceJurisdiction.objects.all())
        defaultservicetable.paginate(page=self.request.GET.get('page', 1), per_page=9)
        # # ret.update({"ServiceJurisdiction": ServiceJurisdiction.objects.all()})
        # # ret.update({"InsuranceJurisdiction": InsuranceTypeJurisdiction.objects.all()})
        # # ret.update({"SubmissionJurisdiction": SubmissionTypeJurisdiction.objects.all()})
        ret.update({"subscription_count_all": subscription_count_all})
        ret.update({"service_count_total": (service_count_current+service_count_coming_due+service_count_past_due)})
        ret.update({"subscription_count_current": subscription_count_current})
        ret.update({"subscription_count_coming_due": subscription_count_coming_due})
        ret.update({"subscription_count_past_due": subscription_count_past_due})

        ret.update({"defaultservicetable": defaultservicetable})
        return ret



@login_required
def alerts(req):
    req.session['form_data'] = None
    search = None
    alerts = Alert.objects.all()
    # alerts = Alert.objects.filter(dealer=req.dealer.id, is_read=False)

    if req.method == 'POST':
        search = req.POST.get('search', None)

        if search:
            alerts = alerts.filter(
                Q(customer__customer_name__icontains=search) |
                Q(customer__customer_number__icontains=search)
            )

    # render the alerts table with django-tables
    table = AlertsTable(alerts)
    RequestConfig(req, paginate={'per_page': 3}).configure(table)
    return render(
        req,
        'dashboard/main.html', {
            'table': table,
            'alerts': alerts,
            'search': search
        }
    )


def customer_management_dismiss_alert(req):
    """This view is intended to use via AJAX"""
    alert_pk = req.POST.get('pk', None)

    print('This would have deleted Alert : ', alert_pk)
    alert = get_object_or_404(req.customer.alert_set, pk=alert_pk)

    alert.is_read = True
    alert.save()
    return HttpResponse('')


def filter_completed_items_list(req):
    """This view is intended to use via AJAX"""
    print('filter_completed_items_list Ajax been called,req.method', req.method)

    if req.method == 'POST':
        print('req.method ',req.method)
        completedfilter_checked = req.POST.get('completedfilter_checked', None)
        pastduefilter_checked = req.POST.get('pastduefilter_checked', None)
        comingduefilter_checked = req.POST.get('comingduefilter_checked', None)
        currentduefilter_checked = req.POST.get('currentduefilter_checked', None)
        print('filter_checked ', completedfilter_checked, currentduefilter_checked, comingduefilter_checked,
              pastduefilter_checked)


    if req.method == 'GET':
        completedfilter_checked = req.GET.get('completedfilter_checked', None)
        pastduefilter_checked = req.GET.get('pastduefilter_checked', None)
        comingduefilter_checked = req.GET.get('comingduefilter_checked', None)
        currentduefilter_checked = req.GET.get('currentduefilter_checked', None)
        print('filter_checked ', completedfilter_checked, currentduefilter_checked, comingduefilter_checked, pastduefilter_checked )

    if completedfilter_checked !=None and  currentduefilter_checked==None and comingduefilter_checked==None and pastduefilter_checked == None:
        print('filter_checked1 ', completedfilter_checked, pastduefilter_checked)
        if completedfilter_checked == 'false':
            defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
                            'ctyp_desc', 'csrv_due_date'))

        if completedfilter_checked == 'true':
            defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316).exclude(
                            basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

    if currentduefilter_checked != None:
        print('filter_checked2 ', completedfilter_checked, pastduefilter_checked)
        if currentduefilter_checked == 'false':
            if completedfilter_checked == 'false':
                defaultservicetable = SubscribedServicesTable(
                    v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
                        'ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                    v_dashboard_service.objects.filter(subscriber=316).exclude(
                        basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

        if currentduefilter_checked == 'true':
            if completedfilter_checked == 'false':
                defaultservicetable = SubscribedServicesTable(
                    v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True,
                                                       due_status='current').order_by('ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                    v_dashboard_service.objects.filter(subscriber=316, due_status='current').exclude(
                        basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

    if comingduefilter_checked != None:
        print('filter_checked2 ', completedfilter_checked, pastduefilter_checked)
        if comingduefilter_checked == 'false':
            if completedfilter_checked == 'false':
                 defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
                            'ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316).exclude(
                            basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

        if comingduefilter_checked == 'true':
            if completedfilter_checked == 'false':
                defaultservicetable = SubscribedServicesTable(
                                    v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True,
                                                                       due_status='coming due').order_by('ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                                    v_dashboard_service.objects.filter(subscriber=316, due_status='coming due').exclude(
                                        basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))


    if pastduefilter_checked != None:
        print('filter_checked2 ', completedfilter_checked, pastduefilter_checked)
        if pastduefilter_checked == 'false':
            if completedfilter_checked == 'false':
                 defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
                            'ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                        v_dashboard_service.objects.filter(subscriber=316).exclude(
                            basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

        if pastduefilter_checked == 'true':
            if completedfilter_checked == 'false':
                defaultservicetable = SubscribedServicesTable(
                                    v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True,
                                                                       due_status='past due').order_by('ctyp_desc', 'csrv_due_date'))

            if completedfilter_checked == 'true':
                defaultservicetable = SubscribedServicesTable(
                                    v_dashboard_service.objects.filter(subscriber=316, due_status='past due').exclude(
                                        basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))

    return render(
        req,
        'dashboard/dashboard_table_body.html', {
            'defaultservicetable': defaultservicetable,

        })

    # req.update({"defaultservicetable": defaultservicetable})
    # # RequestConfig(req, paginate={'per_page': 3}).configure(defaultservicetable)
    # return HttpResponse(req)
    # return render(
    #     req.update({"defaultservicetable": defaultservicetable})
    # )



# def filter_completed_items_list(req):
#     """This view is intended to use via AJAX"""
#     print('filter_completed_items_list Ajax been called,req.method', req.method)
#
#     if req.method == 'POST':
#         print('req.method ',req.method)
#         completedfilter_checked = req.POST.get('completedfilter_checked', None)
#         print('filter_checked ', completedfilter_checked)
#
#     if req.method == 'GET':
#         print('req.method ',req.method)
#         # recurringfilter_checked = req.GET.get('recurringfilter_checked', None)
#         # nonrecurringfilter_checked = req.GET.get('nonrecurringfilter_checked', None)
#         completedfilter_checked = req.GET.get('completedfilter_checked', None)
#         pastduefilter_checked = req.GET.get('pastduefilter_checked', None)
#         print('filter_checked ', completedfilter_checked, pastduefilter_checked )
#
#     # if completedfilter_checked !=None:
#     #     if completedfilter_checked == 'false':
#     #         defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
#     #                         'ctyp_desc', 'csrv_due_date'))
#     #
#     #     if completedfilter_checked == 'true':
#     #         defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316).exclude(
#     #                         basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))
#
#     # if recurringfilter_checked != None and nonrecurringfilter_checked and completedfilter_checked !=None:
#     #     if completedfilter_checked == 'false':
#     #         if recurringfilter_checked == 'false':
#     #             if nonrecurringfilter_checked == 'false':
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).exclude(
#     #                         basi_code='ONCE').order_by('ctyp_desc',
#     #                                                    'csrv_due_date'))
#     #             else:
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
#     #                         'ctyp_desc',
#     #                         'csrv_due_date'))
#     #
#     #         else:
#     #             if nonrecurringfilter_checked == 'false':
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).exclude(
#     #                         basi_code='ONCE').order_by('ctyp_desc',
#     #                                                    'csrv_due_date'))
#     #             else:
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
#     #                         'ctyp_desc',
#     #                         'csrv_due_date'))
#     #
#     #     if completedfilter_checked == 'true':
#     #         if recurringfilter_checked == 'false':
#     #             if nonrecurringfilter_checked == 'false':
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316).exclude(
#     #                         basi_code='ONCE').order_by('ctyp_desc',
#     #                                                    'csrv_due_date'))
#     #             else:
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316,basi_code='ONCE').order_by(
#     #                         'ctyp_desc',
#     #                         'csrv_due_date'))
#     #
#     #         else:
#     #             if nonrecurringfilter_checked == 'false':
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316).exclude(
#     #                         basi_code='ONCE').order_by('ctyp_desc',
#     #                                                    'csrv_due_date'))
#     #             else:
#     #                 defaultservicetable = SubscribedServicesTable(
#     #                     v_dashboard_service.objects.filter(subscriber=316).order_by(
#     #                         'ctyp_desc',
#     #                         'csrv_due_date'))
#
#     if pastduefilter_checked != None:
#         if pastduefilter_checked == 'false':
#             if completedfilter_checked != None:
#                 if completedfilter_checked == 'false':
#                     defaultservicetable = SubscribedServicesTable(
#                         v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).order_by(
#                             'ctyp_desc', 'csrv_due_date'))
#
#                 if completedfilter_checked == 'true':
#                     defaultservicetable = SubscribedServicesTable(
#                         v_dashboard_service.objects.filter(subscriber=316).exclude(
#                             basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))
#
#         if pastduefilter_checked == 'true':
#             if completedfilter_checked != None:
#                 if completedfilter_checked == 'false':
#                                 defaultservicetable = SubscribedServicesTable(
#                                     v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True,
#                                                                        due_status='past due').order_by(
#                                         'ctyp_desc', 'csrv_due_date'))
#
#                 if completedfilter_checked == 'true':
#                                 defaultservicetable = SubscribedServicesTable(
#                                     v_dashboard_service.objects.filter(subscriber=316, due_status='past due').exclude(
#                                         basi_code='ONCE').order_by('ctyp_desc', 'csrv_due_date'))
#
#
#         # defaultservicetable = SubscribedServicesTable(
#         # v_dashboard_service.objects.filter(subscriber=316, csac_service_date__isnull=True).exclude(
#         #     basi_code='ONCE').order_by('ctyp_desc','csrv_due_date'))
#
#     # req.v_SubscribedServicesTable.objects.filter(csac_date__isnull=False)
#
#     # print(defaultservicetable.agen_code.__str__());
#     # RequestConfig(req, paginate={'per_page': 3}).configure(defaultservicetable)
#
#     # return HttpResponse('')
#     return render(
#         req,
#         'dashboard/dashboard_table_body.html', {
#             'defaultservicetable': defaultservicetable,
#
#         })
#
#     # req.update({"defaultservicetable": defaultservicetable})
#     # # RequestConfig(req, paginate={'per_page': 3}).configure(defaultservicetable)
#     # return HttpResponse(req)
#     # return render(
#     #     req.update({"defaultservicetable": defaultservicetable})
#     # )


def ohsrvrecordspop(request):
    default_values = {}
    # loggeduser = request.session['_auth_user_id'];
    #
    # ''' Set account_company Session '''
    # account_company = UserPreference.objects.get(user=loggeduser, uprt_code='DFTCMP').uprf_value
    # if account_company == '':
    #     account_company = CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=loggeduser).cprs_id_id).comp_id
    # request.session['account_company'] = account_company
    # default_values['loggeduserscprs_id'] =CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=request.session['_auth_user_id']).cprs_id)
    print('default_values[loggeduser] --> ', User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id)
    default_values['loggeduser_cprs_id'] = User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id
    default_values['recordprivilege'] = request.GET.get('recordprivilege')
    default_values['ohrecordtype'] = request.GET.get('type')
    default_values['service'] = ComplianceService.objects.get(csrv_id=request.GET.get('service'))
    # print('Service note' , default_values['service'].csrv_note)

    # default_values['factor'] = None
    # default_values['factor_value'] = None
    print('Factor.objects.get 1')
    if Factor.objects.filter(ctyp_id=default_values['service'].srvj.ctyp).exclude(fact_code__exact='NONE').exists():
        print('Factor.objects.get 2')
        ohrecord_factor = Factor.objects.filter(ctyp_id=default_values['service'].srvj.ctyp).exclude(fact_code__exact='NONE').first()
        # factor = Factor.objects.filter(ctyp_id=default_values['service'].srvj.ctyp).exclude(fact_code__exact='NONE').first().fact_desc
        factor = ohrecord_factor.fact_desc
        default_values['factor'] = factor
        print('Factor.objects.get factor',ohrecord_factor)
        print('The value used to retrive values from Factor value are :',default_values['service'],'HOZE')
        factor_value= FactorValue.objects.filter(csrv_id=default_values['service'],fact=ohrecord_factor).first()
        default_values['factor_value'] = factor_value.fval_value
        print('Factor.objects.get factor_value', factor_value.fval_value)
        print('Factor.objects.get 3')

    default_values['cres_id'] = request.GET.get('cres_id', None)
    print('default_values[cres_id] :',default_values['cres_id'])
    default_values['cprs_id_responsible'] = request.GET.get('cprs_id_responsible', None)
    default_values['assignelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])

    default_values['service_schedule'] = None
    default_values['srvj_id'] = request.GET.get('srvj_id')
    default_values['ctyp_id'] = request.GET.get('ctyp_id')
    default_values['cssc_id'] = request.GET.get('cssc_id', None)
    if default_values['cssc_id'] is not None and default_values['cssc_id'] is not "":
        print('Tackling the default_values[service].csrv_id -->',default_values['cssc_id'], default_values['service'].csrv_id)
        scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],csrv_id=default_values['service'].csrv_id)
        default_values['vendorcontactlist'] = v_company_people.objects.filter(comp_id=scheduledservice.comp_id)

        if scheduledservice:
            default_values['service_schedule'] = scheduledservice

    default_values['loggeduser_account_company'] = request.session['account_company']
    default_values['loggeduser_account_subscription'] = request.session['account_subscription']
    default_values['serviceproviderlist'] = v_provider_jurisdiction.objects.filter(srvj_id=default_values['srvj_id'],ctyp_id=default_values['ctyp_id']).exclude(comp_id=request.session['account_company'])
    default_values['lastactioncomplianceexists'] = False
    default_values['lastactioncompliance'] = None
    if v_last_compliance_service_action.objects.filter(subs_id=default_values['loggeduser_account_subscription'],
                                                       srvj_id=default_values['srvj_id']).exists():
        default_values['lastactioncomplianceexists'] = True
        default_values['lastactioncompliance'] = v_last_compliance_service_action.objects.get(
            subs_id=default_values['loggeduser_account_subscription'],
            srvj_id=default_values['srvj_id'])
        print('default_values[lastactioncomplianceexists]', default_values['lastactioncomplianceexists'])
        print('default_values[lastactioncompliance]', default_values['lastactioncompliance'].comp_id_id)
        default_values['lastactionvendorcontactlist'] = v_company_people.objects.filter(
            comp_id=default_values['lastactioncompliance'].comp_id)


    default_values['csrv_due_date'] = request.GET.get('csrv_due_date')
    print('csrv_due_date',default_values['csrv_due_date'])

    default_values['scheduletype'] = request.GET.get('scdtyp')




    default_values['cssc_service_date'] = request.GET.get('cssc_service_date')

    default_values['csac_price_last'] = request.GET.get('csac_price_last')

    default_values['csac_service_date_last'] = request.GET.get('csac_service_date_last')
    default_values['off_from_avg'] = request.GET.get('off_from_avg')
    # default_values['cres_id'] = request.GET.get('cres_id', None)
    # default_values['cprs_id_responsible'] = request.GET.get('cprs_id_responsible',None)



    # default_values['serviceproviderlist'] = v_provider_jurisdiction.objects.filter(srvj_id=default_values['srvj_id'],ctyp_id=default_values['ctyp_id']).exclude(comp_id=request.session['account_company'])
    default_values['responsiblelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])

    print('default_values[scheduletype] -, default_values[cssc_id]', default_values['scheduletype'], default_values['cssc_id'] )
    if default_values['scheduletype']== 'mod' and default_values['cssc_id'] is not None:
        scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],
                                                                 csrv_id=request.GET.get('service'))
        if scheduledservice:
            default_values['service_schedule'] = scheduledservice

    print("\n Scheduled Records default_values :",default_values)

    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    return render(request, 'compliance/ohcsrvservices.html', default_values)

def popupschedule(request):
    default_values = {}
    # loggeduser = request.session['_auth_user_id'];
    #
    # ''' Set account_company Session '''
    # account_company = UserPreference.objects.get(user=loggeduser, uprt_code='DFTCMP').uprf_value
    # if account_company == '':
    #     account_company = CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=loggeduser).cprs_id_id).comp_id
    # request.session['account_company'] = account_company
    # default_values['loggeduserscprs_id'] =CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=request.session['_auth_user_id']).cprs_id)
    print('default_values[loggeduser] --> ', User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id)
    default_values['loggeduser_cprs_id'] = User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id
    print(' request.session[account_company', request.session['account_company'])
    print(' request.session[account_subscription', request.session['account_subscription'])
    default_values['loggeduser_account_company'] = request.session['account_company']
    default_values['loggeduser_account_subscription'] = request.session['account_subscription']

    default_values['rectype'] = request.GET.get('type')
    default_values['service'] = ComplianceService.objects.get(csrv_id=request.GET.get('service'))
    default_values['scheduletype'] = request.GET.get('scdtyp')
    print('default_values[srvj_id]', request.GET.get('srvj_id',None))
    default_values['srvj_id'] = request.GET.get('srvj_id')
    default_values['ctyp_id'] = request.GET.get('ctyp_id')

    default_values['cssc_id'] = request.GET.get('cssc_id',None)
    default_values['cssc_service_date'] = request.GET.get('cssc_service_date')
    default_values['csrv_due_date'] = request.GET.get('csrv_due_date')
    default_values['csac_price_last'] = request.GET.get('csac_price_last')
    default_values['csac_service_date_last'] = request.GET.get('csac_service_date_last')
    default_values['off_from_avg'] = request.GET.get('off_from_avg')
    default_values['cres_id'] = request.GET.get('cres_id', None)
    default_values['cprs_id_responsible'] = request.GET.get('cprs_id_responsible',None)

    print('default_values[cres_id]',default_values['cres_id'])

    default_values['serviceproviderlist'] = v_provider_jurisdiction.objects.filter(srvj_id=default_values['srvj_id'],ctyp_id=default_values['ctyp_id']).exclude(comp_id=request.session['account_company'])
    default_values['responsiblelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])

    print('default_values[scheduletype] -, default_values[cssc_id]', default_values['scheduletype'], default_values['cssc_id'] )
    if default_values['scheduletype']== 'mod' and default_values['cssc_id'] is not None:
        scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],
                                                                 csrv_id=request.GET.get('service'))
        default_values['vendorcontactlist'] = v_company_people.objects.filter(comp_id=scheduledservice.comp_id)

        if scheduledservice:
            default_values['service_schedule'] = scheduledservice

    default_values['lastactioncomplianceexists'] = False
    default_values['lastactioncompliance']= None
    if v_last_compliance_service_action.objects.filter(subs_id=default_values['loggeduser_account_subscription'],
                                                       srvj_id=default_values['srvj_id']).exists():
        default_values['lastactioncomplianceexists'] = True
        default_values['lastactioncompliance'] = v_last_compliance_service_action.objects.get(subs_id=default_values['loggeduser_account_subscription'],
                                                       srvj_id =default_values['srvj_id'])
        print('default_values[lastactioncomplianceexists]',default_values['lastactioncomplianceexists'])
        print('default_values[lastactioncompliance]', default_values['lastactioncompliance'].comp_id_id)
        default_values['lastactionvendorcontactlist'] = v_company_people.objects.filter(comp_id=default_values['lastactioncompliance'].comp_id)



    print("\n Scheduled Records default_values :",default_values)

    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    return render(request, 'dashboard/scheduleservice.html', default_values)

def popupserviceaction(request):
    default_values = {}
    # loggeduser = request.session['_auth_user_id'];
    #
    # ''' Set account_company Session '''
    # account_company = UserPreference.objects.get(user=loggeduser, uprt_code='DFTCMP').uprf_value
    # if account_company == '':
    #     account_company = CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=loggeduser).cprs_id_id).comp_id
    # request.session['account_company'] = account_company
    # default_values['loggeduserscprs_id'] =CompanyPersonRole.objects.get(cprs_id=User.objects.get(user_id=request.session['_auth_user_id']).cprs_id)
    print('default_values[loggeduser] --> ', User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id)
    default_values['loggeduser_cprs_id'] = User.objects.get(pk= request.session['_auth_user_id']).cprs_id_id
    default_values['loggeduser_account_company'] = request.session['account_company']
    default_values['loggeduser_account_subscription'] = request.session['account_subscription']

    default_values['rectype'] = request.GET.get('type')
    default_values['service'] = ComplianceService.objects.get(csrv_id=request.GET.get('service'))
    default_values['actiontype'] = request.GET.get('actiontype')
    default_values['srvj_id'] = request.GET.get('srvj_id')
    default_values['ctyp_id'] = request.GET.get('ctyp_id')
    default_values['basi_code'] = request.GET.get('basi_code', None)
    if default_values['basi_code'] is not None:
        default_values['basis_description'] = Basis.objects.get(basi_code=default_values['basi_code'])

    default_values['cssc_id'] = request.GET.get('cssc_id',None)
    default_values['cssc_service_date'] = request.GET.get('cssc_service_date')

    default_values['csrv_due_date'] = request.GET.get('csrv_due_date')
    default_values['csac_price_last'] = request.GET.get('csac_price_last')
    default_values['csac_service_date_last'] = request.GET.get('csac_service_date_last')
    default_values['off_from_avg'] = request.GET.get('off_from_avg')
    default_values['cres_id'] = request.GET.get('cres_id', None)
    default_values['cprs_id_responsible'] = request.GET.get('cprs_id_responsible',None)

    default_values['service_schedule'] = None
    default_values['serviceproviderlist'] = None
    default_values['service_schedule'] = None

    default_values['serviceproviderlist'] = v_provider_jurisdiction.objects.filter(srvj_id=default_values['srvj_id'],ctyp_id=default_values['ctyp_id']).exclude(comp_id=request.session['account_company'])
    default_values['responsiblelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])

    default_values['lastactioncomplianceexists'] = False
    default_values['lastactioncompliance'] = None

    print('default_values[cssc_id]------->> ',default_values['cssc_id'] )
    if default_values['cssc_id']:
        scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],
                                                                 csrv_id=request.GET.get('service'))
        default_values['vendorcontactlist'] = v_company_people.objects.filter(comp_id=scheduledservice.comp_id)

        if scheduledservice:
            default_values['service_schedule'] = scheduledservice

    else:
        if v_last_compliance_service_action.objects.filter(subs_id=default_values['loggeduser_account_subscription'],
                                                           srvj_id=default_values['srvj_id']).exists():
            print('v_last_compliance_service_action--->Exists')
            default_values['lastactioncomplianceexists'] = True
            default_values['lastactioncompliance'] = v_last_compliance_service_action.objects.get(subs_id=default_values['loggeduser_account_subscription'],
                                                           srvj_id =default_values['srvj_id'])
            print('default_values[lastactioncomplianceexists]',default_values['lastactioncomplianceexists'])
            print('default_values[lastactioncompliance]', default_values['lastactioncompliance'].comp_id_id)
            default_values['lastactionvendorcontactlist'] = v_company_people.objects.filter(comp_id=default_values['lastactioncompliance'].comp_id)


    print("\n Scheduled Records default_values :",default_values)

    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    return render(request, 'dashboard/actionservice.html', default_values)

def popupschedulenewvendor(request):
    default_values = {}
    default_values['rectype'] = 'New Vendor'
    default_values['service'] = 'Vendor'
    default_values['scheduletype'] = 'new'
    default_values['csrv_due_date'] = '01/20/17'
    default_values['csac_price_last'] = '200'
    default_values['csac_service_date_last'] = '01/20/17'
    default_values['off_from_avg'] = '0.2'
    # print('request.GET.get(scdtyp)',request.GET.get('scdtyp'))
    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    print('Calling dashboard/schedulenewvendor.html')
    return render(request, 'dashboard/schedulenewvendor.html', default_values)

def popupschedulenewvendorcontact(request):
    default_values = {}
    default_values['rectype'] = 'New Vendor Contact'
    default_values['service'] = 'Vendor'
    default_values['scheduletype'] = 'new'
    default_values['csrv_due_date'] = '01/20/17'
    default_values['csac_price_last'] = '200'
    default_values['csac_service_date_last'] = '01/20/17'
    default_values['off_from_avg'] = '0.2'
    # print('request.GET.get(scdtyp)',request.GET.get('scdtyp'))
    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    print('Calling dashboard/schedulenewvendorcontact.html')
    return render(request, 'dashboard/schedulenewvendorcontact.html', default_values)


def popupcoordinate(request):
    default_values = {}
    default_values['loggeduser_cprs_id'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    default_values['rectype'] = request.GET.get('type',None)
    default_values['service'] = ComplianceService.objects.get(csrv_id=request.GET.get('service',None))
    default_values['assigntype'] = request.GET.get('assigntype',None)
    default_values['cres_id'] = request.GET.get('cres_id', None)
    default_values['cprs_id_assigner'] = request.GET.get('cprs_id_assigner', None)
    default_values['cprs_id_responsible'] = request.GET.get('cprs_id_responsible', None)


    default_values['cssc_id'] = request.GET.get('cssc_id',None)
    default_values['cssc_service_date'] = request.GET.get('cssc_service_date',None)
    default_values['csrv_due_date'] = request.GET.get('csrv_due_date',None)
    default_values['csac_service_date_last'] = request.GET.get('csac_service_date_last', None)
    default_values['service_schedule'] = None
    default_values['assignelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])
    #     # CompanyPersonRole.objects.values_list('prsn_id__first_name', flat=True).get(comp_id=request.session['account_company'])
    #     # CompanyPersonRole.objects.filter(comp_id=request.session['account_company']).values_list('cprs_id','prsn_id')
    # print('default_values[assignelist]',default_values['assignelist'],request.session['account_company'])
    #
    # print('default_values[scheduletype] -, default_values[cssc_id]', default_values['assigntype'], default_values['cssc_id'] )
    # # if default_values['assigntyptype']== 'mod' and default_values['cssc_id'] is not None:
    # #     scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],
    # #                                                              csrv_id=request.GET.get('service'))

    print('default_values[service]', default_values['service'].csrv_id)
    print('default_values[cres_id]', default_values['cres_id'])

    default_values['responsiblerec']= ''
    if default_values['cres_id'] is not None:

        responsiblerec = ComplianceResponsibility.objects.get(cres_id=default_values['cres_id'],
                                                                 csrv_id=default_values['service'].csrv_id, cres_is_active='Y')

        if responsiblerec:
            default_values['responsiblerec'] = responsiblerec

    if default_values['cssc_id'] is not None:
        scheduledservice = ComplianceServiceSchedule.objects.get(cssc_id=default_values['cssc_id'],
                                                                 csrv_id=request.GET.get('service'))
        if scheduledservice:
            default_values['service_schedule'] = scheduledservice

    print("\n Scheduled Records default_values :",default_values)

    # return HttpResponse(render_to_string('dashboard/scheduleservice.html', {'service': service}))default_values
    # return render(request, 'dashboard/scheduleservice.html', {'service': service , 'scheduletype':scheduletype})
    return render(request, 'dashboard/servicecoordinator.html', default_values)


class ScheduleItemUpdateView(UpdateView):
    # model = Item
    form_class = ScheduleForm
    template_name = 'dashboard/scheduleservice.html'

    def dispatch(self, *args, **kwargs):
        # self.item_id = kwargs['pk']
        service = ComplianceService.objects.get(csrv_id=self.request.GET.get('service'))
        return super(ScheduleItemUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        # item = Item.objects.get(id=self.item_id)
        return HttpResponse(render_to_string('dashboard/scheduleservice_success.html', {'item': '1'}))
