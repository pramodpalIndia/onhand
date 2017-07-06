from datetime import timedelta
from django.db import models
from django.utils.http import int_to_base36, base36_to_int, urlencode
from django.core.exceptions import ValidationError
import recurly

import math
from itertools import chain

from django import forms
# from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from onhand.compliance import get_complianceservice_model, get_complianceservicefactor_model, \
    get_complianceserviceschedule_model, get_complianceresponsibility_model, get_complianceserviceaction_model, \
    get_providerserviceperson_model
from onhand.subscription import adapter, get_subscription_model, get_company_person_role_model, get_company_language_model, get_person_language_model, \
    get_subscriptiondetail_model, get_secret
from onhand.subscription import app_settings

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
from decimal import *
from datetime import *



import os, sys
import imp

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
# constants = imp.load_source('modulename', 'constants.py')
import random

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


from django.utils import six


from django.contrib.sites.models import Site

from allauth.compat import OrderedDict, importlib

try:
    from django.contrib.auth import update_session_auth_hash
except ImportError:
    update_session_auth_hash = None

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from .exceptions import ImmediateHttpResponse
# from .utils import get_request_param

# from . import signals, get_person_model, get_company_model, get_address_model, get_user_model
from .adapter import get_adapter

def set_form_field_order(form, fields_order):
    assert isinstance(form.fields, OrderedDict)
    form.fields = OrderedDict(
        (f, form.fields[f])
        for f in fields_order)

def get_current_site(request=None):
    """Wrapper around ``Site.objects.get_current`` to handle ``Site`` lookups
    by request in Django >= 1.8.

    :param request: optional request object
    :type request: :class:`django.http.HttpRequest`
    """
    # >= django 1.8
    if request and hasattr(Site.objects, '_get_site_by_request'):
        site = Site.objects.get_current(request=request)
    else:
        site = Site.objects.get_current()

    return site

def get_next_redirect_url(request, redirect_field_name="next"):
    """
    Returns the next URL to redirect to, if it was explicitly passed
    via the request.
    """
    redirect_to = get_request_param(request, redirect_field_name)
    if not get_adapter(request).is_safe_url(redirect_to):
        redirect_to = None
    return redirect_to



def get_firstname_max_length():
    from .app_settings import PERSON_MODEL_FIRSTNAME_FIELD
    from . import get_person_model
    if PERSON_MODEL_FIRSTNAME_FIELD is not None:
        Person = get_person_model()
        max_length = Person._meta.get_field(PERSON_MODEL_FIRSTNAME_FIELD).max_length
    else:
        max_length = 0
    return max_length

def import_attribute(path):
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret

def get_form_class(forms, form_id, default_form):
    print('Utils_get_form_class :', forms)

    form_class = forms.get(form_id, default_form)
    print('Utils_get_form_class :', form_class)
    if isinstance(form_class, six.string_types):
        print('Utils_get_form_class :', import_attribute(form_class))
        form_class = import_attribute(form_class)
    return form_class

def get_request_param(request, param, default=None):
    return request.POST.get(param) or request.GET.get(param, default)

def passthrough_next_redirect_url(request, url, redirect_field_name):
    assert url.find("?") < 0  # TODO: Handle this case properly
    next_url = get_next_redirect_url(request, redirect_field_name)
    if next_url:
        url = url + '?' + urlencode({redirect_field_name: next_url})
    return url


def complianceservice_field(complianceservice, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    print('field and hasattr(complianceservice, field',field , hasattr(complianceservice, field))
    if field and hasattr(complianceservice, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Complianceservice = get_complianceservice_model()
                # v = v[0:Person._meta.get_field(field).max_length]
            setattr(complianceservice, field, v)
        else:
            # Getter
            return getattr(complianceservice, field)

def complianceserviceaction_field(complianceserviceaction, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(complianceserviceaction, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Complianceserviceaction = get_complianceserviceaction_model()
                # v = v[0:Person._meta.get_field(field).max_length]
            setattr(complianceserviceaction, field, v)
        else:
            # Getter
            return getattr(complianceserviceaction, field)

def providerserviceperson_field(providerserviceperson, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(providerserviceperson, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Providerserviceperson = get_providerserviceperson_model()
                # v = v[0:Person._meta.get_field(field).max_length]
            setattr(providerserviceperson, field, v)
        else:
            # Getter
            return getattr(providerserviceperson, field)

def complianceservicefactor_field(complianceservicefactor, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    print('field and hasattr(complianceservicefactor, field',field , hasattr(complianceservicefactor, field))
    print('field and getattr(complianceservicefactor, field', field, getattr(complianceservicefactor, field))
    if field and hasattr(complianceservicefactor, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Complianceservicefactor = get_complianceservicefactor_model()
                # v = v[0:Person._meta.get_field(field).max_length]
            setattr(complianceservicefactor, field, v)
        else:
            # Getter
            return getattr(complianceservicefactor, field)


def complianceserviceschedule_field(complianceserviceschedule, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(complianceserviceschedule, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Complianceserviceschedule = get_complianceserviceschedule_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(complianceserviceschedule, field, v)
        else:
            # Getter
            return getattr(complianceserviceschedule, field)


def complianceresponsibility_field(complianceresponsible, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(complianceresponsible, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Complianceresponsible = get_complianceresponsibility_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(complianceresponsible, field, v)
        else:
            # Getter
            return getattr(complianceresponsible, field)
# def person_field(person, field, *args):
#     """
#     Gets or sets (optional) user model fields. No-op if fields do not exist.
#     """
#     if field and hasattr(person, field):
#         if args:
#             # Setter
#             v = args[0]
#             if v:
#                 Person = get_person_model()
#                 # v = v[0:Person._meta.get_field(field).max_length]
#             setattr(person, field, v)
#         else:
#             # Getter
#             return getattr(person, field)

# def company_field(company, field, *args):
#     """
#     Gets or sets (optional) user model fields. No-op if fields do not exist.
#     """
#     if field and hasattr(company, field):
#         if args:
#             # Setter
#             v = args[0]
#             if v:
#                 Company = get_company_model()
#                 # v = v[0:Company._meta.get_field(field).max_length]
#             setattr(company, field, v)
#         else:
#             # Getter
#             return getattr(company, field)

def company_person_role_field(company_person_role, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(company_person_role, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Company_person_role = get_company_person_role_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(company_person_role, field, v)
        else:
            # Getter
            return getattr(company_person_role, field)

def company_language_field(company_language, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(company_language, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Company_language = get_company_language_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(company_language, field, v)
        else:
            # Getter
            return getattr(company_language, field)

def person_language_field(person_language, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(person_language, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Person_language = get_person_language_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(person_language, field, v)
        else:
            # Getter
            return getattr(person_language, field)

def subscription_field(subscription, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(subscription, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Subscription = get_subscription_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(subscription, field, v)
        else:
            # Getter
            return getattr(subscription, field)

def subscriptiondetail_field(subscriptiondetail, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(subscriptiondetail, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Subscriptiondetail = get_subscriptiondetail_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(subscriptiondetail, field, v)
        else:
            # Getter
            return getattr(subscriptiondetail, field)

# def address_field(address, field, *args):
#     """
#     Gets or sets (optional) user model fields. No-op if fields do not exist.
#     """
#     if field and hasattr(address, field):
#         if args:
#             # Setter
#             v = args[0]
#             if v:
#                 Address = get_address_model()
#                 v = v[0:Address._meta.get_field(field).max_length]
#             setattr(address, field, v)
#         else:
#             # Getter
#             return getattr(address, field)

def plan_display(plan):
    for plan in recurly.Plan.all():
        plan = plan.name
    return plan

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def provider_create_account(request, ohsubscription, person, company, address):

    print('In provider_create_account routine')
    try:
        print("Create Customer Profile -> Using AuthorizeNet : Start")
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = get_secret("API_LOGIN_ID")
        merchantAuth.transactionKey = get_secret("API_TRANSACTION_KEY")

        '''
        Create customer profile
        '''
        createCustomerProfile = apicontractsv1.createCustomerProfileRequest()
        createCustomerProfile.merchantAuthentication = merchantAuth

        createCustomerProfile.profile = apicontractsv1.customerProfileType(str(ohsubscription), person.first_name +' '+person.last_name  , person.email)

        controller = createCustomerProfileController(createCustomerProfile)
        controller.execute()

        response = controller.getresponse()

        if (response.messages.resultCode == "Ok"):
            print("Successfully created a customer profile with id: %s" % response.customerProfileId)
        else:
            print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

        '''
        Create customer payment profile
        '''
        if not response.customerProfileId is None:
            creditCard = apicontractsv1.creditCardType()

            creditCard.cardNumber = request.POST.get("cardnumber", None)
            creditCard.expirationDate = str(request.POST.get("cardyear", None) +'-'+request.POST.get("cardmonth", None))
            creditCard.cardCode = request.POST.get("cardcvv", None)
            payment = apicontractsv1.paymentType()
            payment.creditCard = creditCard

            billTo = apicontractsv1.customerAddressType()
            billTo.firstName = person.first_name
            billTo.lastName = person.last_name
            billTo.company = company.name
            # billTo.ip_address = get_client_ip(request)
            billTo.country = address.city.zipc_code.county.state.country_id
            billTo.address = address.address_line_1 + address.address_line_2
            billTo.city = address.city.name
            billTo.state = address.city.zipc_code.county.state.name
            billTo.zip = address.city.zipc_code_id


            profile = apicontractsv1.customerPaymentProfileType()
            profile.payment = payment
            profile.billTo = billTo
            profile.customerType= 'business'

            createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
            createCustomerPaymentProfile.merchantAuthentication = merchantAuth
            createCustomerPaymentProfile.paymentProfile = profile
            print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" % response.customerProfileId)
            createCustomerPaymentProfile.customerProfileId = str(response.customerProfileId)

            controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
            controller.execute()

            response = controller.getresponse()

            if (response.messages.resultCode == "Ok"):
                print("Successfully created a customer payment profile with id: %s" % response.customerPaymentProfileId)
            else:
                print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)
                print("Create Account -> Using Recurly API : End")

    except ValueError:
        print('Exceprion occured while creating account with Recurly',)
        return None

    print('Authorize.Net.response',response.customerProfileId)
    return response.customerProfileId


def provider_create_subscriptiondetails_from_customer_profile(amount, days, startdate, profileId):
    # Setting the merchant details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = get_secret("API_LOGIN_ID")
    merchantAuth.transactionKey = get_secret("API_TRANSACTION_KEY")
    # Setting payment schedule
    paymentschedule = apicontractsv1.paymentScheduleType()
    paymentschedule.interval = apicontractsv1.paymentScheduleTypeInterval()  # apicontractsv1.CTD_ANON() #modified by krgupta
    paymentschedule.interval.length = days
    paymentschedule.interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.days
    paymentschedule.startDate = startdate
    paymentschedule.totalOccurrences = 999
    paymentschedule.trialOccurrences = 0

    # setting the customer profile details
    profile = apicontractsv1.customerProfileIdType()


    getCustomerProfile = apicontractsv1.getCustomerProfileRequest()
    getCustomerProfile.merchantAuthentication = merchantAuth
    getCustomerProfile.customerProfileId = str(profileId)
    controller = getCustomerProfileController(getCustomerProfile)
    controller.execute()

    response = controller.getresponse()

    paymentProfileId = None
    if (response.messages.resultCode == "Ok"):
        print("Successfully retrieved a customer with profile id %s and customer id %s" % (
        getCustomerProfile.customerProfileId, response.profile.merchantCustomerId))
        if hasattr(response, 'profile') == True:
            profile.customerProfileId = getCustomerProfile.customerProfileId
            if hasattr(response.profile, 'paymentProfiles') == True:
                for paymentProfile in response.profile.paymentProfiles:
                    print("paymentProfile in get_customerprofile is:" % paymentProfile)
                    print("Payment Profile ID %s" % str(paymentProfile.customerPaymentProfileId))
                    paymentProfileId = str(paymentProfile.customerPaymentProfileId)
        else:
            print("Failed to get customer profile information with id %s" % getCustomerProfile.customerProfileId)

    profile.customerPaymentProfileId = paymentProfileId
    profile.customerAddressId = None

    # Setting subscription details
    subscription = apicontractsv1.ARBSubscriptionType()
    subscription.name = "Sample Subscription"
    subscription.paymentSchedule = paymentschedule
    subscription.amount = amount
    subscription.trialAmount = Decimal('0.00')
    subscription.profile = profile

    # Creating the request
    request = apicontractsv1.ARBCreateSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.subscription = subscription

    # Creating and executing the controller
    controller = ARBCreateSubscriptionController(request)
    controller.execute()
    # Getting the response
    response = controller.getresponse()

    if (response.messages.resultCode == "Ok"):
        print("SUCCESS:")
        print("Message Code : %s" % response.messages.message[0]['code'].text)
        print("Message text : %s" % response.messages.message[0]['text'].text)
        print("Subscription ID : %s" % response.subscriptionId)
    else:
        print("ERROR:")
        print("Message Code : %s" % response.messages.message[0]['code'].text)
        print("Message text : %s" % response.messages.message[0]['text'].text)

    return response



def provider_get_subscriptiondetails_from_customer_profile( profileId):
    # Setting the merchant details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = get_secret("API_LOGIN_ID")
    merchantAuth.transactionKey = get_secret("API_TRANSACTION_KEY")
    customerProfileId = None
    # setting the customer profile details
    profile = apicontractsv1.customerProfileIdType()

    getCustomerProfile = apicontractsv1.getCustomerProfileRequest()
    getCustomerProfile.merchantAuthentication = merchantAuth
    getCustomerProfile.customerProfileId = str(profileId)
    controller = getCustomerProfileController(getCustomerProfile)
    controller.execute()

    response = controller.getresponse()

    paymentProfileId = None
    if (response.messages.resultCode == "Ok"):
        print("Successfully retrieved a customer with profile id %s and customer id %s" % (
        getCustomerProfile.customerProfileId, response.profile.merchantCustomerId))
        if hasattr(response, 'profile') == True:
            profile.customerProfileId = getCustomerProfile.customerProfileId
            customerProfileId = getCustomerProfile.customerProfileId
            if hasattr(response.profile, 'paymentProfiles') == True:
                for paymentProfile in response.profile.paymentProfiles:
                    print("paymentProfile in get_customerprofile is:" % paymentProfile)
                    print("Payment Profile ID %s" % str(paymentProfile.customerPaymentProfileId))
                    paymentProfileId = str(paymentProfile.customerPaymentProfileId)
        else:
            print("Failed to get customer profile information with id %s" % getCustomerProfile.customerProfileId)

    return customerProfileId



def complete_signup_prelim_registration(request, person, company, address,ohsubscription, ohsubscriptiondetail, provider_subscription_api_id, company_person_role, signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    # signals.user_signed_up.send(sender=person.__class__,
    #                             request=request,
    #                             person=person,
    #                             **signal_kwargs)
    adapter = get_adapter(request)

    print('complete_signup_prelim person , company, address ,ohsubscription, provider_subscription_api_id, company_person_role',person,company, address ,ohsubscription, provider_subscription_api_id, company_person_role )
    adapter.stash_person(request, person)
    adapter.stash_company( request, company)
    adapter.stash_subscription(request, ohsubscription)
    adapter.stash_subscriptiondetail(request, ohsubscriptiondetail)
    print('adapter.stash_subscription(request, provider_subscription_api_id)',provider_subscription_api_id)
    adapter.stash_providersubscription(request, str(provider_subscription_api_id))
    adapter.stash_company_person_role(request, company_person_role.cprs_id)

    return adapter.respond_person_registered(request)

def complete_signup_prelim_user(request, user, signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    # signals.user_signed_up.send(sender=user.__class__,
    #                             request=request,
    #                             user=user,
    #                             **signal_kwargs)
    adapter = get_adapter(request)
    print('complete_signup_prelim_user(request, user, signal_kwargs=None):',user)
    adapter.stash_user(request, str(user.id))

    return adapter.respond_user_registered(request)

# def url_str_to_person_pk(s):
#     Person = get_person_model()
#     print('Person = get_person_model()' , Person)
#     # TODO: Ugh, isn't there a cleaner way to determine whether or not
#     # the PK is a str-like field?
#     if getattr(Person._meta.pk, 'rel', None):
#         pk_field = Person._meta.pk.rel.to._meta.pk
#         print('Person._meta.pk.rel.to._meta.pk', pk_field)
#     else:
#         pk_field = Person._meta.pk
#     if (hasattr(models, 'UUIDField') and issubclass(
#             type(pk_field), models.UUIDField)):
#         print('hasattr -> return s', s)
#         return str(s)
#     try:
#         pk_field.to_python('a')
#         pk = s
#     except ValidationError:
#         pk = base36_to_int(str(s))
#     return pk
#
# def url_str_to_address_pk(s):
#     Address = get_address_model()
#     print('Person = get_person_model()' , Address)
#     # TODO: Ugh, isn't there a cleaner way to determine whether or not
#     # the PK is a str-like field?
#     if getattr(Address._meta.pk, 'rel', None):
#         pk_field = Address._meta.pk.rel.to._meta.pk
#         print('Person._meta.pk.rel.to._meta.pk', pk_field)
#     else:
#         pk_field = Address._meta.pk
#     if (hasattr(models, 'UUIDField') and issubclass(
#             type(pk_field), models.UUIDField)):
#         print('hasattr -> return s', s)
#         return str(s)
#     try:
#         pk_field.to_python('a')
#         pk = s
#     except ValidationError:
#         pk = base36_to_int(str(s))
#     return pk
#
# def person_pk_to_url_str(person):
#     """
#     This should return a string.
#     """
#     Person = get_person_model()
#     if (hasattr(models, 'UUIDField') and issubclass(
#             type(Person._meta.pk), models.UUIDField)):
#         if isinstance(person.pk, six.string_types):
#             return person.pk
#         return person.pk.hex
#
#     ret = person.pk
#     if isinstance(ret, six.integer_types):
#         ret = int_to_base36(person.pk)
#     return str(ret)
#
# def url_str_to_company_pk(s):
#     Company = get_company_model()
#     print('Person = get_person_model()' , Company)
#     # TODO: Ugh, isn't there a cleaner way to determine whether or not
#     # the PK is a str-like field?
#     if getattr(Company._meta.pk, 'rel', None):
#         pk_field = Company._meta.pk.rel.to._meta.pk
#         print('Company._meta.pk.rel.to._meta.pk', pk_field)
#     else:
#         pk_field = Company._meta.pk
#     if (hasattr(models, 'UUIDField') and issubclass(
#             type(pk_field), models.UUIDField)):
#         print('hasattr -> return s', s)
#         return str(s)
#     try:
#         pk_field.to_python('a')
#         pk = s
#     except ValidationError:
#         pk = base36_to_int(str(s))
#     return pk



def resolve_url(to):
    """
    Subset of django.shortcuts.resolve_url (that one is 1.5+)
    """
    try:
        from django.core import urlresolvers
        return urlresolvers.reverse(to)
    except urlresolvers.NoReverseMatch:
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise
    # Finally, fall back and assume it's a URL
    return to


def get_next_redirect_url(request, redirect_field_name="next"):
    """
    Returns the next URL to redirect to, if it was explicitly passed
    via the request.
    """
    redirect_to = get_request_param(request, redirect_field_name)
    if not get_adapter(request).is_safe_url(redirect_to):
        redirect_to = None
    return redirect_to

def get_request_param(request, param, default=None):
    return request.POST.get(param) or request.GET.get(param, default)
