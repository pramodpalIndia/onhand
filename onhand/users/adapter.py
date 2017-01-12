# -*- coding: utf-8 -*-
from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils import six

import json
import re
import time
import warnings
import hashlib

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login, get_backends
from django.contrib.auth import logout as django_logout, authenticate
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


# from onhand.subscription import app_settings
from onhand.subscription.adapter import DefaultAccountAdapter
from onhand.subscription.compat import importlib


from onhand.management.models import Role, Zipcode, City, NaicsLevel5, Language
from onhand.subscription.models import Person, Company, Subscription, CompanyLanguage, PersonLanguage, CompanyPersonRole, \
    CompanyRole, SubscriptionDetail
from onhand.subscription.utils import url_str_to_person_pk, person_field, url_str_to_company_pk, company_field, \
    address_field, subscription_field, company_language_field, person_language_field, company_person_role_field, \
    get_current_site, subscriptiondetail_field
from onhand.users import app_settings
from onhand.users.utils import user_username, user_field, resolve_url
from . import get_user_model

from onhand.subscription.adapter import get_adapter

class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        # from .utils import user_username, user_email, user_field

        data = form.cleaned_data

        person_pk = None
        company_pk = None
        person = None
        company = None
        # companypersonrole = None

        # Update Company Model
        company_pk_str = request.session.get('account_company', None)
        if company_pk_str:
            company_pk = url_str_to_company_pk(company_pk_str)
            company = Company.objects.get(comp_id=company_pk_str)
            if company:
                company_field(company, 'comp_name', data.get('compname'))
                company_field(company, 'comp_email', data.get('compemail'))
                company_field(company, 'comp_website', data.get('website'))
                company_field(company, 'comp_phone', data.get('phone'))
                company_field(company, 'comp_phone', data.get('phone'))
                company_field(company, 'fax', data.get('fax'))

                # Update Address for the company
                address = company.address
                Form_Data_addressline1 = data.get('addressline1')
                Form_Data_addressline2 = data.get('addressline2')
                Form_Data_zipcode = data.get('zipcode')
                Form_Data_cityopt = data.get('cityopt')
                Form_Data_city = data.get('city')
                city = None
                if (Zipcode.objects.filter(zipc_code=Form_Data_zipcode).exists()):
                    if (City.objects.filter(
                        zipc_code=Form_Data_zipcode).exists() and Form_Data_cityopt != 'None' and Form_Data_city):
                        if (City.objects.filter(name=Form_Data_city, zipc_code=Form_Data_zipcode).exists()):
                            city = City.objects.get(name=Form_Data_city, zipc_code=Form_Data_zipcode).city_id.__str__()
                        else:
                            city = City.objects.create(zipc_code=Zipcode.objects.get(zipc_code=Form_Data_zipcode),
                                                       name=Form_Data_city, city_is_user_added='Y')
                        city_id_str = city.__str__()
                    else:
                        city_id_str = Form_Data_cityopt.city_id.__str__()
                        city = City.objects.get(city_id=city_id_str).city_id.__str__()

                if Form_Data_addressline1:
                    address_field(address, 'address_line_1', Form_Data_addressline1)
                if Form_Data_addressline2:
                    address_field(address, 'address_line_2', Form_Data_addressline2)
                if city:
                    address_field(address, 'city_id', city_id_str)

                self.populate_address(request, address)
                print('Saving Changed address for Company in user adapter',address)
                address.save()
                print('Address Saved')

                #TODO : traverse the array list if language is more then one
                if(CompanyLanguage.objects.filter(comp_id=company.comp_id).exists()):
                    CompanyLanguage.objects.filter(comp_id=company.comp_id).all().delete()
                companylanguagechecklist = list(data.get('languagechecklist'))
                print('companylanguagechecklist :', len(companylanguagechecklist))
                if len(companylanguagechecklist) > 1:
                    for language in companylanguagechecklist:
                        print("companylanguagechecklist : Language.lang_code", language.lang_code)
                        adapter = get_adapter(request)
                        if (CompanyLanguage.objects.filter(comp_id=company.comp_id, lang_code=language.lang_code).exists()):
                            companylanguage = CompanyLanguage.objects.get(comp_id=company.comp_id, lang_code=language.lang_code)
                            company_language_field(companylanguage, 'lang_code',
                                                   Language.objects.get(pk=language.lang_code))
                            company_language_field(companylanguage, 'comp_id', company.comp_id)
                            if commit:
                                print('companylanguage.update()')
                                companylanguage.update()
                        else:
                            companylanguage = adapter.new_company_language(request)
                            company_language_field(companylanguage, 'lang_code',
                                                   Language.objects.get(pk=language.lang_code))
                            company_language_field(companylanguage, 'comp_id', company.comp_id)
                            if commit:
                                print('companylanguage.save()')
                                companylanguage.save()
            self.populate_company(request, company)


        ohsubscription_pk_str = request.session.get('ohaccount_subscription', None)
        print('ohsubscription_pk_str and data.get(naicslevel5opt)',ohsubscription_pk_str,data.get('naicslevel5opt'))
        if ohsubscription_pk_str and data.get('naicslevel5opt'):
            if(Subscription.objects.filter(pk=ohsubscription_pk_str).exists()):
                ohsubscription = Subscription.objects.get(pk=ohsubscription_pk_str)
                subscription_field(ohsubscription, 'naicslevel5', NaicsLevel5.objects.get(pk=data.get('naicslevel5opt').naic_level_5_code))
                print('ohsubscription.save()')
                ohsubscription.save()

        person_pk_str = request.session.get('account_person', None)
        if person_pk_str:
            person = Person.objects.get(pk=person_pk_str)
            if person:
                if (PersonLanguage.objects.filter(prsn_id=person.prsn_id).exists()):
                    PersonLanguage.objects.filter(prsn_id=person.prsn_id).all().delete()

                personlanguagechecklist = list(data.get('personlanguagechecklist'))
                print('personlanguagechecklist :', len(personlanguagechecklist))
                if len(personlanguagechecklist) > 1:
                    for language in personlanguagechecklist:
                        print("personlanguagechecklist : language.lang_code ", language.lang_code)
                        adapter = get_adapter(request)
                        if (PersonLanguage.objects.filter(prsn_id=person.prsn_id,
                                                           lang_code=language.lang_code).exists()):
                            personlanguage = PersonLanguage.objects.get(prsn_id=person.prsn_id,
                                                                          lang_code=language.lang_code)
                            person_language_field(personlanguage, 'lang_code',
                                                   Language.objects.get(pk=language.lang_code))
                            person_language_field(personlanguage, 'prsn_id', person.prsn_id)
                            if commit:
                                print('personlanguage.update()')
                                personlanguage.update()
                        else:
                            personlanguage = adapter.new_person_language(request)
                            person_language_field(personlanguage, 'lang_code',
                                                  Language.objects.get(pk=language.lang_code))
                            person_language_field(personlanguage, 'prsn_id', person.prsn_id)
                            if commit:
                                print('personlanguage.save()')
                                personlanguage.save()

        person_role_company_str = request.session.get('company_person_role', None)
        if person_role_company_str:
            print('person_role_company_str',person_role_company_str)
            if(CompanyPersonRole.objects.filter(pk=person_role_company_str).exists()):
                companypersonrole = CompanyPersonRole.objects.get(pk=person_role_company_str)
                if companypersonrole and data.get('personroles'):
                    personrole = data.get('personroles')
                    company_person_role_field(companypersonrole, 'crol_code', CompanyRole.objects.get(pk=personrole))
                    if commit:
                        print('companypersonrole.save()',companypersonrole)
                        companypersonrole.save()
                ohsubscriptiondetail_pk_str = request.session.get('ohaccount_subscriptiondetail', None)
                print('ohsubscriptiondetail_pk_str and companypersonrole', ohsubscriptiondetail_pk_str,companypersonrole)
                if (ohsubscriptiondetail_pk_str and companypersonrole):
                    if (SubscriptionDetail.objects.filter(pk=ohsubscriptiondetail_pk_str).exists()):
                        ohsubscriptiondetail = SubscriptionDetail.objects.get(pk=ohsubscriptiondetail_pk_str)
                        subscriptiondetail_field(ohsubscriptiondetail, 'cprs_id',companypersonrole)

                        ohsubscriptiondetail.save()
                        print('User_Adapter_ohsubscriptiondetail.save()')

        username = data.get('username')
        print('username = data.get(username)', username)
        if username:
            user_username(user, username)

        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        if(form == 'onhand.subscription.forms.SignupForm'):
            user_field(user, 'role_code', Role.objects.get(pk=app_settings.DEFAULT_USER_ENROLMENT_ROLE))

        print('user_field(user, cprs_id, companypersonrole)',int(companypersonrole.pk))
        user_field(user, 'cprs_id', companypersonrole)

        self.populate_username(request, user)

        if commit:
            user.save()
        return user


    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from .utils import user_username,user_field
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username( user, username )

    def respond_user_inactive(self, request, user):
        return HttpResponseRedirect(
            reverse('account_inactive'))


    def login(self, request, user):
        # HACK: This is not nice. The proper Django way is to use an
        # authentication backend
        if not hasattr(user, 'backend'):
            from .auth_backends import AuthenticationBackend
            backends = get_backends()
            for backend in backends:
                if isinstance(backend, AuthenticationBackend):
                    # prefer our own backend
                    break
            else:
                # Pick one
                backend = backends[0]
            backend_path = '.'.join([backend.__module__,
                                     backend.__class__.__name__])
            user.backend = backend_path
        django_login(request, user)

    def logout(self, request):
        django_logout(request)

    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.  Note
        that URLs passed explicitly (e.g. by passing along a `next`
        GET parameter) take precedence over the value returned here.
        """
        assert request.user.is_authenticated()
        url = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if url:
            warnings.warn("LOGIN_REDIRECT_URLNAME is deprecated, simply"
                          " use LOGIN_REDIRECT_URL with a URL name",
                          DeprecationWarning)
        else:
            url = settings.LOGIN_REDIRECT_URL
        return resolve_url(url)


    def get_logout_redirect_url(self, request):
        """
        Returns the URL to redirect to after the user logs out. Note that
        this method is also invoked if you attempt to log out while no users
        is logged in. Therefore, request.user is not guaranteed to be an
        authenticated user.
        """
        return resolve_url(app_settings.LOGOUT_REDIRECT_URL)


    def _get_login_attempts_cache_key(self, request, **credentials):
        site = get_current_site(request)
        login = credentials.get('email', credentials.get('username', ''))
        login_key = hashlib.sha256(login.encode('utf8')).hexdigest()
        return 'allauth/login_attempts@{site_id}:{login}'.format(
            site_id=site.pk,
            login=login_key)

    def pre_authenticate(self, request, **credentials):
        if app_settings.LOGIN_ATTEMPTS_LIMIT:
            cache_key = self._get_login_attempts_cache_key(
                request, **credentials)
            login_data = cache.get(cache_key, None)
            if login_data:
                dt = timezone.now()
                current_attempt_time = time.mktime(dt.timetuple())
                if (len(login_data) >= app_settings.LOGIN_ATTEMPTS_LIMIT and
                        current_attempt_time < (
                            login_data[-1] +
                            app_settings.LOGIN_ATTEMPTS_TIMEOUT)):
                    raise forms.ValidationError(
                        self.error_messages['too_many_login_attempts'])

    def authenticate(self, request, **credentials):
        """Only authenticates, does not actually login. See `login`"""
        self.pre_authenticate(request, **credentials)
        user = authenticate(**credentials)
        if user:
            cache_key = self._get_login_attempts_cache_key(
                request, **credentials)
            cache.delete(cache_key)
        else:
            self.authentication_failed(request, **credentials)
        return user

    def authentication_failed(self, request, **credentials):
        cache_key = self._get_login_attempts_cache_key(request, **credentials)
        data = cache.get(cache_key, [])
        dt = timezone.now()
        data.append(time.mktime(dt.timetuple()))
        cache.set(cache_key, data, app_settings.LOGIN_ATTEMPTS_TIMEOUT)

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(
            reverse('account_email_verification_sent'))


def get_useradapter(request=None):
    path= 'onhand.users.adapter.AccountAdapter'
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return (ret)(request)
