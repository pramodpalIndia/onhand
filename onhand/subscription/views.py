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
from onhand.insurance.models import InsuranceTypeJurisdiction
from onhand.management.models import City, Zipcode, County, State, NaicsLevel2, NaicsLevel3, NaicsLevel4, NaicsLevel5
# from onhand.subscription.app_settings import app_settings
from onhand.submission.models import SubmissionTypeJurisdiction
from onhand.subscription.adapter import get_adapter
from onhand.subscription.tables import ServicesTable, NameTable, data
from onhand.users.forms import LoginForm
from onhand.users.utils import complete_signup, passthrough_next_redirect_url, get_login_redirect_url
from .utils import (get_next_redirect_url, get_current_site, get_form_class, get_request_param,
                    complete_signup_prelim_registration, complete_signup_prelim_user)
from .forms import RegisterForm, SignupForm, AccountInactiveForm, SignupServiceForm
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
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        self.request = request
        # (end WORKAROUND)
        if request.user.is_authenticated() and \
                app_settings.AUTHENTICATED_LOGIN_REDIRECTS:
            redirect_to = self.get_authenticated_redirect_url()
            response = HttpResponseRedirect(redirect_to)
            return _ajax_response(request, response)
        else:
            print('RedirectAuthenticatedUserMixin', )
            response = super(RedirectAuthenticatedUserMixin,
                                self).dispatch(request,
                                                *args,
                                              **kwargs)
            print('RedirectAuthenticatedUserMixin kwargs.items():',kwargs)
            for key, value in kwargs.items():
                print("%s = %s") % (key, value)
        return response

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
        else:
            response = self.form_invalid(form)
            print('self.form_invalid(form) : ', self.form_invalid(form),self)
        # print(response)
        return _ajax_response(self.request, response, form=form)


class RegistrationView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                FormView):
    form_class = RegisterForm
    # template_name = "Regsitration/register." + app_settings.TEMPLATE_EXTENSION
    template_name = "Registration/register.html"
    context_object_name = 'onhand_plan'
    success_url = None
    redirect_field_name = "next"


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_class(self):
        # return get_form_class(app_settings.FORMS, 'register', self.form_class)
        return  RegisterForm

    def form_valid(self, form):
        success_url = self.get_success_url()
        print("RegistrationView form_valid ")
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
        ret = super(RegistrationView, self).get_context_data(**kwargs)
        onhandplans = Product.objects.filter(prdt_code='PLAN').order_by('prod_code')
        onhandbasisplans = ProductBasis.objects.filter(prdb_is_active='Y',prod_code__in=onhandplans.values('prod_code')).order_by('prod_code','prdb_id')
        print('Provider_Views class RegistrationView, Queryset onhandplans :', onhandplans)
        print('Provider_Views class RegistrationView, Queryset onhandbasisplans :', onhandbasisplans)

        print(onhandplans)
        print(onhandbasisplans)
        ret.update({"onhandplans" : onhandplans,
                    "onhandbasisplans": onhandbasisplans})

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

register = RegistrationView.as_view()


class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin,
                 AjaxCapableProcessFormViewMixin, FormView):

    template_name = "account/signup." + str(app_settings.TEMPLATE_EXTENSION)
    form_class = SignupForm
    redirect_field_name = "next"
    success_url = None


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        print('SignupView_dispatch',request.session.get('account_person', None))
        # args =[defaultservicetable]
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        print('SignupView_get_form_class',self.request.session.get('account_person', None))
        print('SignupView_self.form_class',self.form_class)
        self.kwargs = {'person': self.request.session.get('account_person', None),
                  'company': self.request.session.get('account_company', None)}
        print('app_settings.FORMS',app_settings.FORMS)
        # return get_form_class(app_settings.FORMS, 'signup', self.form_class)
        return self.form_class
        # return SignupForm

    def get_form_kwargs(self):
        print('SignupView_get_form_kwargs')
        kwargs = super(SignupView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        print('SignupView_get_success_url')
        ret = (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or self.success_url)
        print('def get_success_url(self):', self.redirect_field_name , self.success_url )
        return ret

    def form_valid(self, form):
        print('SignupViewform_valid')
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance

        self.user = form.save(self.request)
        try:
            return complete_signup_prelim_user(self.request,  self.user, signal_kwargs=None)
            # return complete_signup(
            #     self.request, self.user,
            #     app_settings.EMAIL_VERIFICATION,
            #     self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):

        print('SignupView_get_context_data')
        ret = super(SignupView, self).get_context_data(**kwargs)
        form = ret['form']

        # defaultservicetable = ServicesTable(ServiceJurisdiction.objects.all())
        # defaultservicetable = NameTable(data)
        # ret.update({"defaultservicetable": defaultservicetable})
        #
        # email = self.request.session.get('account_verified_email')
        # email_keys = ['email']
        # if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
        #     email_keys.append('email2')
        # for email_key in email_keys:
        #     form.fields[email_key].initial = email
        # login_url = passthrough_next_redirect_url(self.request,
        #                                           reverse("account_login"),
        #                                           self.redirect_field_name)
        # redirect_field_name = self.redirect_field_name
        # redirect_field_value = get_request_param(self.request,
        #                                          redirect_field_name)
        # ret.update({"login_url": login_url,
        #             "redirect_field_name": redirect_field_name,
        #             "redirect_field_value": redirect_field_value})
        return ret

signup = SignupView.as_view()



class SignupServiceView(RedirectAuthenticatedUserMixin, CloseableSignupMixin,
                 AjaxCapableProcessFormViewMixin, FormView):

    template_name = "account/signupservice." + str(app_settings.TEMPLATE_EXTENSION)
    form_class = SignupServiceForm
    redirect_field_name = "next"
    success_url = None


    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        print('SignupServiceView',request.session.get('account_user', None))

        # args =[defaultservicetable]
        return super(SignupServiceView, self).dispatch(request, *args, **kwargs)
        # return SignupServiceView.dispatch(self, request, *args, **kwargs)

    def get_form_class(self):
        print('SignupServiceView_get_form_class',self.request.session.get('account_user', None))
        print('SignupServiceView_self.form_class',self.form_class)
        self.kwargs = {'person': self.request.session.get('account_user', None),
                  'company': self.request.session.get('account_company', None)}
        print('app_settings.FORMS',app_settings.FORMS)
        # return get_form_class(app_settings.FORMS, 'signup', self.form_class)
        return self.form_class
        # return SignupForm

    def get_form_kwargs(self):
        print('SignupServiceView_get_form_kwargs')
        kwargs = super(SignupServiceView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        print('SignupServiceView_get_success_url')
        ret = (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or self.success_url)
        print('Signupform- get Success url' ,ret)
        return ret

    def form_valid(self, form):
        print('SignupServiceView_valid')
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance

        self.user = form.save(self.request)
        try:
            return complete_signup(
                self.request, self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):

        print('SignupServiceView_get_context_data')
        ret = super(SignupServiceView, self).get_context_data(**kwargs)
        # ret = SignupServiceView.get_context_data(**kwargs)
        form = ret['form']
        defaultservicetable = ServicesTable(ServiceJurisdiction.objects.all())
        # defaultservicetable = NameTable(data)
        ret.update({"ServiceJurisdiction": ServiceJurisdiction.objects.all()})
        ret.update({"InsuranceJurisdiction": InsuranceTypeJurisdiction.objects.all()})
        ret.update({"SubmissionJurisdiction": SubmissionTypeJurisdiction.objects.all()})
        ret.update({"defaultservicetable": defaultservicetable})
        return ret


    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        print('get_queryset(self): SignupServiceView')
        return ServiceJurisdiction.objects.all()

servicesignup = SignupServiceView.as_view()


class LoginView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                FormView):
    form_class = LoginForm
    template_name = "account/login." + app_settings.TEMPLATE_EXTENSION
    success_url = None
    redirect_field_name = "next"

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'login', self.form_class)

    def form_valid(self, form):
        success_url = self.get_success_url()
        try:
            return form.login(self.request, redirect_url=success_url)
        except ImmediateHttpResponse as e:
            return e.response

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (get_next_redirect_url(
            self.request,
            self.redirect_field_name) or self.success_url)
        return ret

    def get_context_data(self, **kwargs):
        ret = super(LoginView, self).get_context_data(**kwargs)
        signup_url = passthrough_next_redirect_url(self.request,
                                                   reverse("account_signup"),
                                                   self.redirect_field_name)
        redirect_field_value = get_request_param(self.request,
                                                 self.redirect_field_name)
        site = get_current_site(self.request)

        ret.update({"signup_url": signup_url,
                    "site": site,
                    "redirect_field_name": self.redirect_field_name,
                    "redirect_field_value": redirect_field_value})
        return ret

login = LoginView.as_view()

@csrf_protect
def validate_discount_code(request):
    """Toggle "like" for a single color, then refresh the color-list page."""
    plan = request.GET.get('plan', None)
    discount_code = request.GET.get('discount', None)
    print(plan)
    print(discount_code)
    # print(ProductDiscount.objects.filter(disc_code=discount_code).exists())
    # print(Discount.objects.get(disc_code=discount_code).disc_desc)
    try:
        if(ProductDiscount.objects.filter(prdb_id=plan,disc_code=discount_code).exists()):
            data = {
                'valid' : Discount.objects.get(disc_code=discount_code).disc_desc
            }

        if(data['valid'] == False):
             data['error_message'] = 'Promotion code not valid.'
    except:
        data = {
            'error_message': 'Promotion code not valid'
        }

    return JsonResponse(data)

@csrf_protect
def validate_zipcode(request):
    form_zipcode = request.GET.get('zipcode', None)
    form_city = request.GET.get('city', None)
    form_county = request.GET.get('county', None)
    form_state = request.GET.get('state', None)
    response_data = {}

    try:
        print(form_zipcode)
        print(Zipcode.objects.filter(zipc_code=form_zipcode).exists())
        if(Zipcode.objects.filter(zipc_code=form_zipcode).exists()):
            zipcode = Zipcode.objects.get(zipc_code=form_zipcode)
            city_choices = tuple(City.objects.values_list('city_id', 'name').filter(zipc_code=form_zipcode))
            county = zipcode.county
            state = county.state
            response_data['result'] = 'is_valid_zipcode'
            response_data['city'] = city_choices
            response_data['county'] =county.name
            response_data['state'] = state.name
        else:
            print(form_zipcode)
            print('Zipcode not found. else', form_zipcode[:3])
            zipcode = Zipcode.objects.filter(zipc_code__istartswith=form_zipcode[:3])
            print('Zipcode.objects.filter. Done')
            print(zipcode)
            if zipcode.count() > 0:
                zipcode= zipcode[0]
                county = zipcode.county
                state = county.state
                print(county.name)
                print(state.name)
                response_data['result'] = 'is_nearby_zipcode'
                response_data['county'] = county.name
                response_data['state'] = state.name
    except:
        print('exception :Zipcode notd found.')
        response_data['error_message'] = 'Zipcode not sfound.'

    return JsonResponse(response_data)


@csrf_protect
def get_naiclevel(request):
    form_naicslevelopt = request.GET.get('form_naicslevelopt', None)
    form_naicslevel = request.GET.get('form_naicslevel', None)
    response_data = {}
    try:
        print('Ajax request get_naiclevel2(request) -> ',form_naicslevel , form_naicslevelopt )
        if form_naicslevel == 'NAICS_LEVEL1':
            if form_naicslevelopt != None:
                if (NaicsLevel2.objects.filter(naic_level_1_code=form_naicslevelopt).exists()):
                    naicsLevel2_choices = tuple(
                        NaicsLevel2.objects.values_list('naic_level_2_code', 'naic_level_2_desc').filter(
                            naic_level_1_code=form_naicslevelopt))
                    response_data['result'] = 'is_valid_NaicsLevel'
                    response_data['NaicsLevel'] = naicsLevel2_choices
                else:
                    response_data['result'] = 'NaicsLevel_None'
            else:
                response_data['result'] = 'invalid_NaicsLevel'
        elif form_naicslevel == 'NAICS_LEVEL2':
            if form_naicslevelopt != None:
                if (NaicsLevel3.objects.filter(naic_level_2_code=form_naicslevelopt).exists()):
                    naicsLevel3_choices = tuple(
                        NaicsLevel3.objects.values_list('naic_level_3_code', 'naic_level_3_desc').filter(
                            naic_level_2_code=form_naicslevelopt))
                    response_data['result'] = 'is_valid_NaicsLevel'
                    response_data['NaicsLevel'] = naicsLevel3_choices
                else:
                    response_data['result'] = 'NaicsLevel_None'
            else:
                response_data['result'] = 'invalid_NaicsLevel'
        elif form_naicslevel == 'NAICS_LEVEL3':
            if form_naicslevelopt != None:
                if (NaicsLevel4.objects.filter(naic_level_3_code=form_naicslevelopt).exists()):
                    naicsLevel4_choices = tuple(
                        NaicsLevel4.objects.values_list('naic_level_4_code', 'naic_level_4_desc').filter(
                            naic_level_3_code=form_naicslevelopt))
                    response_data['result'] = 'is_valid_NaicsLevel'
                    response_data['NaicsLevel'] = naicsLevel4_choices
                else:
                    response_data['result'] = 'NaicsLevel_None'
            else:
                response_data['result'] = 'invalid_NaicsLevel'
        elif form_naicslevel == 'NAICS_LEVEL4':
            if form_naicslevelopt != None:
                if (NaicsLevel5.objects.filter(naic_level_4_code=form_naicslevelopt).exists()):
                    naicsLevel5_choices = tuple(
                        NaicsLevel5.objects.values_list('naic_level_5_code', 'naic_level_5_desc').filter(
                            naic_level_4_code=form_naicslevelopt))
                    response_data['result'] = 'is_valid_NaicsLevel'
                    response_data['NaicsLevel'] = naicsLevel5_choices
                else:
                    response_data['result'] = 'NaicsLevel_None'
            else:
                response_data['result'] = 'invalid_NaicsLevel'
    except:
        print('exception :NaicsLevel2 not found.')
        response_data['result'] = 'invalid_NaicsLevel'

    return JsonResponse(response_data)


@csrf_protect
def validateselectedonhandplan(request):
    plancode_form = request.GET.get('plan', None)
    discount_code_form = request.GET.get('discount', None)

    response_data = {}
    response_data['plan'] = '-'
    response_data['price'] = '-'
    response_data['billed'] = '-'
    response_data['promotion'] = '-'
    response_data['result'] = "valid"

    try:
        if(ProductBasis.objects.filter(prdb_id__exact=plancode_form).exists()):
            productBasis = ProductBasis.objects.get(prdb_id__exact=plancode_form)
            response_data['plan'] = productBasis.prod_code.prod_name
            response_data['price'] = productBasis.prdb_list_price
            response_data['billed'] = productBasis.basi_code.basi_desc
            if(discount_code_form !="" and ProductDiscount.objects.filter(prdb_id=plancode_form, disc_code=discount_code_form).exists()):
                response_data['promotion'] = ProductDiscount.objects.get(prdb_id=plancode_form, disc_code=discount_code_form).pdis_name
            response_data['result'] = "valid"
        else:
            response_data['result'] = "invalid"
    except:
        response_data['result'] = "invalid"

    return JsonResponse(response_data)



# @user_passes_test(lambda user: not user.username, login_url='/', redirect_field_name=None)

class AccountInactiveView(RedirectAuthenticatedUserMixin,
                AjaxCapableProcessFormViewMixin,
                FormView):
    form_class = AccountInactiveForm
    template_name = "account/account_inactive." + app_settings.TEMPLATE_EXTENSION
    # template_name = (
    #             'account/account_inactive.html')
    # # context_object_name = 'onhand_plan'
    success_url = 'accounts/signup/'
    redirect_field_name = "next"

    def test_func(self):
        return test_settings(self.request.user)

    @sensitive_post_parameters_m
    # @method_decorator(user_passes_test(test_settings, login_url='/'))
    def dispatch(self, request, *args, **kwargs):
        return super(AccountInactiveView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AccountInactiveView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form_class(self):
        # return get_form_class(app_settings.FORMS, 'register', self.form_class)
        return  AccountInactiveForm

    # def form_valid(self, form):
    #     success_url = self.get_success_url()
    #     print("class AccountInactiveView _def form_valid")
    #     try:
    #         print("class AccountInactiveView _def form_valid_form.save(self.request, redirect_url=success_url")
    #         return form.save(self.request, redirect_url=success_url)
    #     except ImmediateHttpResponse as e:
    #         return e.response

    # def get_success_url(self):
    #     # Explicitly passed ?next= URL takes precedence
    #     ret = (get_next_redirect_url(
    #         self.request,
    #         self.redirect_field_name) or self.success_url)
    #     return ret

    def get_context_data(self, **kwargs):
        ret = super(AccountInactiveView, self).get_context_data(**kwargs)
        onhandplans = Product.objects.filter(prdt_code='PLAN').order_by('prod_code')
        print('Provider_Views, Queryset onhandplans :',onhandplans)
        onhandbasisplans = ProductBasis.objects.filter(prdb_is_active='Y',prod_code__in=onhandplans.values('prod_code')).order_by('prod_code','prdb_id')
        print('Provider_Views, Queryset onhandbasisplans :',onhandbasisplans)
        ret.update({"onhandplans" : onhandplans,
                    "onhandbasisplans": onhandbasisplans})

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

account_inactive = AccountInactiveView.as_view()


# # @user_passes_test(lambda user: not user.username, login_url='/', redirect_field_name=None)
# class AccountInactiveView(RedirectAuthenticatedUserMixin,
#                 AjaxCapableProcessFormViewMixin,
#                 FormView):
#     # form_class = get_form_class
#     form_class = AccountInactiveForm
#     template_name = (
#         'account/account_inactive' , app_settings.TEMPLATE_EXTENSION)
#     redirect_field_name = "next"
#     success_url = None
#     print('AccountInactiveView_TemplateView() :')
#
#
#     def get_form_class(self):
#         return get_form_class(app_settings.FORMS, 'account_inactive', self.form_class)
#
#     # def get_success_url(self):
#     #     # Explicitly passed ?next= URL takes precedence
#     #     print('get_success_url')
#     #     ret = (get_next_redirect_url(
#     #         self.request,
#     #         self.redirect_field_name) or self.success_url)
#     #     return ret
#     #
#     # def get_context_data(self, **kwargs):
#     #     print('get_context_data')
#     #     ret = super(AccountInactiveView, self).get_context_data(**kwargs)
#     #     ret.update({"onhandplans": "",
#     #                 "onhandbasisplans": ""})
#     #
#     #     site = get_current_site(self.request)
#     #
#     #     ret.update({"register_url": "/login",
#     #                 "site": site,
#     #                 "redirect_field_value": "/login"})
#     #     return ret
#
#
# account_inactive = AccountInactiveView.as_view

