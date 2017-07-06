from __future__ import unicode_literals
import json
import re
from datetime import date, datetime, timedelta, time
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

from onhand.compliance.models import ComplianceServiceType, ServiceJurisdiction, Factor, ScheduleStatus, \
    ComplianceService
from onhand.management.models import City, Zipcode, State, County, Basis, NaicsLevel5
from onhand.management.utils import calculated_basis_date
from onhand.products.models import ProductDiscount, Discount, ProductBasis
from onhand.subscription.compat import validate_password
from onhand.subscription.models import Address, CompanyRole, Subscription, CompanyPersonRole, Company
# from onhand.subscription.utils import company_person_role_field
# from onhand.subscription.utils import subscriptiondetail_field

from onhand.users import get_user_model
from . import app_settings, get_person_model, get_company_model, get_address_model, \
    get_subscription_model, get_company_person_role_model, get_company_language_model, get_person_language_model, \
    get_subscriptiondetail_model, get_complianceservice_model, get_complianceservicefactor_model, \
    get_complianceserviceschedule_model, get_complianceresponsibility_model, get_complianceserviceaction_model, \
    get_providerserviceperson_model
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

    def new_complianceserviceaction(self, request):
        """
        Instantiates a new User instance.
        """
        complianceserviceaction = get_complianceserviceaction_model()()
        return complianceserviceaction

    def new_providerserviceperson(self, request):
        """
        Instantiates a new User instance.
        """
        providerserviceperson = get_providerserviceperson_model()()
        return providerserviceperson

    def new_complianceservicefactor(self, request):
        """
        Instantiates a new User instance.
        """
        complianceservicefactor = get_complianceservicefactor_model()()
        return complianceservicefactor

    def new_ComplianceServiceSchedule(self, request):
        """
        Instantiates a new schedule instance.
        """
        complianceserviceschedule  = get_complianceserviceschedule_model()()
        print('new_ComplianceServiceSchedule',complianceserviceschedule)
        return complianceserviceschedule

    def new_ComplianceResponsibility(self, request):
        """
        Instantiates a new schedule instance.
        """
        complianceresponsibility  = get_complianceresponsibility_model()()
        print('new_complianceresponsibility',complianceresponsibility)
        return complianceresponsibility

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

    def save_complianceserviceschedule(self, complianceserviceschedule, scheduled_data, commit=True):
        from onhand.compliance.utils import complianceserviceschedule_field

        try:
            if scheduled_data['form_recordtype_id']:
                complianceserviceschedule_field(complianceserviceschedule, 'csrv_id',  ComplianceService.objects.get(pk=scheduled_data['form_recordtype_id']).csrv_id)
                print('scheduled_data[form_recordtype_id]',scheduled_data['form_recordtype_id'], ComplianceService.objects.get(pk=scheduled_data['form_recordtype_id']).csrv_due_date)

            if scheduled_data['form_vendorid']:
                complianceserviceschedule_field(complianceserviceschedule, 'comp_id', Company.objects.get(pk=scheduled_data['form_vendorid']).comp_id)
                print('scheduled_data[form_vendorid]', scheduled_data['form_vendorid'])

            if scheduled_data['form_schedule_status']:
                complianceserviceschedule_field(complianceserviceschedule, 'schs_code', ScheduleStatus.objects.get(pk=scheduled_data['form_schedule_status']))
                print('scheduled_data[form_schedule_status]', scheduled_data['form_schedule_status'])

            if scheduled_data['form_vendorcontactroleid']:
                complianceserviceschedule_field(complianceserviceschedule, 'cprs_id_provider', CompanyPersonRole.objects.get(pk=scheduled_data['form_vendorcontactroleid']))
                print('scheduled_data[form_vendorcontactroleid]', CompanyPersonRole.objects.get(pk=scheduled_data['form_vendorcontactroleid']).cprs_id)

            if scheduled_data['form_responsible']:
                complianceserviceschedule_field(complianceserviceschedule, 'cprs_id_responsible',CompanyPersonRole.objects.get(pk=scheduled_data['form_responsible']))
                print('scheduled_data[form_responsible]', scheduled_data['form_responsible'])

            if scheduled_data['form_assigner']:
                complianceserviceschedule_field(complianceserviceschedule, 'cprs_id_assigner', CompanyPersonRole.objects.get(pk=scheduled_data['form_assigner']))
                print('scheduled_data[form_assigner]', scheduled_data['form_assigner'])

            if scheduled_data['form_schedule']:
                # scheduledate = datetime.strptime(scheduled_data['form_schedule'], '%m/%d/%y %H:%M')
                # scheduledate = datetime(*time.strptime(scheduled_data['form_schedule'], "%m/%d/%y %H:%M")[:5])
                # scheduledate = scheduledate.date()
                complianceserviceschedule_field(complianceserviceschedule, 'cssc_service_date',  datetime.strptime(scheduled_data['form_schedule'], '%m/%d/%y %H:%M') )
                print('scheduled_data[form_schedule] , -- scheduledate',scheduled_data['form_schedule'],  datetime.strptime(scheduled_data['form_schedule'], '%m/%d/%y %H:%M'))

            if scheduled_data['form_notes']:
                complianceserviceschedule_field(complianceserviceschedule, 'cssc_note', scheduled_data['form_notes'])
                print('scheduled_data[form_notes]', scheduled_data['form_notes'])

            complianceserviceschedule_field(complianceserviceschedule, 'cssc_date', datetime.now())
            print('date.today()', datetime.now())


            if commit:
                complianceserviceschedule.save()
                print('Saving Schedule: Provider_Adapter_save_complianceserviceschedule', complianceserviceschedule)

        except Exception as e:
            print('Exception encountered while committing complianceserviceschedule', e)

        return complianceserviceschedule

    def save_complianceresponsibility(self, compserviceresponsible, scheduled_data, commit=True):
        from onhand.compliance.utils import complianceresponsibility_field

        try:
            if scheduled_data['form_recordtype_id']:
                complianceresponsibility_field(compserviceresponsible, 'csrv_id',  ComplianceService.objects.get(pk=scheduled_data['form_recordtype_id']).csrv_id)
                print('scheduled_data[form_recordtype_id]',scheduled_data['form_recordtype_id'], ComplianceService.objects.get(pk=scheduled_data['form_recordtype_id']).csrv_due_date)

            if scheduled_data['form_responsible']:
                complianceresponsibility_field(compserviceresponsible, 'cprs_id_responsible',CompanyPersonRole.objects.get(pk=scheduled_data['form_responsible']))
                                               # CompanyPersonRole.objects.get(pk=scheduled_data['form_responsible']))
                print('scheduled_data[form_responsible]', scheduled_data['form_responsible'])

            if scheduled_data['form_assigner']:
                complianceresponsibility_field(compserviceresponsible, 'cprs_id_assigner',CompanyPersonRole.objects.get(pk=scheduled_data['form_assigner']))
                                               # CompanyPersonRole.objects.get(pk=scheduled_data['form_assigner']))
                print('scheduled_data[form_assigner]', scheduled_data['form_assigner'])

            complianceresponsibility_field(compserviceresponsible, 'cres_is_active','Y')

            if scheduled_data['form_notes']:
                complianceresponsibility_field(compserviceresponsible, 'cres_note', scheduled_data['form_notes'])
                print('scheduled_data[form_notes]', scheduled_data['form_notes'])

            complianceresponsibility_field(compserviceresponsible, 'cres_date', datetime.now())

            if commit:
                compserviceresponsible.save()
                print('Saving Schedule: Provider_Adapter_save_complianceserviceschedule', compserviceresponsible)

        except Exception as e:
            print('Exception encountered while committing compserviceresponsible', e)

        return compserviceresponsible

    def save_complianceservice(self, request, complianceservice_new, form,  commit=True, **subscription_kwargs):
        from .utils import complianceservice_field
        data = form.cleaned_data

        frequency = data.get('frequency',None)
        servicejurisdiction = data.get('complianceservice')
        nextservicedate = data.get('nextservicedate')
        servicenote = data.get('servicenote')
        factorvalue = data.get('factorvalue')

        print(servicejurisdiction.srvj_id,frequency.basi_code,nextservicedate,servicenote,factorvalue)


        print('account_subscription, account_company, account_county', request.session['account_subscription'],
              request.session['account_company'], request.session['account_county'])

        try:
            print('Saving basis code: ',Basis.objects.get(basi_code=frequency.basi_code).basi_code)
            if frequency is not None:
                complianceservice_field(complianceservice_new, 'basi_code', Basis.objects.get(basi_code=frequency.basi_code))
            print('Saved basis code  on to complianceservice: ', frequency.basi_code)

            if servicejurisdiction is not None:
                complianceservice_field(complianceservice_new, 'srvj_id', int(servicejurisdiction.srvj_id))

            complianceservice_field(complianceservice_new, 'subs_id', request.session['account_subscription'])

            if nextservicedate and frequency :
                nextservicedate = datetime.strptime(nextservicedate, '%m/%d/%y')
                nextservicedate = nextservicedate.date()
                print('nextservicedate - timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days)',nextservicedate, timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days))
                alert_date  = nextservicedate - timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days)
                complianceservice_field(complianceservice_new, 'csrv_alert_date', alert_date)

            if nextservicedate :
                complianceservice_field(complianceservice_new, 'csrv_due_date', nextservicedate)

            if servicenote :
                complianceservice_field(complianceservice_new, 'csrv_note', servicenote)

            if commit:
                complianceservice_new.save()
                print('Saved new Complianceservice',complianceservice_new.csrv_id)

        except Exception as e:
            print('Exception encountered while Creating new Compliance record ', e)

        return complianceservice_new

    def save_complianceservice_ajax(self, complianceservice, complianceaction_data, commit=True):
        from .utils import complianceservice_field

        try:
            # basis_code = Basis.objects.get(pk=complianceaction_data['oldcompliance'].basi_code)
            # print('save_complianceservice_ajax- complianceaction_data[oldcompliance].basi_code',basis_code.basi_code)
            # complianceservice_field(complianceservice, 'basi_code', basis_code.basi_code)
            # complianceservice_field(complianceservice, 'basi_code', basis_code.basi_code)
            if complianceaction_data['oldcompliance'].basi_code is not None:
                print('ssaving basis_code', str(complianceaction_data['oldcompliance'].basi_code))
                complianceservice_field(complianceservice, 'basi_code', complianceaction_data['oldcompliance'].basi_code)


            # print('save_complianceservice_ajax- complianceaction_data[oldcompliance].srvj_id',
            #       complianceaction_data['oldcompliance'].srvj_id)
            if complianceaction_data['oldcompliance'].srvj_id is not None:
                complianceservice_field(complianceservice, 'srvj_id', int(complianceaction_data['oldcompliance'].srvj_id))

            complianceservice_field(complianceservice, 'subs_id', complianceaction_data['oldcompliance'].subs_id)

            if complianceaction_data['nextservicedate'] and complianceaction_data['oldcompliance'].basi_code :
                nextservicedate = datetime.strptime(complianceaction_data['nextservicedate'], '%m/%d/%y')
                nextservicedate = nextservicedate.date()
                print('nextservicedate - timedelta(days=Basis.objects.get(basi_code=frequency.basi_code).basi_alert_days)',nextservicedate, timedelta(days=Basis.objects.get(basi_code=complianceaction_data['oldcompliance'].basi_code).basi_alert_days))
                alert_date  = nextservicedate - timedelta(days=Basis.objects.get(basi_code=complianceaction_data['oldcompliance'].basi_code).basi_alert_days)
                complianceservice_field(complianceservice, 'csrv_alert_date', alert_date)

            if complianceaction_data['nextservicedate']:
                complianceservice_field(complianceservice, 'csrv_due_date', datetime.strptime(complianceaction_data['nextservicedate'], '%m/%d/%y'))

            print('save_complianceservice_ajax- complianceaction_data[form_notes]',
                  complianceaction_data['form_notes'])
            if complianceaction_data['form_notes'] :
                complianceservice_field(complianceservice, 'csrv_note', complianceaction_data['form_notes'])
            print('Commiting save_complianceservice_ajax')

            if commit:
                complianceservice.save()
                print('Saved new Complianceservice',complianceservice.csrv_id)
        except Exception as e:
            print('Exception encountered while committing ', e)

        return complianceservice

    def save_complianceserviceaction_ajax(self, complianceserviceaction, complianceaction_data, oldcomplianceservice, commit=True):
        from .utils import complianceserviceaction_field


        if oldcomplianceservice is not None:
            complianceserviceaction_field(complianceserviceaction, 'csrv_id', oldcomplianceservice.csrv_id)

        if complianceaction_data['form_vendorid'] is not None:
            complianceserviceaction_field(complianceserviceaction, 'comp_id', complianceaction_data['form_vendorid'])

        if complianceaction_data['form_schedule'] is not None:
            complianceserviceaction_field(complianceserviceaction, 'cssc_id', complianceaction_data['form_schedule'])

        if complianceaction_data['actiondate']:
            complianceserviceaction_field(complianceserviceaction, 'csac_service_date', datetime.strptime(complianceaction_data['actiondate'], '%m/%d/%y'))


        if complianceaction_data['form_price']:
            complianceserviceaction_field(complianceserviceaction, 'csac_price', complianceaction_data['form_price'])

        if complianceaction_data['form_notes']:
            complianceserviceaction_field(complianceserviceaction, 'csac_note', complianceaction_data['form_notes'])


        if complianceaction_data['form_assigner']:
            complianceserviceaction_field(complianceserviceaction, 'cprs_id',CompanyPersonRole.objects.get(pk=complianceaction_data['form_assigner']))

            complianceserviceaction_field(complianceserviceaction, 'csac_date', datetime.now())

        if commit:
            complianceserviceaction.save()
            print('Saved new Complianceservice Action',complianceserviceaction.csac_id)

        return complianceserviceaction

    def save_complianceservicefactor(self, request, compliancefactor, complianceservice, form,  commit=True, **subscription_kwargs):
        from .utils import complianceservicefactor_field
        data = form.cleaned_data

        complianceservice = data.get('complianceservice')
        factorvalue = data.get('factorvalue')

        print('compliancefactor, complianceservice,factorvalue',compliancefactor, complianceservice.srvj_id,factorvalue)
        if factorvalue:
            if Factor.objects.filter(ctyp_id=complianceservice.srvj_id).exists():
                factorcode = Factor.objects.get(ctyp_id=complianceservice.srvj_id).fact_code
                complianceservicefactor_field(compliancefactor, 'csrv_id', complianceservice.csrv_id)
                print('csrv_id Done!')
                complianceservicefactor_field(compliancefactor, 'fact_code', factorcode)
                print('fact_code Done!')
                complianceservicefactor_field(compliancefactor, 'fval_value', factorvalue)
                print('fval_value Done!',factorvalue)

        if commit:
            compliancefactor.save()
            print('Saved new Compliancefactor')

        return compliancefactor

    def save_providerserviceperson_ajax(self, serviceproviderperson, complianceserviceaction, companyperson , commit=True):
        from .utils import providerserviceperson_field

        try:
            if companyperson:
                providerserviceperson_field(serviceproviderperson, 'csac_id', complianceserviceaction.csac_id)
                providerserviceperson_field(serviceproviderperson, 'cprs_id', CompanyPersonRole.objects.get(pk=companyperson).cprs_id)

            if commit:
                serviceproviderperson.save()
                print('Saved new serviceproviderperson',serviceproviderperson.psvp_id)

        except Exception as e:
            print('Exception encountered while committing compserviceresponsible', e)

        return serviceproviderperson

    def save_complianceservicefactor_ajax(self, compliancefactor, complianceservice, oldfactorvalue, commit=True):
        from .utils import complianceservicefactor_field

        print('save_complianceservicefactor_ajax for complianceservice using oldfactorvalue ',oldfactorvalue.csrv_id, oldfactorvalue.fact,oldfactorvalue.fval_value )
        if oldfactorvalue:
            # if Factor.objects.filter(csrv_id=oldfactorvalue.csrv_id).exists():
            #     print('Inside filter for complianceservice using oldfactorvalue ',
            #           oldfactorvalue.csrv_id, oldfactorvalue.fact_code, oldfactorvalue.fval_value)
                # factorcode = Factor.objects.get(ctyp_id=complianceservice.srvj_id).fact_code
            complianceservicefactor_field(compliancefactor, 'csrv_id', complianceservice.csrv_id)
            complianceservicefactor_field(compliancefactor, 'fact_id',  Factor.objects.get(pk=oldfactorvalue.fact).fact_code)
            complianceservicefactor_field(compliancefactor, 'fval_value', oldfactorvalue.fval_value)
                # print('fval_value Done!',factorvalue)
        if commit:
            compliancefactor.save()
            print('Created new Compliancefactor',compliancefactor.fval_id)

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

