from datetime import date, datetime

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

from onhand.compliance.models import ComplianceService, ServiceJurisdiction, V_Service_jurisdiction, \
    ComplianceServiceType, Factor, ComplianceServiceSchedule, ScheduleStatus, ComplianceResponsibility, FactorValue
from onhand.insurance.models import InsuranceTypeJurisdiction
from onhand.management.models import City, Zipcode, County, State, NaicsLevel2, NaicsLevel3, NaicsLevel4, NaicsLevel5, \
    v_dashboard_service, v_company_people
# from onhand.subscription.app_settings import app_settings
from onhand.submission.models import SubmissionTypeJurisdiction
from onhand.subscription.adapter import get_adapter
from onhand.subscription.models import Company, CompanyPersonRole
from onhand.subscription.tables import ServicesTable, NameTable, data
from onhand.users.forms import LoginForm
from onhand.users.models import UserPreference, User
from onhand.users.utils import complete_signup, passthrough_next_redirect_url, get_login_redirect_url
from onhand.subscription.utils import (get_next_redirect_url, get_current_site, get_form_class, get_request_param,
                    complete_signup_prelim_registration, complete_signup_prelim_user)
from .forms import ComplianceForm
from . import app_settings
from .exceptions import ImmediateHttpResponse
# from .adapter import get_adapter
from onhand.products.models import Product,ProductDiscount,ProductType,ProductBasis,Discount
from onhand.management.models import Basis


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password1', 'password2'))


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


class RedirectAuthenticatedUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        print('Compliance view, Im Here!')
        self.request = request
        if request.user.is_authenticated() and \
                app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
            print('RedirectAuthenticatedUserMixin', )
            response = super(RedirectAuthenticatedUserMixin,
                             self).dispatch(request,
                                            *args,
                                            **kwargs)
            print('RedirectAuthenticatedUserMixin kwargs.items():', kwargs)
            for key, value in kwargs.items():
                print("%s = %s") % (key, value)
        # return response

            # redirect_to = self.get_authenticated_redirect_url()
            # print('RedirectAuthenticatedUserMixin - redirect_to', redirect_to)
            # # response = HttpResponseRedirect(redirect_to)
            # response = super(RedirectAuthenticatedUserMixin,
            #                  self).dispatch(request,
            #                                 *args,
            #                                 **kwargs)
            # print('RedirectAuthenticatedUserMixin - response', response)
            # print('_ajax_response(request, response)', _ajax_response(request, response))
            # return _ajax_response(request, response)
        else:
            print('RedirectAuthenticatedUserMixin', )
            redirect_to = reverse('login')
            print('RedirectAuthenticatedUserMixin - redirect_to', redirect_to)
            response = HttpResponseRedirect(redirect_to)
        return response


        # (end WORKAROUND)
        # if request.user.is_authenticated() and \
        #         app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
        #
        #     redirect_to = self.get_authenticated_redirect_url()
        #     print('Compliance RedirectAuthenticatedUserMixin dispatch - redirect_to', redirect_to)
        #     response = HttpResponseRedirect(redirect_to)
        #     return _ajax_response(request, response)
        # else:
        #     print('RedirectAuthenticatedUserMixin', )
        #     response = super(RedirectAuthenticatedUserMixin,
        #                         self).dispatch(request,
        #                                         *args,
        #                                       **kwargs)
        #     print('RedirectAuthenticatedUserMixin kwargs.items():',kwargs)
        #     for key, value in kwargs.items():
        #         print("%s = %s") % (key, value)
        # return response

    def get_authenticated_redirect_url(self):
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
            print('self.form_valid(form) : ')
        else:
            response = self.form_invalid(form)
            print('self.form_invalid(form) : ', self.form_invalid(form),self)
        # print(response)
        return _ajax_response(self.request, response, form=form)


class ComplianceRegistrationView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                FormView):
    form_class = ComplianceForm
    # template_name = "Regsitration/register." + app_settings.TEMPLATE_EXTENSION
    template_name = "compliance/register.html"
    context_object_name = 'onhand_plan'
    success_url = "home"
    redirect_field_name = "next"

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        print(request.session['_auth_user_id'])
        print('Printing Default Company for user')
        print('account_subscription, account_company, account_county', request.session['account_subscription'] , request.session['account_company'], request.session['account_county'])
        print(UserPreference.objects.get(user=request.session['_auth_user_id'], uprt_code='DFTCMP').uprf_value)
        # subscription_id_user = Subscription.objects.get()
        return super(ComplianceRegistrationView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ComplianceRegistrationView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_class(self):
        # return get_form_class(app_settings.FORMS, 'register', self.form_class)
        return  ComplianceForm

    def form_valid(self, form):
        success_url = self.get_success_url()
        print("ComplianceRegistrationView form_valid ")
        try:
            return form.save(self.request, redirect_url=success_url)
        except ImmediateHttpResponse as e:
            return e.response

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (get_next_redirect_url(
            self.request,
            self.redirect_field_name) or self.success_url)
        return ret

    def get_context_data(self, **kwargs):
        ret = super(ComplianceRegistrationView, self).get_context_data(**kwargs)


        # register_url = passthrough_next_redirect_url(self.request,
        # register_url = passthrough_next_redirect_url(self.request,
        #                                            reverse("account_signup"),
        #                                            self.redirect_field_name)
        # redirect_field_value = get_request_param(self.request,
        #                                          self.redirect_field_name)
        # site = get_current_site(self.request)
        #
        # ret.update({"register_url": register_url,
        #             "site": site,
        #             "redirect_field_name": self.redirect_field_name,
        #             "redirect_field_value": redirect_field_value})
        return ret

registercompliance = ComplianceRegistrationView.as_view()


@csrf_protect
def get_complianceservice_details(request):
    form_compliance = request.GET.get('complianceserviceselected', None)
    response_data = {}
    response_data['result'] = 'success'
    response_data['frequency'] = ''
    response_data['compliance_desc'] = '-'
    response_data['jurisdiction'] = '-'
    response_data['agency'] = '-'
    response_data['factor'] = '-'
    response_data['lastservicedate'] = ''

    response_data['loggeduser_cprs_id'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    response_data['cprs_id_responsible'] = request.GET.get('cprs_id_responsible', None)
    # response_data['responsiblelist'] = CompanyPersonRole.objects.filter(comp_id=request.session['account_company'])
    responsiblelist = tuple(
        v_company_people.objects.values_list('cprs_id', 'prsn_name').filter(comp_id=request.session['account_company']))
    print('responsiblelist',responsiblelist)
    response_data['responsiblelist'] = responsiblelist

    #response_data['lastservicedate'] = datetime.now().strftime("%m/%d/%y")
    try:
        frequency = ComplianceServiceType.objects.get(ctyp_id=form_compliance).basi_code_id
        print('frequency',frequency)
        response_data['frequency'] = frequency
        service_desc = ComplianceServiceType.objects.get(ctyp_id=form_compliance).ctyp_desc

        compliance_desc=  ServiceJurisdiction.objects.get(ctyp_id=form_compliance,cont_id=request.session['account_county']).srvj_help_text
        # compliance_desc = ComplianceServiceType.objects.get(ctyp_id=form_compliance).ctyp_desc
        print('compliance_desc', compliance_desc)
        response_data['compliance_desc'] = compliance_desc

        jurisdiction = V_Service_jurisdiction.objects.values_list('govl_code__govl_desc', flat=True).get(ctyp_id=form_compliance)
        print('jurisdiction', jurisdiction)
        response_data['jurisdiction'] = jurisdiction

        agency = V_Service_jurisdiction.objects.values_list('agen_code__agen_name', flat=True).get(ctyp_id=form_compliance)
        print('agency', agency)
        response_data['agency'] = agency

        print('Factor.objects.get 1')
        if Factor.objects.filter(ctyp_id=form_compliance).exclude(fact_code__exact='NONE').exists():
            print('Factor.objects.get 2')
            factor = Factor.objects.filter(ctyp_id=form_compliance).exclude(fact_code__exact='NONE').first().fact_desc
            response_data['factor'] =factor

            print('Factor.objects.get 3')
        # lastservicedate = datetime.now()
        lastservicedate = None
        if (v_dashboard_service.objects.filter(subscriber=316,csac_service_date_last__isnull=False,ctyp_desc=service_desc).count() != 0):
            print('v_dashboard_service last service date')
            lastservicedate = v_dashboard_service.objects.values_list('csac_service_date_last', flat=True).filter(subscriber=316,csac_service_date_last__isnull=False,ctyp_desc=service_desc).first()
        if lastservicedate is not None:
            print('lastservicedate', lastservicedate.strftime("%m/%d/%y"))
            response_data['lastservicedate'] = lastservicedate.strftime("%m/%d/%y")

    except Exception as e:
        print('Exception encountered ', e)
        print('exception :Compliance not found.')
        response_data['result'] = 'error'
        response_data['error_message'] = 'Compliance not found.'

    return JsonResponse(response_data)

@csrf_protect
def add_new_vendor_compliance(request):
    print('AJAX -add_new_vendor_compliance')

    form_vendorname = request.GET.get('vendorname', None)
    form_firstname = request.GET.get('firstname', None)
    form_lastname = request.GET.get('lastname', None)
    form_phone = request.GET.get('phone', None)
    form_email = request.GET.get('email', None)
    response_data = {}
    response_data['result'] = 'success'
    response_data['vendor'] = ''
    response_data['vendorcontact'] = ''
    response_data['vendorcontactrole']=''

    try:
        adapter = get_adapter(request)
        if(form_vendorname):
            if Company.objects.filter(name__exact=form_vendorname).count() == 0:
                company = adapter.new_company(request)

                print('Created Company Object',company)
                adapter.save_vendor(company, form_vendorname, form_phone, form_email)
                print('Created New Vendor Company',company.comp_id)
                response_data['vendor'] = company.comp_id

                print('form_firstname',form_firstname)
                if form_firstname:
                    person = adapter.new_person(request)
                    print('Created Person Object', person)
                    adapter.save_vendor_contact(person, form_firstname, form_lastname,  form_phone, form_email)
                    print('Created New Vendor Contact', person.prsn_id)
                    response_data['vendorcontact'] = person.prsn_id

                    company_person_role = adapter.new_company_person_role(request)
                    print('Created Person role Object', company_person_role)
                    # # adapter.save_company_vendorperson_role()
                    # # company_person_role = adapter.new_company_person_role(request)
                    adapter.save_company_vendorperson_role(company_person_role, company.comp_id, person.prsn_id)
                    response_data['vendorcontactrole'] = company_person_role.cprs_id
                    print('company_person_role :', company_person_role.cprs_id)

    except:
        print('exception :Error creating new vendor.')
        response_data['result'] = 'error'
        response_data['error_message'] = 'Error occured while creating new vendor.'

    return JsonResponse(response_data)


@csrf_protect
def add_new_vendor_contact_compliance(request):


    form_vendorid = request.GET.get('vendorid', None)
    form_firstname = request.GET.get('firstname', None)
    form_lastname = request.GET.get('lastname', None)
    form_phone = request.GET.get('phone', None)
    form_email = request.GET.get('email', None)
    response_data = {}
    response_data['result'] = 'success'
    response_data['vendorcontact'] = ''
    response_data['vendorcontactrole']=''

    try:
        adapter = get_adapter(request)
        if form_vendorid:
            if Company.objects.filter(comp_id__exact=form_vendorid).count() != 0:
                company = Company.objects.get(comp_id=form_vendorid)
                print('AJAX -add_new_vendor_contact_compliance')
                if form_firstname:
                    person = adapter.new_person(request)
                    print('Created Person Object', person)
                    adapter.save_vendor_contact(person, form_firstname, form_lastname,  form_phone, form_email)
                    print('Created New Vendor Contact', person.prsn_id)
                    response_data['vendorcontact'] = person.prsn_id

                    company_person_role = adapter.new_company_person_role(request)
                    print('Created Person role Object', company_person_role)

                    adapter.save_company_vendorperson_role(company_person_role, company.comp_id, person.prsn_id)
                    response_data['vendorcontactrole'] = company_person_role.cprs_id
                    print('company_person_role :', company_person_role.cprs_id)

    except:
        print('exception :Error creating new vendor Contact.')
        response_data['result'] = 'error'
        response_data['error_message'] = 'Error occured while creating new vendor.'

    return JsonResponse(response_data)

@csrf_protect
def add_new_vendor_compliance_valid(request):
    print('AJAX -Check new vendor name is Valid')
    form_vendorname = request.GET.get('vendorname', None)
    response_data = {}
    response_data['result'] = 'success'
    response_data['error_message'] = ''
    try:
        if(form_vendorname):
            if Company.objects.filter(name__exact=form_vendorname).count() != 0:
                response_data['result'] = 'error'
                response_data['error_message'] = 'Already registered'
    except:
        print('exception :Error Checking vendor.')
        response_data['result'] = 'error'
        response_data['error_message'] = 'Unable to validate Vendor name'

    return JsonResponse(response_data)

@csrf_protect
def add_new_schedule_compliance(request):
    from onhand.compliance.adapter import get_adapter
    scheduled_data = {}
    scheduled_data['form_action'] = request.GET.get('action', None)
    scheduled_data['form_modified_cssc_id'] = request.GET.get('modified_cssc_id', None)
    scheduled_data['form_scheduletype'] = request.GET.get('scheduletype', None)
    scheduled_data['form_recordtype'] = request.GET.get('recordtype', None)
    scheduled_data['form_recordtype_id'] = request.GET.get('recordtype_id', None)
    scheduled_data['form_vendorid'] = request.GET.get('vendor', None)
    scheduled_data['form_vendorcontactroleid'] = request.GET.get('vendorcontactrole', None)
    scheduled_data['form_phone'] = request.GET.get('phone', None)
    scheduled_data['form_email'] = request.GET.get('email', None)
    scheduled_data['form_schedule'] = request.GET.get('schedule', None)
    scheduled_data['form_notes'] = request.GET.get('notes', None)
    scheduled_data['form_cres_id'] = request.GET.get('cres_id', None)
    scheduled_data['form_responsible'] = request.GET.get('responsible', None)
        # User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    scheduled_data['form_assigner'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    scheduled_data['form_schedule_status']='PEND'

    response_data = {}
    response_data['result'] = 'success'
    response_data['vendor'] = ''
    response_data['vendorcontact'] = ''

    print('AJAX - Scheduled Action callled')
    print('scheduled_data[form_action]',scheduled_data['form_action'])

    # Create New Schedule
    if scheduled_data['form_action'] == 'create':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if scheduled_data['form_vendorid'] :
                if scheduled_data['form_recordtype'] == 'Service':
                    print('form_vendorid',scheduled_data['form_vendorid'])
                    print('scheduled_data[form_recordtype_id]',scheduled_data['form_recordtype_id'])
                    print('scheduled_data[form_assigner]', scheduled_data['form_assigner'])
                    print('scheduled_data[form_vendorid]', scheduled_data['form_vendorid'])
                    print('scheduled_data[form_responsible]', scheduled_data['form_responsible'])
                    print('scheduled_data[form_vendorcontactroleid]', scheduled_data['form_vendorcontactroleid'])
                    print('scheduled_data[form_cres_id]', scheduled_data['form_cres_id'])

                    print(ComplianceServiceSchedule.objects.filter(csrv_id=scheduled_data['form_recordtype_id'],cprs_id_assigner=scheduled_data['form_assigner'],
                                                                comp_id=scheduled_data['form_vendorid'],cprs_id_responsible=scheduled_data['form_responsible'],
                                                                cprs_id_provider=scheduled_data['form_vendorcontactroleid'],schs_code='PEND').count())
                    if ComplianceServiceSchedule.objects.filter(csrv_id=scheduled_data['form_recordtype_id'],cprs_id_assigner=scheduled_data['form_assigner'],
                                                                comp_id=scheduled_data['form_vendorid'],cprs_id_responsible=scheduled_data['form_responsible'],
                                                                cprs_id_provider=scheduled_data['form_vendorcontactroleid'],schs_code='PEND').count() == 0:
                        print('scheduled_data[form_responsible]1', scheduled_data['form_responsible'])
                        compserviceschedule = adapter.new_ComplianceServiceSchedule(request)
                        print('Created complianceserviceSchedule Object',compserviceschedule.cssc_id)
                        adapter.save_complianceserviceschedule(compserviceschedule, scheduled_data)
                        print('Created New Schedule',compserviceschedule.cssc_id)

                    if scheduled_data['form_cres_id'] is None or scheduled_data['form_cres_id']== 0 or scheduled_data['form_cres_id']=='':
                        print('scheduled_data[form_cres_id]', scheduled_data['form_cres_id'])
                        compserviceresponsible = adapter.new_ComplianceResponsibility(request)
                        print('Created compserviceresponsible Object', compserviceresponsible.cres_id)
                        adapter.save_complianceresponsibility(compserviceresponsible, scheduled_data)
                        print('Created New Schedule', compserviceresponsible.cres_id)

        except Exception as e:
            print('Exception encountered while committing complianceserviceschedule', e)
            print('exception :Error creating new Schedule.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating Schedule'

    if scheduled_data['form_action'] == 'update':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if scheduled_data['form_vendorid'] and scheduled_data['form_modified_cssc_id'] :
                if scheduled_data['form_recordtype'] == 'Service':
                    print('form_vendorid',scheduled_data['form_vendorid'])
                    print(ComplianceServiceSchedule.objects.filter(csrv_id=scheduled_data['form_recordtype_id'],cprs_id_assigner=scheduled_data['form_assigner'],
                                                                comp_id=scheduled_data['form_vendorid'],cprs_id_responsible=scheduled_data['form_responsible'],
                                                                cprs_id_provider=scheduled_data['form_vendorcontactroleid'],schs_code='PEND').count())
                    if ComplianceServiceSchedule.objects.filter(csrv_id=scheduled_data['form_recordtype_id'],cprs_id_assigner=scheduled_data['form_assigner'],
                                                                comp_id=scheduled_data['form_vendorid'],cprs_id_responsible=scheduled_data['form_responsible'],
                                                                cprs_id_provider=scheduled_data['form_vendorcontactroleid'],schs_code='PEND').count() == 0:
                        print('scheduled_data[form_responsible]1', scheduled_data['form_responsible'])
                        compserviceschedule =   ComplianceServiceSchedule.objects.get(cssc_id=scheduled_data['form_modified_cssc_id'])
                        print('Retrived modified complianceserviceSchedule Object',compserviceschedule.cssc_id)
                        adapter.save_complianceserviceschedule(compserviceschedule, scheduled_data)
                        print('Created New Schedule',compserviceschedule.cssc_id)

                    if not scheduled_data['form_cres_id']:
                        print('scheduled_data[form_cres_id]', scheduled_data['form_cres_id'])
                        compserviceresponsible = adapter.new_ComplianceResponsibility(request)
                        print('Created compserviceresponsible Object', compserviceresponsible.cres_id)
                        adapter.save_complianceresponsibility(compserviceresponsible, scheduled_data)
                        print('Created New Schedule', compserviceresponsible.cres_id)

        except Exception as e:
            print('Exception encountered while committing complianceserviceschedule', e)
            print('exception :Error creating new Schedule.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating Schedule'

    # Udpate Existing Schedule
    # if scheduled_data['form_action'] == 'update':

    # Delete Existing Schedule
    print('Action %s is been called.',scheduled_data['form_action'])
    if scheduled_data['form_action'] == 'delete':
        try:
            if scheduled_data['form_vendorid']:
                if scheduled_data['form_recordtype'] == 'Service':
                    print('scheduled_data[form_modified_cssc_id]: %s, scheduled_data[form_recordtype_id]: %s',scheduled_data['form_modified_cssc_id'],scheduled_data['form_recordtype_id'])
                    if ComplianceServiceSchedule.objects.filter(cssc_id=scheduled_data['form_modified_cssc_id'],
                                                                             csrv_id=scheduled_data['form_recordtype_id']).exists():
                        print('Trying Delete CSSSC_ID')
                        deleteschedule = ComplianceServiceSchedule.objects.get(cssc_id=scheduled_data['form_modified_cssc_id'],
                                                                 csrv_id=scheduled_data['form_recordtype_id'])
                        print('deleteschedule',deleteschedule.schs_code)
                        deleteschedule.schs_code = ScheduleStatus.objects.get(pk='CANC')
                        deleteschedule.save(update_fields=['schs_code'])
        except Exception as e:
            print('exception :Error deleting Schedule.',e)
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while deleting Schedule'

    return JsonResponse(response_data)


@csrf_protect
def add_new_compliance_action(request):
    from onhand.compliance.adapter import get_adapter
    complianceaction_data = {}

    complianceaction_data['form_action'] = request.GET.get('action', None)
    complianceaction_data['form_complianceservice_id'] = request.GET.get('complianceservice_id', None)
    complianceaction_data['form_basi_code'] = request.GET.get('basi_code', None)
    complianceaction_data['form_modified_cssc_id'] = request.GET.get('modified_cssc_id', None)
    complianceaction_data['form_actiontype'] = request.GET.get('actiontype', None)
    complianceaction_data['form_recordtype'] = request.GET.get('recordtype', None)
    complianceaction_data['form_recordtype_id'] = request.GET.get('recordtype_id', None)
    complianceaction_data['form_vendorid'] = request.GET.get('vendor', None)
    complianceaction_data['form_vendorcontactroleid'] = request.GET.get('vendorcontactrole', None)
    complianceaction_data['form_phone'] = request.GET.get('phone', None)
    complianceaction_data['form_email'] = request.GET.get('email', None)
    complianceaction_data['form_schedule'] = request.GET.get('schedule', None)
    complianceaction_data['form_notes'] = request.GET.get('notes', None)
    complianceaction_data['actiondate'] = request.GET.get('actiondate', None)
    complianceaction_data['nextservicedate'] = request.GET.get('nextservicedate', None)
    complianceaction_data['form_price'] = request.GET.get('price', None)
    complianceaction_data['form_responsible'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    complianceaction_data['form_assigner'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id

    response_data = {}
    response_data['result'] = 'success'
    response_data['error_message'] = ''

    # Create New Schedule
    if complianceaction_data['form_action'] == 'create':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if complianceaction_data['form_complianceservice_id'] is not None:
                if complianceaction_data['form_recordtype'] == 'Service':
                    if ComplianceServiceSchedule.objects.filter(csrv_id=complianceaction_data['form_complianceservice_id']).exists():
                        oldcompliance = ComplianceService.objects.get(csrv_id=complianceaction_data['form_complianceservice_id'])
                        complianceaction_data['oldcompliance'] =oldcompliance

                        print('Creating complianceserviceaction for ->', oldcompliance.csrv_id)
                        complianceserviceaction = adapter.new_complianceserviceaction(request)
                        complianceserviceaction = adapter.save_complianceserviceaction_ajax(complianceserviceaction,
                                                                                            complianceaction_data,
                                                                                            oldcompliance)

                        print('Creating serviceproviderperson for complianceserviceaction ->', complianceserviceaction.csac_id)
                        if complianceaction_data['form_vendorcontactroleid']:
                            serviceproviderperson = adapter.new_providerserviceperson(request)
                            serviceproviderperson = adapter.save_providerserviceperson_ajax(serviceproviderperson, complianceserviceaction,
                                                                                            complianceaction_data[
                                                                                                'form_vendorcontactroleid'])

                        print('Creating New complianceservice After creation of  complianceserviceaction -> ', complianceserviceaction.csrv_id)
                        complianceservice = adapter.new_complianceservice(request)
                        complianceservice = adapter.save_complianceservice_ajax(complianceservice, complianceaction_data)


                        if FactorValue.objects.filter(csrv_id=complianceaction_data['form_complianceservice_id']).exists()\
                            and complianceservice is not None:
                            print('Creating FactorValue for complianceservice ->', complianceservice.csrv_id)
                            oldfactorvalue = FactorValue.objects.get(csrv_id=complianceaction_data['form_complianceservice_id'])
                            print('oldfactorvalue',oldfactorvalue.fact,oldfactorvalue.csrv_id,oldfactorvalue.fval_value)
                            compliancefactor = adapter.new_complianceservicefactor(request)
                            compliancefactor = adapter.save_complianceservicefactor_ajax(compliancefactor,
                                                                                         complianceservice, oldfactorvalue)

                        if complianceaction_data['form_recordtype_id']:
                            if ComplianceResponsibility.objects.filter(csrv_id=complianceaction_data['form_complianceservice_id'],
                                                                       cres_is_active='Y').exists():
                                oldomplianceresponsibility = ComplianceResponsibility.objects.get(csrv_id=complianceaction_data['form_complianceservice_id'],
                                                                       cres_is_active='Y')
                                complianceaction_data['form_responsible'] = oldomplianceresponsibility.cprs_id_responsible.cprs_id
                                oldomplianceresponsibility.cres_is_active = 'N'
                                oldomplianceresponsibility.save(update_fields=['cres_is_active'])

                            compserviceresponsible = adapter.new_ComplianceResponsibility(request)
                            adapter.save_complianceresponsibility(compserviceresponsible, complianceaction_data)
                            print('Created New Responsible', compserviceresponsible.cres_id)


                    print('complianceaction_data[form_modified_cssc_id] ',complianceaction_data['form_modified_cssc_id'] )
                    if complianceaction_data['form_modified_cssc_id'] is None or complianceaction_data['form_modified_cssc_id']== 0 or complianceaction_data['form_modified_cssc_id']=='':
                        print('Trying Delete CSSSC_ID1')
                        if ComplianceServiceSchedule.objects.filter(cssc_id=complianceaction_data['form_modified_cssc_id'].cssc_id,
                                                                    csrv_id=complianceaction_data['complianceservice_id'].csrv_id).exists():
                            print('Trying Delete CSSSC_ID')
                            deleteschedule = ComplianceServiceSchedule.objects.get(
                                cssc_id=complianceaction_data['form_modified_cssc_id'].cssc_id,
                                csrv_id=complianceaction_data['complianceservice_id'].csrv_id)
                            print('deleteschedule', deleteschedule.schs_code)
                            deleteschedule.schs_code = ScheduleStatus.objects.get(pk='COMP')
                            deleteschedule.save(update_fields=['schs_code'])

        except Exception as e:
            print('Exception encountered while committing complianceserviceschedule', e)
            print('exception :Error creating new compliance.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating action'

    return JsonResponse(response_data)


@csrf_protect
def add_new_complianceservice_upload(request):
    from onhand.compliance.adapter import get_adapter
    import boto3
    import boto3.s3.transfer
    complianceaction_data = {}
    AWS_ACCESS_KEY = 'AKIAJS67YGGJ3TER3VSQ'
    AWS_ACCESS_SECRET_KEY = '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'

    from datetime import datetime
    import gzip
    try:
        from unittest import mock
    except ImportError:  # Python 3.2 and below
        import mock
    from django.test import TestCase
    from django.conf import settings
    from django.core.files.base import ContentFile
    # from django.utils.six.moves.urllib import parse as urlparse
    from django.utils.timezone import is_aware, utc

    from botocore.exceptions import ClientError

    from storages.backends import s3boto3

    request.self.storage = s3boto3.S3Boto3Storage()
    request.self.storage._connection = mock.MagicMock()

    # s3 = boto3.resource('s3')
    # s3client = boto3.client('s3')

    s3client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_ACCESS_SECRET_KEY
    )

    response = s3client.list_buckets()
    #
    # # Get a list of all bucket names from the response
    # buckets = [bucket['Name'] for bucket in response['Buckets']]
    #
    # # Print out the bucket list
    # print("Bucket List: %s" % buckets)
    #
    bucket_name = 'onhand-dev'
    for bucket in response["Buckets"]:
        print(bucket['Name'])
        bucket_name = str(bucket['Name'])



        # obj = s3.Bucket(bucket['Name']).Object(AWS_ACCESS_KEY)
        # print(obj)

        # result = s3client.get_bucket_acl(Bucket=bucket)
        # print(result)
        theobjects = s3client.list_objects_v2(Bucket=str(bucket['Name']))
        for object in theobjects["Contents"]:
            print(object["Key"])
            # fn = '/tmp/xyz'
            # fp = open(fn, 'w')
            # response = s3client.get_object(Bucket=str(bucket['Name']), Key=object["Key"])
            # contents = response['Body'].read()
            # print("Contents",contents)
            # fp.write(str(contents))
            # fp.close()

    complianceaction_data['form_action'] = request.GET.get('action', None)
    complianceaction_data['form_complianceservice_id'] = request.GET.get('complianceservice_id', None)
    complianceaction_data['filetobeuploadedtitle'] = request.GET.get('filetobeuploadedtitle', None)
    complianceaction_data['filetobeuploaded'] = request.GET.get('filetobeuploaded', None)
    s3client.upload_file(complianceaction_data['filetobeuploaded'], bucket_name,  complianceaction_data['filetobeuploadedtitle'])

    # complianceaction_data['form_basi_code'] = request.GET.get('basi_code', None)
    # complianceaction_data['form_modified_cssc_id'] = request.GET.get('modified_cssc_id', None)
    # complianceaction_data['form_actiontype'] = request.GET.get('actiontype', None)
    # complianceaction_data['form_recordtype'] = request.GET.get('recordtype', None)
    # complianceaction_data['form_recordtype_id'] = request.GET.get('recordtype_id', None)

    response_data = {}
    response_data['result'] = 'success..Pramod'
    response_data['error_message'] = ''

    # Create New Schedule
    if complianceaction_data['form_action'] == 'create':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if complianceaction_data['form_complianceservice_id'] is not None:
                if complianceaction_data['form_recordtype'] == 'Service':
                    if ComplianceServiceSchedule.objects.filter(csrv_id=complianceaction_data['form_complianceservice_id']).exists():
                        # oldcompliance = ComplianceService.objects.get(csrv_id=complianceaction_data['form_complianceservice_id'])
                        # complianceaction_data['oldcompliance'] =oldcompliance
                        # print('Creating complianceserviceaction for ->', oldcompliance.csrv_id)
                        response_data['error_message'] = 'upload sucessfull'


        except Exception as e:
            print('Exception encountered while committing complianceserviceschedule', e)
            print('exception :Error creating new compliance.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating action'

    return JsonResponse(response_data)

@csrf_protect
def add_new_responsible_compliance(request):
    from onhand.compliance.adapter import get_adapter

    responsible_data = {}
    responsible_data['form_action'] = request.GET.get('action', None)
    responsible_data['form_cres_id'] = request.GET.get('cres_id', None)
    responsible_data['form_recordtype_id'] = request.GET.get('csrv_id', None)
    responsible_data['form_responsible'] = request.GET.get('responsible', None)
    responsible_data['form_assigner'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
    responsible_data['form_notes'] = request.GET.get('notes', None)

    response_data = {}
    response_data['result'] = 'success'

    print('AJAX - Responsible Action called')
    print('responsible_data[form_recordtype_id]',responsible_data['form_recordtype_id'])
    print('responsible_data[form_responsible]', responsible_data['form_responsible'])
    print('responsible_data[form_action]', responsible_data['form_action'])

    # Create New Responsible
    if responsible_data['form_action'] == 'create':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if responsible_data['form_recordtype_id'] :
                if ComplianceResponsibility.objects.filter(csrv_id=responsible_data['form_recordtype_id'], cres_is_active='Y').count() == 0:
                    compserviceresponsible = adapter.new_ComplianceResponsibility(request)
                    adapter.save_complianceresponsibility(compserviceresponsible, responsible_data)
                    print('Created New Responsible', compserviceresponsible.cres_id)

        except Exception as e:
            print('Exception encountered while committing compserviceresponsible', e)
            print('exception :Error creating new Schedule.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating Schedule'

    # Udpate Existing Schedule
    if responsible_data['form_action'] == 'update':
        try:
            adapter = get_adapter(request)
            print('get_adapter(request)',adapter)
            if responsible_data['form_recordtype_id'] and responsible_data['form_cres_id']:
                if responsible_data['form_cres_id']:
                    if ComplianceResponsibility.objects.filter(csrv_id=responsible_data['form_recordtype_id'],
                                                               cres_id=responsible_data['form_cres_id'],
                                                               cres_is_active='Y').exists():
                        print('Trying Delete CSSSC_ID')
                        deleteresponsible = ComplianceResponsibility.objects.get(
                            csrv_id=responsible_data['form_recordtype_id'],
                            cres_id=responsible_data['form_cres_id'], cres_is_active='Y')
                        print('deleteschedule', deleteresponsible.cres_id)
                        deleteresponsible.cprs_id_responsible_id = responsible_data['form_responsible']
                        deleteresponsible.cprs_id_assigner_id = responsible_data['form_assigner']
                        deleteresponsible.cres_note = responsible_data['form_notes']
                        deleteresponsible.save(update_fields=['cprs_id_responsible','cprs_id_assigner','cres_note'])

        except Exception as e:
            print('Exception encountered while committing compserviceresponsible', e)
            print('exception :Error creating new Schedule.')
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while creating Schedule'

    # Delete Existing Schedule
    print('Action %s is been called.',responsible_data['form_action'])
    if responsible_data['form_action'] == 'delete':
        try:
            if responsible_data['form_recordtype_id']:
                if responsible_data['form_cres_id'] :
                    if ComplianceResponsibility.objects.filter(csrv_id=responsible_data['form_recordtype_id'],
                                                                             cres_id=responsible_data['form_cres_id'], cres_is_active='Y').exists():
                        print('Trying Delete CSSSC_ID')
                        deleteresponsible = ComplianceResponsibility.objects.get(csrv_id=responsible_data['form_recordtype_id'],
                                                                             cres_id=responsible_data['form_cres_id'], cres_is_active='Y')
                        print('deleteschedule',deleteresponsible.cres_id)
                        deleteresponsible.cres_is_active = 'N'
                        deleteresponsible.save(update_fields=['cres_is_active'])
        except Exception as e:
            print('exception :Error deleting Responsibility.',e)
            response_data['result'] = 'error'
            response_data['error_message'] = 'Error occured while deleting Responsibility'

    return JsonResponse(response_data)


@csrf_protect
def get_vendorcontactlist(request):
    form_vendorselected = request.GET.get('vendorselected', None)

    response_data = {}
    response_data['result'] = 'success'
    response_data['vendorcontact'] = ''
    response_data['phone'] = ''
    response_data['email'] = ''
    response_data['error_message'] = ''
    try:
        if(Company.objects.filter(comp_id=form_vendorselected).exists()):
            vendorcontact = tuple(v_company_people.objects.values_list('cprs_id', 'prsn_name').filter(comp_id=form_vendorselected))
            response_data['vendorcontact'] = vendorcontact
            vendorcontactpoint = (CompanyPersonRole.objects.filter(comp_id=form_vendorselected).first()).prsn
            response_data['phone'] = vendorcontactpoint.office_phone
            response_data['email'] = vendorcontactpoint.email
            if response_data['phone']=='' or response_data['email']=='':
                vendorcompanycontact = Company.objects.get(comp_id=form_vendorselected)
                if response_data['phone']=='':
                    response_data['phone'] = vendorcompanycontact.phone
                if response_data['email']=='':
                   response_data['email'] = vendorcompanycontact.email
            # else:
            #     response_data['result'] = 'NORECORDEXIST'
        else:
            response_data['result'] = 'VENDORNOTFOUND'
    except:
        response_data['result'] = 'ERROR'
        response_data['error_message'] = 'Vendor Contact not found'

    return JsonResponse(response_data)

@csrf_protect
def get_vendorcontactdetails(request):
    form_vendorselectedcontact = request.GET.get('vendorselectedcontact', None)
    form_vendorselected = request.GET.get('vendorselected', None)

    response_data = {}
    response_data['result'] = 'success'
    response_data['phone'] = ''
    response_data['email'] = ''
    response_data['error_message'] = ''

    try:
        if form_vendorselectedcontact:
            vendorcontactpoint = CompanyPersonRole.objects.get(cprs_id=form_vendorselectedcontact).prsn
            response_data['phone'] = vendorcontactpoint.office_phone
            response_data['email'] = vendorcontactpoint.email
            if (response_data['phone'] == '' or response_data['email'] == '') and form_vendorselected:
                vendorcompanycontact = Company.objects.get(comp_id=form_vendorselected)
                if response_data['phone'] == '':
                    response_data['phone'] = vendorcompanycontact.phone
                if response_data['email'] == '':
                    response_data['email'] = vendorcompanycontact.email
    except:
        response_data['result'] = 'ERROR'
        response_data['error_message'] = 'Details for Contact not found'

    return JsonResponse(response_data)
