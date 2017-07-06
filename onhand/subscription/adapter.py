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
    get_subscriptiondetail_model
from django.utils.translation import ugettext_lazy as _

from onhand.subscription.compat import importlib
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text



class DefaultAccountAdapter(object):

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

    name_regex =  re.compile(r'^[a-zA-Z0-9_\s]*$')
    address_regex = re.compile(r'^[A-Za-z0-9_\.\-\s\,]*$')
    Credit_Card_Numbers_regex = re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|(?:5[1-5][0-9]{2}|2720|27[01][0-9]|2[3-6][0-9]{2}|22[3-9][0-9]|222[1-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35[0-9]{3})[0-9]{11})\b')
    Credit_Card_CVV_regex = re.compile(r'^([0-9]{3,4})$')
    username_regex = re.compile(r'^[\w.@+-]+$')
    error_messages = {

    }

    # name_regex = re.compile(r'^[\w.@+-]+$')
    error_messages = {
        'invalid_username':
            _('Usernames can only contain letters, digits and @/./+/-/_.'),
        'username_blacklisted':
            _('Username can not be used. Please use other username.'),
        'username_taken':
            AbstractUser._meta.get_field('username').error_messages['unique'],
        'too_many_login_attempts':
            _('Too many failed login attempts. Try again later.'),
        'email_taken':
            _("A user is already registered with this e-mail address."),
        'ohplanselect_invalid':('Selected Onhand Plan  unavailable at the moment'),
        'discount_invalid':
            _('Promotion code not valid'),
        'firstname_required':
            _('First name is mandatory.'),
        'firstname_invalid':
        _('Enter a valid First name.'),
        'lastname_required':
            _('Last name is mandatory.'),
        'lastname_invalid':
            _('Enter a valid Last name.'),
        'compname_required':
            _('Business name is mandatory.'),
        'compname_invalid':
            _('Enter a valid Business name.'),
        'email_required':
            _('Email is mandatory.'),
        'addressline1_required':
            _('Business name is mandatory.'),
        'addressline1_invalid':
            _('Enter a valid street address.'),
        'zipcode_required':
            _('Zipcode is mandatory.'),
        'zipcode_unavailable':
            _('Zipcode unavailable'),
        'city_required':
            _('Enter a valid City name.'),
        'city_invalid':
            _('Enter a valid City name.'),
        'county_required':
            _('County name is mandatory.'),
        'county_invalid':
            _('Enter a valid County name.'),
        'state_required':
            _('State name is mandatory.'),
        'state_invalid':
            _('Enter a valid State name.'),
        'cardnumber_required':
            _('Enter a valid Credit card number.'),
        'cardnumber_invalid':
            _('Enter a valid Credit card number.'),
        'cardcvv_required':
            _('CVV required.'),
        'cardcvv_invalid':
            _('Enter a valid CVV.'),

    }



    def get_person_search_fields(self):
        person = get_person_model()
        return filter(lambda a: a and hasattr(person, a),
                      ['first_name', 'last_name', 'email'])

    def __init__(self, request=None):
        self.request = request

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user


    def new_person(self, request):
        """
        Instantiates a new User instance.
        """
        person = get_person_model()()
        return person

    def new_subscription(self, request):
        """
        Instantiates a new User instance.
        """
        subscription = get_subscription_model()()
        return subscription


    def new_subscriptiondetail(self, request):
        """
        Instantiates a new User instance.
        """
        subscriptiondetail = get_subscriptiondetail_model()()
        return subscriptiondetail



    def new_company(self, request):
        """
        Instantiates a new User instance.
        """
        company  = get_company_model()()
        return company

    def new_company_person_role(self, request):
        """
        Instantiates a new person role in company instance.
        """
        company_person_role  = get_company_person_role_model()()
        return company_person_role

    def new_address(self, request):
        """
        Instantiates a new User instance.
        """
        address  = get_address_model()()
        return address

    def new_company_language(self, request):
        """
        Instantiates a new User instance.
        """
        company_language  = get_company_language_model()()
        return company_language

    def new_person_language(self, request):
        """
        Instantiates a new User instance.
        """
        person_language  = get_person_language_model()()
        return person_language

    def populate_person(self, request, person):
        """
        Fills in a valid username, if required and missing.  If the
        person is already present it is assumed to be valid
        (unique).
        """
        from .utils import person_field
        print('populate_person')
        print(person)
        first_name = person_field(person, 'first_name')
        last_name = person_field(person, 'last_name')
        email = person_field(person, 'email')

    def populate_company(self, request, company):
        from .utils import company_field
        compname = company_field(company, 'name')


    def populate_address(self, request, address):

        from .utils import address_field

        address_line_1 = address_field(address, 'address_line_1')
        address_line_2 = address_field(address, 'address_line_2')
        city = address_field(address, 'city_id')

    def populate_subscription(self, request, subscription):
        from .utils import subscription_field
        subscriptionid = subscription_field(subscription, 'subs_id')


    def set_first_name(self, person, first_name):
        person.set_first_name(first_name)
        person.save()

    def set_last_name(self, person, last_name):
        person.set_first_name(last_name)
        person.save()

    def set_email(self, person, email):
        person.set_first_name(email)
        person.save()

    def set_comp_name(self, company, compname):
        company.set_comp_name(compname)
        company.save()

    def set_address_line_1(self, address, addressline1):
        address.set_address_line_1(addressline1)
        address.save()

    def set_address_line_2(self, address, addressline2):
        address.set_address_line_2(addressline2)
        address.save()

    def set_city(self, address, city):
        address.set_city(city)
        address.save()


    def clean_ohplanselect(self, ohplanselect, shallow=False):
        print("1:Validating clean_ohplanselect",ohplanselect )


        try:
            if(ProductBasis.objects.filter(prdb_id=ohplanselect).exists()):
                return ohplanselect
            else:
                raise forms.ValidationError(
                self.error_messages['ohplanselect_invalid'])
        except:
            raise forms.ValidationError(
                self.error_messages['ohplanselect_invalid'])

        return ohplanselect


    def clean_discount(self, discount, shallow=False):
        print("1:Validating clean_discount")
        # plan = request.GET.get('plan', None)
        # plan = clean_ohplanselect()
        # print(plan)
        print(discount)
        # print(ProductDiscount.objects.filter(disc_code=discount_code).exists())
        # print(Discount.objects.get(disc_code=discount_code).disc_desc)
        if discount:
            try:
                if (Discount.objects.filter(disc_code=discount).exists()):
                    return discount
                else:
                    raise forms.ValidationError(
                        self.error_messages['discount_invalid'])
            except:
                raise forms.ValidationError(
                    self.error_messages['discount_invalid'])

        return discount


    def clean_first_name(self, first_name, shallow=False):
        print("1:Validating clean_first_name")
        if not first_name:
            raise forms.ValidationError(
                self.error_messages['firstname_required'])

        if not self.name_regex.match(first_name):
            raise forms.ValidationError(
                self.error_messages['firstname_invalid'])

        return first_name

    def clean_last_name(self, last_name, shallow=False):
        if not last_name:
            raise forms.ValidationError(
                self.error_messages['lastname_required'])

        if not self.name_regex.match(last_name):
            raise forms.ValidationError(
                self.error_messages['lastname_invalid'])

        return last_name

    def clean_email(self, email):
        return email

    def clean_compemail(self, compemail):
        return compemail

    def clean_website(self, website):
        return website

    def clean_phone(self, phone):
        return phone

    def clean_fax(self, fax):
        return fax

    def clean_compname(self, compname):
        if not compname:
            raise forms.ValidationError(
                self.error_messages['compname_required'])

        if not self.name_regex.match(compname):
            raise forms.ValidationError(
                self.error_messages['compname_invalid'])

        min_length = 4
        if min_length and len(compname) < min_length:
            raise forms.ValidationError(_("Company name must be a minimum of {0} "
                                          "characters.").format(min_length))
        # if not self.name_regex.match(compname):
        #     raise forms.ValidationError(
        #         self.error_messages['invalid_compname'])

        return compname

    def clean_addressline1(self, addressline1):
        if not addressline1:
            raise forms.ValidationError(
                self.error_messages['addressline1_required'])

        if not self.address_regex.match(addressline1):
            raise forms.ValidationError(
                self.error_messages['addressline1_invalid'])
        min_length = 4

        if min_length and len(addressline1) < min_length:
            raise forms.ValidationError(_("Fill in correct street address"))

        return addressline1

    def clean_addressline2(self, addressline2):
        if not self.address_regex.match(addressline2):
            raise forms.ValidationError(
                self.error_messages['addressline2_invalid'])
        return addressline2

    def clean_zipcode(self, zipcode):
        if not zipcode:
            raise forms.ValidationError(
                self.error_messages['zipcode_required'])
        min_length = 5
        if min_length and len(zipcode.__str__()) < min_length:
            raise forms.ValidationError(_("Enter a US {0} digit ZIP Codes ").format(min_length))

        try:
            if(Zipcode.objects.filter(zipc_code=zipcode).exists()):
                pass
            else:
                print('** Zipcode ValidationErrorRaised error after Model check')
                raise forms.ValidationError(
                    self.error_messages['zipcode_unavailable'])
        except KeyError:
            print('** Zipcode ValidationErrorRaised error after KeyError exception')
            raise forms.ValidationError(
                self.error_messages['zipcode_unavailable'])
        return zipcode

    def clean_cityopt(self, cityopt):
        print('** City dropdown check : ', cityopt)

        if(cityopt == 'None'):
            raise forms.ValidationError(
                self.error_messages['city_required'])
        else:
            if (cityopt == 'add'):
                pass
            else:
                try:
                    if (True):
                        # City.objects.filter(city_id=cityopt).exists()
                        pass
                    else:
                        raise forms.ValidationError(
                            self.error_messages['city_invalid'])
                except KeyError:
                    raise forms.ValidationError(
                        self.error_messages['city_invalid'])
        return cityopt

    def clean_city(self, city , check_user_city_value):
        print("** City user addeed textbox check required: %s  Value -> (%s)" % (check_user_city_value, city))
        if check_user_city_value:
            if not self.name_regex.match(city):
                raise forms.ValidationError(
                    self.error_messages['city_invalid'])
            if not city:
                raise forms.ValidationError(
                self.error_messages['city_invalid'])
        return city




    def clean_county(self, county):
        if not county:
            raise forms.ValidationError(
                self.error_messages['county_required'])

        if not self.name_regex.match(county):
            raise forms.ValidationError(
                self.error_messages['county_invalid'])

        try:
            if(County.objects.filter(name=county).exists()):
                pass
            else:
                print('** county ValidationErrorRaised error after Model check')
                raise forms.ValidationError(
                    self.error_messages['county_invalid'])
        except KeyError:
            print('** county ValidationErrorRaised error after KeyError exception')
            raise forms.ValidationError(
                self.error_messages['county_invalid'])
        return county

    def clean_state(self, state):
        if not state:
            raise forms.ValidationError(
                self.error_messages['state_required'])

        if not self.name_regex.match(state):
            raise forms.ValidationError(
                self.error_messages['state_invalid'])

        try:
            if(State.objects.filter(name=state).exists()):
                pass
            else:
                print('** county ValidationErrorRaised error after Model check')
                raise forms.ValidationError(
                    self.error_messages['state_invalid'])
        except KeyError:
            print('** Zipcode ValidationErrorRaised error after KeyError exception')
            raise forms.ValidationError(
                self.error_messages['state_invalid'])

        return state





    def clean_cardnumber(self, cardnumber):
        if not cardnumber:
            raise forms.ValidationError(
                self.error_messages['cardnumber_required'])
        print(cardnumber)
        if not self.Credit_Card_Numbers_regex.match(str(cardnumber)):
            raise forms.ValidationError(
                self.error_messages['cardnumber_invalid'])
        return cardnumber

    def clean_cardcvv(self, cardcvv):
        if not cardcvv:
            raise forms.ValidationError(
                self.error_messages['cardcvv_required'])

        if not self.Credit_Card_CVV_regex.match(str(cardcvv)):
            raise forms.ValidationError(
                self.error_messages['cardcvv_invalid'])
        return cardcvv

    def clean_naicslevel1opt(self,naicslevel1opt):
        return naicslevel1opt

    def clean_naicslevel2opt(self,naicslevel2opt):
        return naicslevel2opt


    def clean_naicslevel3opt(self,naicslevel3opt):
        return naicslevel3opt

    def clean_naicslevel4opt(self,naicslevel4opt):
        return naicslevel4opt

    def clean_naicslevel5opt(self,naicslevel5opt):
        return naicslevel5opt

    def clean_languagechecklist(self,languagechecklist):
        return languagechecklist

    def clean_personlanguagechecklist(self,personlanguagechecklist):
        return personlanguagechecklist

    def clean_personroles(self,personroles):
        return personroles

    def clean_username(self, username, shallow=False):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen.
        """
        if not self.username_regex.match(username):
            raise forms.ValidationError(
                self.error_messages['invalid_username'])

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(
                self.error_messages['username_blacklisted'])
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            username_field = app_settings.USER_MODEL_USERNAME_FIELD
            assert username_field
            user_model = get_user_model()
            try:
                query = {username_field + '__iexact': username}
                user_model.objects.get(**query)
            except user_model.DoesNotExist:
                return username
            error_message = user_model._meta.get_field(
                username_field).error_messages.get('unique')
            if not error_message:
                error_message = self.error_messages['username_taken']
            raise forms.ValidationError(error_message)
        return username

    def clean_password(self, password, user=None):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if min_length and len(password) < min_length:
            raise forms.ValidationError(_("Password must be a minimum of {0} "
                                          "characters.").format(min_length))
        validate_password(password, user)
        return password


    def clean_secquestion1(self,secquestion1):
        return secquestion1

    def clean_secanswer1(self,secanswer1):
        return secanswer1

    def clean_secquestion2(self,secquestion2):
        return secquestion2

    def clean_secanswer2(self,secanswer2):
        return secanswer2

    def clean_secquestion3(self,secquestion3):
        return secquestion3

    def clean_secanswer3(self,secanswer3):
        return secanswer3

    def clean_secquestion4(self,secquestion4):
        return secquestion4

    def clean_secanswer4(self,secanswer4):
        return secanswer4

    def save_address(self, request, address, form, commit=True):
        from .utils import address_field
        data = form.cleaned_data
        Form_Data_addressline1 = data.get('addressline1')
        Form_Data_addressline2 = data.get('addressline2')
        Form_Data_zipcode =   data.get('zipcode')
        Form_Data_cityopt = data.get('cityopt')
        Form_Data_city = data.get('city')
        city = None

        print("~~~~~~~~~~~~~~~~~~~~~~~" ,Form_Data_cityopt,  Form_Data_city )
        if(Zipcode.objects.filter(zipc_code=Form_Data_zipcode).exists()):
            if(City.objects.filter(zipc_code=Form_Data_zipcode).exists() and Form_Data_cityopt != 'None' and Form_Data_city):
                if(City.objects.filter(name=Form_Data_city,zipc_code=Form_Data_zipcode).exists()):
                    city = City.objects.get(name=Form_Data_city,zipc_code=Form_Data_zipcode).city_id.__str__()
                else:
                    city = City.objects.create(zipc_code= Zipcode.objects.get(zipc_code=Form_Data_zipcode) ,name=Form_Data_city,city_is_user_added='Y')
                print(city)
                city_id_str = city.__str__()
            else:
                # if (City.objects.filter(city_id=Form_Data_cityopt,zipc_code=Form_Data_zipcode).exists()
                #     and Form_Data_city ==""):
                print("******* ----->",Form_Data_cityopt.city_id.__str__())
                city_id_str = Form_Data_cityopt.city_id.__str__()
                city =  City.objects.get(city_id=city_id_str).city_id.__str__()


        if Form_Data_addressline1:
            address_field(address, 'address_line_1', Form_Data_addressline1)
        if Form_Data_addressline2:
            address_field(address, 'address_line_2', Form_Data_addressline2)
        if city:
            address_field(address, 'city_id', city_id_str)

        self.populate_address(request, address)
        print('populate_address')
        print(address.city)
        if commit:
            address.save()
        return address

    def save_person(self, request, person, address, form, commit=True):
        """
        Saves a new `person` instance using information provided in the
        regsitration form.
        """
        from .utils import person_field
        data = form.cleaned_data
        first_name = data.get('firstname')
        # print(data)
        last_name = data.get('lastname')
        email = data.get('email')
        #
        if first_name:
            person_field(person, 'first_name', first_name)
        if last_name:
            person_field(person, 'last_name', last_name)
        if email:
            person_field(person, 'email', email)
        print('address.city_id',  address.addr_id)
        print(address)
        if address.city_id:
            # address = Address.objects.get(addr_id=address.addr_id).addr_id.__str__()
            person_field(person, 'address',address)
        # person = Person

        self.populate_person(request, person)
        print('saving')
        print('commit : ', commit)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            # self.set_first_name(person,first_name)

            # person.first_name=first_name
            # print('printing fist name :-> ', person.first_name)
            person.save()
            print('saved perspneeee')
        return person

    def save_company(self, request, company, address, form, commit=True):
        from .utils import company_field
        data = form.cleaned_data
        compname = data.get('compname')

        if compname:
            company_field(company, 'name', compname)
        if address.addr_id:
            company_field(company, 'address', address)

        self.populate_company(request, company)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            print('Saving Company: Provider_Adapter_save_company', company)
            company.save()
        return company

    def save_vendor(self, company, vendorname, phone, email, commit=True):
        from .utils import company_field
        print('request, company, vendorname', company, vendorname)
        if vendorname:
            company_field(company, 'name', vendorname)
        if phone:
            company_field(company, 'phone', phone)
        if email:
            company_field(company, 'email', email)

        if commit:
            print('Saving Vendor: Provider_Adapter_save_vendor', company)
            company.save()
        return company


    def save_vendor_contact(self, person, firstname, lastname, phone, email, commit=True):
        from .utils import person_field
        print('person, firstname, lastname, phone, email', person, firstname, lastname, phone, email)
        if firstname:
            person_field(person, 'first_name', firstname)
        if lastname:
            person_field(person, 'last_name', lastname)
        if phone:
            person_field(person, 'office_phone', phone )
        if email:
            person_field(person, 'email', email)

        if commit:
            print('Saving Vendor contact: Provider_Adapter_save_vendor_contact', person)
            person.save()
        return person



    def save_company_vendorperson_role(self, person_role_company, company, person, commit=True):
        from .utils import company_field
        from onhand.subscription.utils import company_person_role_field
        # data = form.cleaned_data
        # compname = data.get('compname')

        # adapter = get_adapter()
        # person_role_company = adapter.new_person_role_company(request)
        print('New Vendor Company ID, Company',company )
        print('New Vendor Company Contact ID , Person', person)
        if company:
            company_person_role_field(person_role_company, 'comp_id', company)
            print('Saved comp_id')

        if person:
            company_person_role_field(person_role_company, 'prsn_id', person)
            print('Saved prsn_id')
        # if (form == 'onhand.subscription.forms.RegisterForm'):
        default_companyperson_role = 'EMPLOY'
        company_person_role_field(person_role_company, 'crol_code',
                                  CompanyRole.objects.get(pk=default_companyperson_role))
        print('Saved crol_code')

        if commit:
            person_role_company.save()
            print('Committing person_role_company:',person_role_company)
        return person_role_company

    def save_schedule_service(self, company, vendorname, phone, email, commit=True):
        from .utils import company_field
        print('request, company, vendorname', company, vendorname)
        if vendorname:
            company_field(company, 'name', vendorname)
        if phone:
            company_field(company, 'phone', phone)
        if email:
            company_field(company, 'email', email)

        if commit:
            print('Saving Vendor: Provider_Adapter_save_vendor', company)
            company.save()
        return company

    def save_company_person_role(self, request, person_role_company, company, person, form, commit=True):
        from .utils import company_field
        data = form.cleaned_data
        # compname = data.get('compname')

        # adapter = get_adapter()
        # person_role_company = adapter.new_person_role_company(request)
        print('save_company_person_role, Company',company.comp_id )
        print('person_role_company , Person', person.prsn_id)
        if company:
            from onhand.subscription.utils import company_person_role_field
            company_person_role_field(person_role_company, 'comp_id', company.comp_id)

        if person:
            company_person_role_field(person_role_company, 'prsn_id', person.prsn_id)

        print('form : save_company_person_role')
        # if (form == 'onhand.subscription.forms.RegisterForm'):
        default_companyperson_role = app_settings.DEFAULT_COMPANY_PERSON_ROLE
        if(CompanyRole.objects.filter(pk=default_companyperson_role).exists()):
            print('default_companyperson_role: ',CompanyRole.objects.get(pk=default_companyperson_role)._get_pk_val)
            company_person_role_field(person_role_company, 'crol_code', CompanyRole.objects.get(pk=default_companyperson_role))

        if commit:
            print('Committing person_role_company:',person_role_company)
            person_role_company.save()
            print('Committed person_role_company:')

        return person_role_company


    def save_subscription(self, request, subscription, form,  commit=True, **subscription_kwargs):
        from .utils import subscription_field
        data = form.cleaned_data
        company = subscription_kwargs.pop('company',None)
        salessource = subscription_kwargs.pop('salessource', 1)
        naic_group_level = subscription_kwargs.pop('naic_group_level', '2')
        naic_level_5_code = subscription_kwargs.pop('naic_level_5_code' , '000000')

        if not company is None:
            print('company.comp_id', company.comp_id)
            subscription_field(subscription, 'comp_id', int(company.comp_id))
            subscription_field(subscription, 'ssrc_id', int(salessource))
            subscription_field(subscription, 'subs_naic_group_level', naic_group_level)
            subscription_field(subscription, 'naic_level_5_code', NaicsLevel5.objects.get(naic_level_5_code=naic_level_5_code))

            if (request.POST.get('cardnumber', None) and request.POST.get("cardmonth", "") and request.POST.get(
                "cardyear", "")):
                expire_date = date.today()
                expire_date.replace(int(request.POST.get("cardyear", "")), int(request.POST.get("cardmonth", "")), 1)
                subscription_field(subscription, 'subs_cc_exp_date', expire_date)

            # if (request.POST.get('ohplanselect', None)):
            #     basis = ProductBasis.objects.get(prdb_id=request.POST.get('ohplanselect', None)).basi_code_id
            #     alert_date = datetime.now() + timedelta(days=Basis.objects.get(basi_code=basis).basi_days)
            #     subscription_field(subscription, 'subs_alert_date', alert_date)

            if commit:
                subscription.save()

        return subscription.subs_id

    def save_subscriptiondetail(self, request, ohsubscriptiondetail, provider_subscription_api_id, ohsubscription, company, form, commit=True):
        from .utils import subscriptiondetail_field, provider_get_subscriptiondetails_from_customer_profile, subscription_field
        subscription_validity_days =0
        data = form.cleaned_data
        subscription_keywords = {}
        plancode_form = data.get('ohplanselect')
        discount_code_form = data.get('discount')
        print('plancode_form = data.get(ohplanselect)', plancode_form)
        if not ohsubscription is None:
            subscription = Subscription.objects.get(pk=ohsubscription)
            if  provider_subscription_api_id != '':
                print('subscription_field_set_subs_apid_id',provider_subscription_api_id)
                print('Subscription.objects.get(pk=ohsubscription)',ohsubscription)
                subscription_field(subscription,'subs_api_id',int(provider_subscription_api_id))
                subscription_field(subscription, 'subs_api_payment_id', int(provider_get_subscriptiondetails_from_customer_profile(provider_subscription_api_id)))
                subscription.save()

            subscriptiondetail_field(ohsubscriptiondetail, 'subs_id', ohsubscription)

        productselected=ProductBasis.objects.get(prdb_id=plancode_form)
        if productselected != '':
            subscriptiondetail_field(ohsubscriptiondetail, 'prdb_id', productselected.prdb_id)

        if (request.POST.get('ohplanselect', None)):
            # basis = productselected.basi_code_id
            # subscription_validity_days = Basis.objects.get(basi_code=basis).basi_days
            subscription_end_date =  calculated_basis_date( productselected.basi_code, datetime.now())
            #TODO : Need to take request for Subscription start date
            subscriptiondetail_field(ohsubscriptiondetail, 'subd_start_date', datetime.now())
            subscriptiondetail_field(ohsubscriptiondetail, 'subd_end_date', subscription_end_date)
            subscriptiondetail_field(ohsubscriptiondetail, 'subd_date', datetime.now())

        subscriptiondetail_field(ohsubscriptiondetail, 'subd_list_price', productselected.prdb_list_price)

        discount = 0
        if(plancode_form != None and discount_code_form!= ''):
             if ProductDiscount.objects.filter(prdb_id=plancode_form,disc_code=discount_code_form).exists():
                 productdiscount = ProductDiscount.objects.get(prdb_id=plancode_form,disc_code=discount_code_form)
                 subscriptiondetail_field(ohsubscriptiondetail, 'pdis_id', productdiscount)
                 discount = Discount.objects.get(disc_code= productdiscount.disc_code).disc_percent / 100
                 discount = 0 if  discount <0  else discount

        subscriptiondetail_field(ohsubscriptiondetail, 'subd_discount', discount)
        netprice = productselected.prdb_list_price * (1 - discount)
        subscriptiondetail_field(ohsubscriptiondetail, 'subd_net_price', netprice)

        salestaxrate =0
        if Zipcode.objects.get(pk=int(request.POST.get('zipcode', None))).county.state.state_is_collect_sales_tax == 'Y':
            salestaxrate = Zipcode.objects.get(pk=int(request.POST.get('zipcode', None))).county.state.state_sales_tax_rate
        if salestaxrate != 0:
            subscriptiondetail_field(ohsubscriptiondetail, 'subd_sales_tax', netprice * (salestaxrate/100))

        # if (productselected.prod_code.prdt_code.prdt_is_fulfill_recurring == 'Y'):
        #     #Todo : Capture start date
        #     startdate = date.today()
        #     args = (netprice, subscription_validity_days, startdate, provider_subscription_api_id)
        #     if( netprice!= 0 and  subscription_validity_days !=0):
        #         CreatedSubscription = provider_create_subscriptiondetails_from_customer_profile(*args)
        #         if not CreatedSubscription:
        #             print('Automated Recurring Billing (ARB) Service:',CreatedSubscription)

        if commit:
            ohsubscriptiondetail.save()

        return ohsubscriptiondetail.subd_id


    def stash_user(self, request, user):
        request.session['account_user'] = user

    def unstash_user(self, request):
        return request.session.pop('account_user', None)

    def stash_person(self, request, person):
        request.session['account_person'] = person
        print('request.session[account_person] ----> ',request.session['account_person'])

    def unstash_person(self, request):
        print('request.session.pop(account_person, None) ----> ', request.session.get('account_person', None))
        return request.session.pop('account_person', None)


    def stash_company(self, request, company):
        print('stash_company :',company)
        request.session['account_company'] = company

    def unstash_company(self, request):
        return request.session.pop('account_company', None)

    def stash_subscription(self, request, subscription):
        request.session['ohaccount_subscription'] = subscription

    def unstash_subscription(self, request):
        return request.session.pop('ohaccount_subscription', None)

    def stash_subscriptiondetail(self, request, subscriptiondetail):
        request.session['ohaccount_subscriptiondetail'] = subscriptiondetail

    def unstash_subscriptiondetail(self, request):
        return request.session.pop('ohaccount_subscriptiondetail', None)

    def stash_providersubscription(self, request, subscription):
        request.session['provideraccount_subscription'] = subscription

    def unstash_providersubscription(self, request):
        return request.session.pop('provideraccount_subscription', None)

    def stash_company_person_role(self, request, company_person_role):
        request.session['company_person_role'] = company_person_role

    def unstash_company_person_role(self, request):
        return request.session.pop('company_person_role', None)


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


    def respond_person_registered(self, request):
        print('respond_person_registered Session', request.session)
        return HttpResponseRedirect(
            reverse('account_inactive'))

    def respond_person_unregistered(self, request):
        return HttpResponseRedirect(
            reverse('account_inactive'))

    def respond_user_registered(self, request):
        print('respond_person_registered Session', request.session)
        return HttpResponseRedirect(
            reverse('account_servicesignup'))

    def respond_user_unregistered(self, request):
        print('respond_person_registered Session', request.session)
        return HttpResponseRedirect(
            reverse('account_servicesignup'))


    def get_logout_redirect_url(self, request):
        """
        Returns the URL to redirect to after the user logs out. Note that
        this method is also invoked if you attempt to log out while no users
        is logged in. Therefore, request.user is not guaranteed to be an
        authenticated user.
        """
        try:
            from django.core import urlresolvers
            return urlresolvers.reverse(app_settings.LOGOUT_REDIRECT_URL)
        except urlresolvers.NoReverseMatch:
            # If this doesn't "feel" like a URL, re-raise.
            if '/' not in app_settings.LOGOUT_REDIRECT_URL and '.' not in app_settings.LOGOUT_REDIRECT_URL:
                raise
        return app_settings.LOGOUT_REDIRECT_URL

def get_adapter(request=None):
    path= 'onhand.subscription.adapter.DefaultAccountAdapter'
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return (ret)(request)
    # return ('allauth.account.adapter.DefaultAccountAdapter') (request)
    # return import_attribute('allauth.account.adapter.DefaultAccountAdapter')(request)
# return import_attribute(app_settings.ADAPTER)(request)
