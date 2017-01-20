from __future__ import unicode_literals
import json
import re
from datetime import date, datetime, timedelta
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
# from .utils import import_attribute
# from onhand.subscription.utils import import_attribute
from django.urls import reverse
from django.utils import six, dateparse

from onhand.compliance.models import ComplianceServiceType, ServiceJurisdiction, Factor
from onhand.management.models import City, Zipcode, State, County, Basis, NaicsLevel5
from onhand.management.utils import calculated_basis_date
from onhand.products.models import ProductDiscount, Discount, ProductBasis
from onhand.subscription.compat import validate_password
from onhand.subscription.models import Address, CompanyRole, Subscription
# from onhand.subscription.utils import company_person_role_field
# from onhand.subscription.utils import subscriptiondetail_field

from onhand.users import get_user_model
from . import app_settings, get_person_model, get_company_model, get_address_model, \
    get_subscription_model, get_company_person_role_model, get_company_language_model, get_person_language_model, \
    get_subscriptiondetail_model, get_complianceservice_model, get_complianceservicefactor_model
from django.utils.translation import ugettext_lazy as _

from onhand.subscription.compat import importlib
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text



class DefaultComplianceAdapter(object):

    # Don't bother turning this into a setting, as changing this also
    # requires changing the accompanying form error message. So if you
    # need to change any of this, simply override clean_username().
    #
    # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **
    # ^ (?:4[0 - 9] {12}(?:[0 - 9] {3})?  # Visa
    # | (?:5[1 - 5][0 - 9] {2}  # MasterCard
    # | 222[1 - 9] | 22[3 - 9][0 - 9] | 2[3 - 6][0 - 9] {2} | 27[01][0 - 9] | 2720)[0 - 9]{12}
    # | 3[47][0 - 9]  {13}  # American Express
    # | 3(?:0[0 - 5] | [68][0 - 9])[0 - 9] {11}  # Diners Club
    # | 6(?:011 | 5[0 - 9] {2})[0 - 9] {12}  # Discover
    # | (?:2131 | 1800 | 35\d {3})\d {11}  # JCB
    # )$
    # ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **

    numeric_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")
    name_regex =  re.compile(r'^[a-zA-Z0-9_\s]*$')
    address_regex = re.compile(r'^[A-Za-z0-9_\.\-\s\,]*$')
    Credit_Card_Numbers_regex = re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|(?:5[1-5][0-9]{2}|2720|27[01][0-9]|2[3-6][0-9]{2}|22[3-9][0-9]|222[1-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35[0-9]{3})[0-9]{11})\b')
    Credit_Card_CVV_regex = re.compile(r'^([0-9]{3,4})$')
    username_regex = re.compile(r'^[\w.@+-]+$')
    error_messages = {

    }

    # name_regex = re.compile(r'^[\w.@+-]+$')
    error_messages = {
        'complianceservice_required':
            _('Service type is mandatory'),
        'complianceservice_invalid':
        _('Service type selected is invalid'),
        'frequency_required':
            _('Service frequency is mandatory'),
        'frequency_invalid':
            _('Service frequency selected is invalid'),
        'factorvalue_invalid':
            _('Enter a valid numeric value'),
        'nextservicedate_required':
            _('Next Due date is mandatory'),
        'nextservicedate_invalid':
            _('Next Due date is invalid'),
    }

    def __init__(self, request=None):
        self.request = request


    def new_complianceservice(self, request):
        """
        Instantiates a new User instance.
        """
        complianceservice = get_complianceservice_model()()
        return complianceservice

    def new_complianceservicefactor(self, request):
        """
        Instantiates a new User instance.
        """
        complianceservicefactor = get_complianceservicefactor_model()()
        return complianceservicefactor

    def populate_complianceservice(self, request, complianceservice):
        """
        Fills in a valid username, if required and missing.  If the
        person is already present it is assumed to be valid
        (unique).
        """
        from .utils import complianceservice_field
        print('populate_complianceservice')
        print(complianceservice)
        basi_code = complianceservice_field(complianceservice, 'basi_code')
        srvj_id = complianceservice_field(complianceservice, 'srvj_id')
        subs_id = complianceservice_field(complianceservice, 'subs_id')
        csrv_alert_date = complianceservice_field(complianceservice, 'csrv_alert_date')
        csrv_due_date = complianceservice_field(complianceservice, 'csrv_due_date')
        csrv_note = complianceservice_field(complianceservice, 'csrv_note')



    def populate_subscription(self, request, subscription):
        from .utils import subscription_field
        subscriptionid = subscription_field(subscription, 'subs_id')

    def set_basi_code(self, complianceservice, basi_code):
        complianceservice.set_basi_code(basi_code)
        complianceservice.save()

    def set_srvj_id(self, complianceservice, srvj_id):
        complianceservice.set_srvj_id(srvj_id)
        complianceservice.save()

    def set_subs_id(self, complianceservice, subs_id):
        complianceservice.set_subs_id(subs_id)
        complianceservice.save()

    def set_csrv_alert_date(self, complianceservice, csrv_alert_date):
        complianceservice.set_csrv_alert_date(csrv_alert_date)
        complianceservice.save()

    def set_csrv_due_date(self, complianceservice, csrv_due_date):
        complianceservice.set_csrv_due_date(csrv_due_date)
        complianceservice.save()

    def set_csrv_note(self, complianceservice, csrv_note):
        complianceservice.set_csrv_note(csrv_note)
        complianceservice.save()

    def clean_complianceservice(self, complianceopt):
        print('** Compliance dropdown check : ', complianceopt)

        if complianceopt is None:
            raise forms.ValidationError(
                self.error_messages['complianceservice_required'])
        else:
            if (complianceopt == 'add'):
                pass
            else:
                try:
                    if ServiceJurisdiction.objects.filter(srvj_id=complianceopt.srvj_id).exists():
                        pass
                    else:
                        raise forms.ValidationError(
                            self.error_messages['complianceservice_invalid'])
                except KeyError:
                    raise forms.ValidationError(
                        self.error_messages['complianceservice_invalid'])
        return complianceopt

    def clean_factorvalue(self, factorvalue, shallow=False):
        print('** factorvalue  check : ', factorvalue)
        if factorvalue:
            if not self.numeric_format.match(str(factorvalue)):
                raise forms.ValidationError(
                self.error_messages['factorvalue_invalid'])
        return factorvalue

    def clean_frequency(self, frequencyopt, shallow=False):
        print('** frequencyopt dropdown check : ', frequencyopt)

        if frequencyopt is None:
            raise forms.ValidationError(
                self.error_messages['frequency_required'])
        else:
            try:
                Basis.objects.filter(basi_code=frequencyopt).exists()
            except KeyError:
                raise forms.ValidationError(
                    self.error_messages['frequency_invalid'])
        return frequencyopt


    def clean_lastservicedate(self, lastservicedate, shallow=False):
        print("Validating lastservicedate :", lastservicedate)
        return lastservicedate

    def clean_nextservicedate(self, nextservicedate, shallow=False):
        print("Validating nextservicedate :", nextservicedate)
        if not nextservicedate and  nextservicedate is date:
            raise forms.ValidationError(
                    self.error_messages['nextservicedate_required'])
        return nextservicedate


    def clean_servicenote(self, servicenote, shallow=False):
        print("Validating servicenote :", servicenote)
        return servicenote


    def save_complianceservice(self, request, complianceservice, form,  commit=True, **subscription_kwargs):
        from .utils import complianceservice_field
        data = form.cleaned_data

        frequency = data.get('frequency')
        complianceservice = data.get('complianceservice')
        nextservicedate = data.get('nextservicedate')
        servicenote = data.get('servicenote')
        factorvalue = data.get('factorvalue')

        print(complianceservice.srvj_id,frequency.basi_code,nextservicedate,servicenote,factorvalue)


        print('account_subscription, account_company, account_county', request.session['account_subscription'],
              request.session['account_company'], request.session['account_county'])

        if frequency is not None:
            complianceservice_field(complianceservice, 'basi_code', frequency.basi_code)

        if complianceservice is not None:
            complianceservice_field(complianceservice, 'srvj_id', int(complianceservice.srvj_id))

        complianceservice_field(complianceservice, 'subs_id', request.session['account_subscription'])

        if nextservicedate and frequency :
            nextservicedate = datetime.strptime(nextservicedate, '%m/%d/%y')
            nextservicedate = nextservicedate.date()
            print('nextservicedate - timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days)',nextservicedate, timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days))
            alert_date  = nextservicedate - timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days)
            complianceservice_field(complianceservice, 'csrv_alert_date', alert_date)

        if nextservicedate :
            complianceservice_field(complianceservice, 'csrv_due_date', nextservicedate)

        if servicenote :
            complianceservice_field(complianceservice, 'csrv_note', servicenote)

        if commit:
            complianceservice.save()
            print('Saved new Complianceservice',complianceservice.csrv_id)

        return complianceservice


    def save_complianceservicefactor(self, request, compliancefactor, complianceservice, form,  commit=True, **subscription_kwargs):
        from .utils import complianceservicefactor_field
        data = form.cleaned_data

        complianceservice = data.get('complianceservice')
        factorvalue = data.get('factorvalue')

        print('compliancefactor, complianceservice,factorvalue',compliancefactor, complianceservice.srvj_id,factorvalue)
        if factorvalue:
            if Factor.objects.filter(ctyp_id=complianceservice.srvj_id).exists():
                factorcode = Factor.objects.get(ctyp_id=complianceservice.srvj_id).fact_code
                complianceservicefactor_field(compliancefactor, 'csrv_id', int(complianceservice.srvj_id))
                print('csrv_id Done!')
                complianceservicefactor_field(compliancefactor, 'fact_code', factorcode)
                print('fact_code Done!')
                complianceservicefactor_field(compliancefactor, 'fval_value', factorvalue)
                print('fval_value Done!',factorvalue)

        if commit:
            compliancefactor.save()
            print('Saved new Compliancefactor')

        return compliancefactor


    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        """
        Wrapper of `django.contrib.messages.add_message`, that reads
        the message text from a template.
        """
        if 'django.contrib.messages' in settings.INSTALLED_APPS:
            try:
                if message_context is None:
                    message_context = {}
                message = render_to_string(message_template,
                                           message_context).strip()

                if message:
                    messages.add_message(request, level, message,
                                         extra_tags=extra_tags)
                    print('def add_message : ', message_template ,message, extra_tags)
            except TemplateDoesNotExist:
                pass

    def ajax_response(self, request, response, redirect_to=None, form=None):
        data = {}
        status = response.status_code

        if redirect_to:
            status = 200
            data['location'] = redirect_to
        if form:
            if form.is_valid():
                status = 200
            else:
                status = 400
                data['form_errors'] = form._errors
            if hasattr(response, 'render'):
                response.render()
            data['html'] = response.content.decode('utf8')
        return HttpResponse(json.dumps(data),
                            status=status,
                            content_type='application/json')

    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        return is_safe_url(url)


def get_adapter(request=None):
    path= 'onhand.compliance.adapter.DefaultComplianceAdapter'
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return (ret)(request)

