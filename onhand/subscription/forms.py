from __future__ import absolute_import

import datetime
import warnings

from django import forms
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

from onhand.subscription.models import Person, Company, CompanyRole
from onhand.subscription.utils import  provider_create_account, person_field, ColumnCheckboxSelectMultiple, \
    url_str_to_company_pk, url_str_to_address_pk,  complete_signup_prelim_registration, set_form_field_order
# from onhand.users.adapter import get_useradapter
from onhand.users.utils import get_username_max_length, perform_login
from . import app_settings
from .adapter import get_adapter
from .validators import validate_all_city_choices
from .utils import person_pk_to_url_str,url_str_to_person_pk

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from onhand.products.models import ProductType,Product,ProductBasis,ProductDiscount,Discount
from onhand.management.models import Country,State,County,City, Zipcode, Language, NaicsLevel1, NaicsLevel2, NaicsLevel3, NaicsLevel4, NaicsLevel5, \
    Address

MONTHS = (
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'),
            (12, 'December')
        )

YEARS = (
            (2016, '2016'), (2017, '2017'), (2018, '2018'), (2019, '2019'), (2020, '2020'), (2021, '2021'),
            (2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'),
            (2028, '2028'), (2029, '2029'), (2030, '2030'), (2031, '2031'), (2032, '2032'), (2033, '2033'),
            (2034, '2034'), (2035, '2035'), (2036, '2036'), (2037, '2037'), (2038, '2038'), (2039, '2039'),
            (2040, '2040')
        )

SECURITY_QUESTIONS =(
    ('favorite_color', 'What is your favorite color?' ), ('favorite_movie', 'What is your favorite movie?'),
    ('favorite_sport', 'What is your favorite sport'), ('sports_hero', 'Who is your childhood sports hero?'),
    ('firstjob_town','Town name of your first job?'), ('childhood_nickname', 'What was your childhood nickname?'),
    ('year_fatherborn?', 'Which Year your father was born?'), ('nearest_sibling', 'In what city or town does your nearest sibling live?' )
)


def validate():
    print(print("****** Validation of Customer City choices------>*"))
    pass


class AjaxModelChoiceField(forms.ModelChoiceField):
    def __init__(self, model_class, *args, **kwargs):
        queryset = model_class.objects.none()
        super(AjaxModelChoiceField, self).__init__(queryset, *args, **kwargs)
        self.model_class = model_class

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            print("None check for City", key)
            value = self.model_class.objects.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            print(ValueError)
            value="Add City"
            return None
            # raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class AjaxModelNaicLevel2ChoiceField(forms.ModelChoiceField):
    def __init__(self, model_class, *args, **kwargs):
        queryset = model_class.objects.none()
        super(AjaxModelNaicLevel2ChoiceField, self).__init__(queryset, *args, **kwargs)
        self.model_class = model_class

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'naic_level_2_code'
            print("None check for City", key)
            value = self.model_class.objects.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            print(ValueError)
            return None
            # raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class AjaxModelNaicLevel3ChoiceField(forms.ModelChoiceField):
    def __init__(self, model_class, *args, **kwargs):
        print('1')
        # NaicsLevel2.objects.values_list('naic_level_2_code', 'naic_level_2_desc').all()
        queryset = model_class.objects.none()
        super(AjaxModelNaicLevel3ChoiceField, self).__init__(queryset, *args, **kwargs)
        self.model_class = model_class
        print(' self.model_class->', self.model_class)

    def to_python(self, value):
        print('2')
        print('NAICS LEVEL VALUE',value)
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'naic_level_3_code'
            print("None check for Level 3", self.to_field_name, self.model_class, key)
            value = self.model_class.objects.get(**{key: value})
            print('Value :self.model_class.objects.get(**{key: value}',value)
        except (ValueError, self.queryset.model.DoesNotExist):
            print(ValueError)
            value="teere"
            return None
            # raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class AjaxModelNaicLevelChoiceField(forms.ModelChoiceField):
    def __init__(self, model_class, *args, **kwargs):
        queryset = model_class.objects.none()
        super(AjaxModelNaicLevelChoiceField, self).__init__(queryset, *args, **kwargs)
        print(queryset)
        self.model_class = model_class

    def to_python(self, value):
        print('NAICS LEVEL VALUE',value)
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            print("None check for City", self.to_field_name)
            value = self.model_class.objects.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            print(ValueError)
            # value="Add City"
            return None
            # raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class LanguageChoicefield(forms.ModelMultipleChoiceField):
    def __init__(self, model_class, *args, **kwargs):
        queryset = model_class.objects.none
        print(queryset)
        super(LanguageChoicefield, self).__init__(queryset, *args, **kwargs)
        self.model_class = model_class

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            print("None check for Language", key)
            value = self.model_class.objects.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            print(ValueError)
            # value="Add City"
            return None
            # raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop('render_value',
                                  app_settings.PASSWORD_INPUT_RENDER_VALUE)
        kwargs['widget'] = forms.PasswordInput(render_value=render_value,
                                               attrs={'placeholder':
                                                      _(kwargs.get("label"))})
        super(PasswordField, self).__init__(*args, **kwargs)


class LoginForm(forms.Form):

    password = PasswordField(label=_("Password"))
    remember = forms.BooleanField(label=_("Remember Me"),
                                  required=False)

    user = None
    error_messages = {
        'account_inactive':
        _("This account is currently inactive."),

        'email_password_mismatch':
        _("The e-mail address and/or password you specified are not correct."),

        'username_password_mismatch':
        _("The username and/or password you specified are not correct."),

        'username_email_password_mismatch':
        _("The login and/or password you specified are not correct.")
    }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)
        login_widget = forms.TextInput(attrs={'placeholder':
                                                  _('Username'),
                                              'autofocus': 'autofocus'})
        login_field = forms.CharField(
            label=_("Username"),
            widget=login_widget,
            max_length=get_username_max_length())

        self.fields["login"] = login_field
        set_form_field_order(self,  ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields['remember']

    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        login = self.cleaned_data["login"]
        credentials["username"] = login
        credentials["password"] = self.cleaned_data["password"]
        return credentials

    def clean_login(self):
        login = self.cleaned_data['login']
        return login.strip()

    def clean(self):
        super(LoginForm, self).clean()
        if self._errors:
            return
        credentials = self.user_credentials()
        user = get_adapter(self.request).authenticate(
            self.request,
            **credentials)
        if user:
            self.user = user
        else:
            raise forms.ValidationError(
                self.error_messages[
                    '%s_password_mismatch'
                    % app_settings.AUTHENTICATION_METHOD])
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        ret = perform_login(request, self.user,
                            email_verification=app_settings.EMAIL_VERIFICATION,
                            redirect_url=redirect_url)
        print('class LoginForm(forms.Form) ---> def login')
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data['remember']
        if remember:
            request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            request.session.set_expiry(0)
        return ret

class RegistrationForm(forms.Form):

    # person = None

    error_messages = {
        'cc_error':
        _("Correct the information for the credit card."),

        'first_name_empty':
        _("The first name you specified is not correct.")
    }

    def __init__(self, *args, **kwargs):
        print("RegistrationForm__init__")
        self.request = kwargs.pop('request', None)
        super(RegistrationForm, self).__init__(*args, **kwargs)


    def clean(self):
        super(RegistrationForm, self).clean()
        return self.cleaned_data

def _base_register_form_class():
        return  RegistrationForm


class BaseRegisterForm(_base_register_form_class()):


    # options = (value for key, value in YEARS)
    #
    # list = forms.CharField(widget=forms.Textarea(attrs= {'selectBoxOptions': ';'.join(options)}),
    #                     label = _("ListExample"), required = False)


    hidden_field_sel_plan = forms.HiddenInput()

    onhandplans = Product.objects.filter(prdt_code='PLAN').order_by('prod_code')
    print('Provider_Forms, Queryset : onhandplans :',onhandplans )

    plan_choices = ProductBasis.objects.values_list('prdb_id', 'prod_code' ).filter(prdb_is_active='Y',prod_code__in=onhandplans.values('prod_code')).order_by('prod_code',
                                                                                                           'prdb_id')

    print('Provider_Forms, Queryset : plan_choices :', plan_choices)

    ohplanselect = forms.ChoiceField(widget=forms.RadioSelect, choices=plan_choices)

    print('Printing Radio select', ohplanselect.choices)

    discount = forms.CharField(label=_("Have a promotion code?"), required=False,
                                widget=forms.TextInput(
                                    attrs={'placeholder':
                                               _('Enter promotion code'),
                                           'class': "inp_card_info_discount_code"}))

    firstname = forms.CharField(label=_("First name"),required=True,
                               min_length=app_settings.FIRSTNAME_MIN_LENGTH,
                               error_messages={'required': "Last name is is mandatory."},
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('First name'),
                                          'autofocus': 'autofocus' ,'class':"inp_card_info_firstname"}))

    lastname = forms.CharField(label=_("Last name"),
                                min_length=app_settings.LASTNAME_MIN_LENGTH,
                                error_messages={'required':"Last name is mandatory."},
                                widget=forms.TextInput(
                                    attrs={'placeholder':
                                               _('Last name'),'class':"inp_card_info_lastname"}))

    email = forms.EmailField(label=_("Email"),error_messages={'required':"Email is  mandatory."},
                             widget=forms.TextInput(attrs={'type': 'email','placeholder': _('E-mail address'),'class':"inp_card_info_email"}))

    compname = forms.CharField(label=_("Business Name"),error_messages={'required':"Business name is mandatory."},
                               min_length=4,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                              _('Enter the name of your business'), 'class': "inp_card_info_business"}))

    addressline1 = forms.CharField(label=_("Address line 1"),error_messages={'required':"Address line 1 is mandatory."},
                               min_length=4,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                              _('Enter the street address'), 'class': "inp_card_info_addressline1"}))

    addressline2 = forms.CharField(label=_("Address line 2"),required=False,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                              _('Address line 2'),'class': "inp_card_info_addressline2"}))

    zipcode = forms.CharField(label=_("Zipcode"),required=True,
                                 error_messages={'required': 'Enter a US 5 digit ZIP Codes.',
                                                 'invalid': 'Enter a US 5 digit ZIP Codes.'},
                                 widget=forms.NumberInput(
                                     attrs={'placeholder':_('Enter zipcode first'),
                                            'autocomplete': 'off',
                                            'class': "inp_card_info_zip"}))

    BLANK_CHOICE = (('None', '---------'), ('add', 'Add city'))
    # city_choices = (
    #     (None, 'Select City'),
    # )
    # city_choices = BLANK_CHOICE + tuple(City.objects.values_list('city_id', 'name').filter())
    # city_choices = BLANK_CHOICE +tuple((o.city_id, str(o.name)) for o in City.objects.filter(zipc_code=zipcode))
    # print('******* City Choices*******')
    # print(city_choices)
    #
    # cityopt = forms.ModelChoiceField(queryset=City.objects.filter(zipc_code=zipcode),
    #                                  required=False, initial='None', disabled=False,
    #                                  widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))
    cityopt = AjaxModelChoiceField(City,required=False, initial='None', disabled=False,
                                     widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))

    city = forms.CharField(label=_("City"),required=False,error_messages={'required':"Valid city."},
                                   widget=forms.TextInput(
                                       attrs={'placeholder':
                                              _('city name'),'class': "inp_card_info_city"}))


    county = forms.CharField(label=_("County"), required=False, disabled=False,
                           widget=forms.TextInput(
                               attrs={'placeholder':
                                          _('county name'), 'class': "inp_card_info_county"}))
    state = forms.CharField(label=_("State"), required=False, disabled=False,
                           widget=forms.TextInput(
                               attrs={'placeholder':
                                          _('state name'), 'class': "inp_card_info_state"}))


    cardnumber = forms.IntegerField(label=_("Card Number"), required=True,error_messages={'required':"Enter credit card details."},
                                    widget=forms.NumberInput(
                                     attrs={'placeholder':_(' Enter the credit card number'),
                                            'class': "inp_card_info"}))

    cardmonth = forms.ChoiceField(choices=MONTHS, required=True,initial=datetime.datetime.now().month,
                                  widget=forms.Select(
                                      attrs={'class': "inp_card_info_expire_month"})
                                  )

    cardyear = forms.ChoiceField(choices=YEARS, required=True,initial=datetime.datetime.now().year,
                                 widget=forms.Select(
                                     attrs={'class': "inp_card_info_expire_year"})
                                 )

    cardcvv = forms.IntegerField(label=_("CVV"), required=True,
                                 error_messages={'required': "CVV is mandatory."},
                                    widget=forms.NumberInput(
                                        attrs={'placeholder':
                                                   _(' CVV'),
                                               'class': "inp_card_info_cvv"}))


    # city = forms.CharField(label=_("City"), required=True,
    #                                widget=forms.Select(choices=City.objects.get('name').order_by('name')),
    #                                    attrs={'class': "inp_card_info_state"}))


    def __init__(self, *args, **kwargs):
        print("BaseRegisterForm")


            # print(tuple((o.city_id, str(o.name)) for o in City.objects.filter(zipc_code=self.clean_zipcode())))
        self.product = Product.objects.all()

        self.firstname_required = kwargs.pop('firstname_required',
                                            app_settings.FIRSTNAME_REQUIRED)

        self.lastname_required = kwargs.pop('lastname_required',
                                             app_settings.LASTNAME_REQUIRED)

        email_required = kwargs.pop('email_required',
                                    app_settings.EMAIL_REQUIRED)

        self.compname_required = kwargs.pop('compname_required', True)

        self.addressline1_required = kwargs.pop('addressline1_required', True)

        self.addressline2_required = kwargs.pop('addressline2_required', False)

        self.zipcode_required = kwargs.pop('zipcode_required', True)

        self.city_required = kwargs.pop('city_required', True)

        self.cardnumber_required = kwargs.pop('cardnumber_required', True)

        self.cardcvv_required = kwargs.pop('cardcvv_required', True)

        self.county_required = kwargs.pop('county_required', True)

        self.state_required = kwargs.pop('state_required', True)

        super(BaseRegisterForm, self).__init__(*args, **kwargs)

        # print(tuple((o.city_id, str(o.name)) for o in City.objects.filter(zipc_code=BaseRegisterForm.clean_zipcode(RegisterForm))))

    def clean_ohplanselect(self):
        print("RegisterForm Radio Button")
        value = self.cleaned_data["ohplanselect"]
        value = get_adapter().clean_ohplanselect(value)
        return value

    def clean_discount(self):
        print("RegisterForm CleN discount CCODE")
        value = self.cleaned_data["discount"]
        value = get_adapter().clean_discount(value)
        return value

    def clean_firstname(self):
        print("RegisterForm clean_firstname")
        value = self.cleaned_data["firstname"]
        value = get_adapter().clean_first_name(value)
        return value

    def clean_lastname(self):
        value = self.cleaned_data["lastname"]
        value = get_adapter().clean_last_name(value)
        return value

    def clean_email(self):
        value = self.cleaned_data['email']
        value = get_adapter().clean_email(value)
        return value

    def clean_compname(self):
        value = self.cleaned_data['compname']
        value = get_adapter().clean_compname(value)
        return value

    def clean_addressline1(self):
        value = self.cleaned_data['addressline1']
        value = get_adapter().clean_addressline1(value)
        return value

    def clean_addressline2(self):
        value = self.cleaned_data['addressline2']
        value = get_adapter().clean_addressline2(value)
        return value

    def clean_zipcode(self):
        value = self.cleaned_data['zipcode']
        value = get_adapter().clean_zipcode(value)
        # print(ValidationError.error_list[])
        return value

    def clean_cityopt(self):
        value = self.cleaned_data['cityopt']
        value = get_adapter().clean_cityopt(value)
        Form_Data_zipcode = self.cleaned_data.get('zipcode')
        updated_city_list = tuple(City.objects.values_list('city_id', 'name').filter(zipc_code=Form_Data_zipcode))
        print('RegistrationForm__init__def clean_cityopt ', value , updated_city_list)
        print('RegistrationForm__init__def clean_cityopt', self.has_error('cityopt'))
        print('RegistrationForm__init__def clean_cityopt', self.errors)
        return value

    def clean_city(self):
        # print(self)
        value = self.cleaned_data['city']

        Form_Data_zipcode =self.cleaned_data.get('zipcode')
        Form_Data_cityopt = self.cleaned_data.get('cityopt')
        Form_Data_city = value
        print("RegistrationForm__init__def clean_city :",Form_Data_cityopt)
        # print('*************** self.cleaned_data City opt ********* ', self.cleaned_data.get('cityopt'))
        try:
            if(Zipcode.objects.filter(zipc_code=Form_Data_zipcode).exists()):
                if(City.objects.filter(zipc_code=Form_Data_zipcode).exists() and Form_Data_cityopt != 'None'):
                    if Form_Data_cityopt is None:
                        print("New city add 1")
                        value = get_adapter().clean_city(value, True)
                    else:
                        print("New city add 2")
                        value = get_adapter().clean_city(value, False)
                else:
                    if (City.objects.filter(city_id=Form_Data_cityopt,zipc_code=Form_Data_zipcode).exists()
                        and Form_Data_city ==""):
                        print("New city add 3")
                        city = City.objects.get(zipc_code_id=Form_Data_zipcode).city_id.__str__()
            else:
                print("New city add 4")
                value = get_adapter().clean_city(value, False)
        except KeyError:
            print("New city add 5")
            value = get_adapter().clean_city(value, False)

        return value

    def clean_county(self):
        value = self.cleaned_data['county']
        value = get_adapter().clean_county(value)
        print('cleaned_data --> County value :',value)
        return value

    def clean_state(self):
        value = self.cleaned_data['state']
        print('cleaned_data --> State value :', value)
        value = get_adapter().clean_state(value)
        return value

    def clean_cardnumber(self):
        value = self.cleaned_data['cardnumber']
        value = get_adapter().clean_cardnumber(value)
        return value

    def clean_cardcvv(self):
        value = self.cleaned_data['cardcvv']
        value = get_adapter().clean_cardcvv(value)
        return value


    def clean(self):
        print("2:BaseRegisterForm clean")
        cleaned_data = super(BaseRegisterForm, self).clean()
        return cleaned_data


class RegisterForm(BaseRegisterForm):

    def __init__(self, *args, **kwargs):
        # self.plan = Product.objects.all()
        print("RegisterForm")
        super(RegisterForm, self).__init__(*args, **kwargs)


    def clean(self):

        print("1:RegisterForm clean")
        super(RegisterForm, self).clean()
        return self.cleaned_data

    def save(self, request, redirect_url=None):

        print("RegisterForm save")
        adapter = get_adapter(request)
        print(adapter)

        """
        Create seperate address for each Person and Company;
        Reason: Address can be changed for each instances
        """
        address = adapter.new_address(request)
        address = adapter.save_address(request, address, self)
        person = adapter.new_person(request)
        adapter.save_person(request, person,address, self)

        """
        Create seperate address for each Person and Company;
        Reason: Address can be changed for each instances
        """

        address = adapter.new_address(request)
        address = adapter.save_address(request, address, self)
        company = adapter.new_company(request)
        print(' adapter.new_company(request)',company)
        adapter.save_company(request, company, address, self)

        """
        Create OH Subscription
        """
        subscription = adapter.new_subscription(request)
        subscription_kwargs = {}
        subscription_kwargs['company'] = company
        subscription_kwargs['salessource'] = app_settings.DEFAULT_SALES_SOURCE
        subscription_kwargs['naic_group_level'] = app_settings.DEFAULT_NAIC_GROUP_LEVEL
        subscription_kwargs['naic_level5_code'] = app_settings.DEFAULT_NAIC_LEVE5_CODE

        ohsubscription = adapter.save_subscription(request, subscription, self, **subscription_kwargs)
        print('adapter.stash_subscription(request, ohsubscription)', ohsubscription)

        if not ohsubscription is None:
            args= (ohsubscription, person, company, address)
            provider_subscription_api_id = provider_create_account(request, *args)

            print('provider_create_account called :', provider_subscription_api_id, person, company, address)
            ohsubscriptiondetail = adapter.new_subscriptiondetail(request)
            args = (ohsubscriptiondetail, provider_subscription_api_id, ohsubscription,company, self)
            ohsubscriptiondetail = adapter.save_subscriptiondetail(request, *args)
            print('Save Subscription details(request, ohsubscriptiondetail)', ohsubscriptiondetail)

        company_person_role = adapter.new_company_person_role(request)
        print('person_role_company :',company_person_role)
        adapter.save_company_person_role(request, company_person_role, company, person, self)

        ret = complete_signup_prelim_registration(request, person.pk, company.pk, address, ohsubscription, ohsubscriptiondetail, provider_subscription_api_id, company_person_role, signal_kwargs=None)
        return ret



class AccountInactiveForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()


    def __init__(self, *args, **kwargs):
        from .utils import person_field

        self.request = kwargs.pop('request', None)
        print('AccountInactiveForm__init__ :')
        # if 'person' in self.request.session:
        #     print( self.request.session['person'])
        #
        # print('self.request',self.request)
        # print(self.request.session)
        person_pk = None
        # person_pk_str = get_adapter(self.request).unstash_person(self.request)
        person_pk_str = self.request.session.get('account_person', None)
        # print('person_pk_str',person_pk_str)
        if person_pk_str:
            person_pk = url_str_to_person_pk(person_pk_str)

        # print('person_pk' , person_pk)
        person = Person.objects.get(prsn_id=person_pk_str)
        if person_pk :
            print('person_field(person_pk, first_name)', person_field(person, 'first_name'))
            firstname_model = person_field(person, 'first_name')
            lastname_model = person_field(person, 'last_name')
            kwargs.update(initial={
                # 'field': 'value'
                'firstname': firstname_model,
                'lastname': lastname_model
            })
        super(AccountInactiveForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(AccountInactiveForm, self).clean()
        return self.cleaned_data

class PasswordVerificationMixin(object):
    def clean(self):
        cleaned_data = super(PasswordVerificationMixin, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if (password1 and password2) and password1 != password2:
            self.add_error(
                'password2', _("You must type the same password each time.")
            )
        return cleaned_data

class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop('render_value',
                                  app_settings.PASSWORD_INPUT_RENDER_VALUE)
        kwargs['widget'] = forms.PasswordInput(render_value=render_value,
                                               attrs={'placeholder':
                                                      _(kwargs.get("label")),'class':"inp_steps_password"})
        super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):

    def __init__(self, *args, **kwargs):
        super(SetPasswordField, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        value = super(SetPasswordField, self).clean(value)
        value = get_adapter().clean_password(value, user=self.user)
        return value


class _DummyCustomSignupForm(forms.Form):

    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        need to check when invoked within the sales account or not
        """
        print('_DummyCustomSignupForm_signup')
        pass


def _base_signup_form_class():
    return _DummyCustomSignupForm


class BaseSignupForm(_base_signup_form_class()):

    compname = forms.CharField(label=_("Name"), required=True,
                                min_length=app_settings.FIRSTNAME_MIN_LENGTH,
                                error_messages={'required': "Company name is mandatory"},
                                widget=forms.TextInput(
                                    attrs={'placeholder':
                                               _('Enter your company name'),
                                            'class': "inp_steps_compname"}))


    compemail = forms.EmailField(label=_("Email"),required=False,
                             widget=forms.TextInput(attrs={'type': 'email', 'placeholder': _('E-mail address'),
                                                           'class': "inp_steps_email"}))

    website = forms.CharField(label=_("Website"), required=False,
                               min_length=4,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                              _('Website URL of your company'), 'class': "inp_steps_website",
                                          'autofocus': 'autofocus'}))

    phone = forms.CharField(label=_("Phone & Fax"), required=False,
                              widget=forms.NumberInput(
                                  attrs={'placeholder': _('Phone number'),
                                         'autocomplete': 'off',
                                         'class': "inp_steps_phone"}))

    fax = forms.CharField(label=_("Phone & Fax"), required=False,
                            widget=forms.NumberInput(
                                attrs={'placeholder': _('Fax number'),
                                       'autocomplete': 'off',
                                       'class': "inp_steps_fax"}))

    addressline1 = forms.CharField(label=_("Address line 1"),
                                   error_messages={'required': "Address line 1 is mandatory."},
                                   min_length=4,
                                   widget=forms.TextInput(
                                       attrs={'placeholder':
                                                  _('Enter the street address'),
                                              'class': "inp_steps_addressline1"}))


    addressline2 = forms.CharField(label=_("Address line 2"), required=False,
                                   widget=forms.TextInput(
                                       attrs={'placeholder':
                                                  _('Address line 2'), 'class': "inp_steps_addressline2"}))



    zipcode = forms.CharField(label=_("Zipcode & City"), required=True,
                              error_messages={'required': 'Enter a US 5 digit ZIP Codes.',
                                              'invalid': 'Enter a US 5 digit ZIP Codes.'},
                              widget=forms.NumberInput(
                                  attrs={'placeholder': _('Zipcode'),
                                         'autocomplete': 'off',
                                         'class': "inp_steps_zipcode"}))

    BLANK_CHOICE = (('None', '---------'), ('add', 'Add city'))

    cityopt = AjaxModelChoiceField(City, required=False, initial='None', disabled=False,
                                   widget=forms.Select(attrs={'class': "inp_steps_city_opt"}))

    city = forms.CharField(label=_("City"), required=False, error_messages={'required': "Valid city."},
                           widget=forms.TextInput(
                               attrs={'placeholder':
                                          _('city name'), 'class': "inp_steps_City"}))

    county = forms.CharField(label=_("County & State"), required=False, disabled=False,
                             widget=forms.TextInput(
                                 attrs={'placeholder':
                                            _('county name'), 'class': "inp_steps_county"}))
    state = forms.CharField(label=_("State"), required=False, disabled=False,
                            widget=forms.TextInput(
                                attrs={'placeholder':
                                           _('state name'), 'class': "inp_steps_State"}))

    # naicslevel1opt = AjaxModelNaicLevelChoiceField(NaicsLevel1,label='', required=True,
    #                                widget=forms.Select(attrs={'class': "step1_company_naics_dropdown"}))

    naicslevel1opt_choice = (('None', 'Select economic sector'),) + tuple(NaicsLevel1.objects.values_list('naic_level_1_code', 'naic_level_1_desc').all())
    naicslevel2opt_choice = (('None', ''),) + tuple(NaicsLevel2.objects.values_list('naic_level_2_code', 'naic_level_2_desc').all())



    naicslevel1opt = forms.ChoiceField(choices=naicslevel1opt_choice, required=False, initial='00', disabled=False,
                                   widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))

    naicslevel2opt = AjaxModelChoiceField(NaicsLevel2, required=False, initial='None', disabled=False,
                                   widget=forms.Select(attrs={'class': "step1_company_naics_dropdown"}))

    naicslevel3opt = AjaxModelChoiceField(NaicsLevel3, required=False, initial='None', disabled=False,
                                                    widget=forms.Select(
                                                        attrs={'class': "step1_company_naics_dropdown"}))

    naicslevel4opt = AjaxModelChoiceField(NaicsLevel4, required=False, initial='None', disabled=False,
                                                    widget=forms.Select(
                                                        attrs={'class': "step1_company_naics_dropdown"}))

    naicslevel5opt = AjaxModelChoiceField(NaicsLevel5, required=True, initial='None', disabled=False,error_messages={'required': "Business Classification required"},
                                                    widget=forms.Select(
                                                        attrs={'class': "step1_company_naics_dropdown"}))

    languagechecklist = forms.CheckboxSelectMultiple()

    personlanguagechecklist = forms.CheckboxSelectMultiple()

    personroles =  forms.ChoiceField(widget=forms.RadioSelect, choices=tuple(CompanyRole.objects.values_list('crol_code','crol_desc').all()),
                                    required=True,initial='employ',
                                    error_messages={'required': "Select your role in the company"}
                                    )
    # personroles = forms.ModelChoiceField(queryset=CompanyRole.objects.all(),
    #                                                     required=True,
    #                                                     error_messages={'required': "Select your role in the company"},
    #                                                     widget=forms.RadioSelect)


    username = forms.CharField(label=_("Username"),
                               min_length=app_settings.USERNAME_MIN_LENGTH,required=True,
                               error_messages={'required': "Please enter a valid username"},
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('Enter login username'),
                                          'autofocus': 'autofocus', 'class': "inp_steps_username"}))

    secquestion1 = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=False, initial='favorite_color',
                                 widget=forms.Select(attrs={'class': "inp_steps step2_user_login_questions_select"}))

    secanswer1 = forms.CharField(label=_("Answer1"),required=False,
                               widget=forms.TextInput(attrs={'placeholder':_('Security Answer 1'),
                                                             'class': "step2_user_login_answers_input"}))

    secquestion2 = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=False, initial="favorite_movie",
                                 widget=forms.Select(attrs={'class': "inp_steps step2_user_login_questions_select"}))

    secanswer2 = forms.CharField(label=_("Answer1"), required=False,
                                 widget=forms.TextInput(attrs={'placeholder': _('Security Answer 1'),
                                                               'class': "step2_user_login_answers_input"}))

    secquestion3 = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=False, initial='favorite_sport',
                                 widget=forms.Select(attrs={'class': "inp_steps step2_user_login_questions_select"}))

    secanswer3 = forms.CharField(label=_("Answer1"), required=False,
                                 widget=forms.TextInput(attrs={'placeholder': _('Security Answer 1'),
                                                               'class': "step2_user_login_answers_input"}))

    secquestion4 = forms.ChoiceField(choices=SECURITY_QUESTIONS, required=False, initial='sports_hero',
                                 widget=forms.Select(attrs={'class': "inp_steps step2_user_login_questions_select"}))

    secanswer4 = forms.CharField(label=_("Answer1"), required=False,
                                 widget=forms.TextInput(attrs={'placeholder': _('Security Answer 1'),
                                                               'class': "step2_user_login_answers_input"}))

    # email = forms.EmailField(widget=forms.TextInput(
    #     attrs={'type': 'email',
    #            'placeholder': _('E-mail address')}))

    def __init__(self,request, *args, **kwargs):
        from .utils import person_field, company_field, address_field
        # naicslevel1opt = kwargs.pop('naicslevel1opt', None)
        print('BaseSignupForm__init__ :')
        person_pk = None
        company_pk = None
        default_values = {}
        person = None
        company =None
        # self.fields['compname'].initial = 'pramod2'

        person_pk_str = request.session.get('account_person', None)
        company_pk_str = request.session.get('account_company', None)
        print('person_pk_str , company_pk_str :->',person_pk_str , company_pk_str)

        if person_pk_str:
            person_pk = url_str_to_person_pk(person_pk_str)
            print('person_pk :' , person_pk )
            person = Person.objects.get(prsn_id=person_pk_str)
            if person_pk:
                default_values['compemail'] = person_field(person, 'email')
                default_values['username'] = person_field(person, 'email')

        if company_pk_str:
            company_pk = url_str_to_company_pk(company_pk_str)
            print('company_pk :' , company_pk)
            company = Company.objects.get(comp_id=company_pk_str)

            if company_pk:
                default_values['compname'] = company_field(company, 'name')
                # print(company_field(company, 'address'))
                if company_field(company, 'address'):
                    # address_pk = url_str_to_address_pk(company_field(company, 'address'))
                    # print('address_pk :', address_pk.state)
                    address = Address.objects.get(addr_id=str(company_field(company, 'address')))
                    default_values['addressline1'] = address_field(address, 'address_line_1')
                    default_values['addressline2'] = address_field(address, 'address_line_2')
                    default_values['zipcode'] = address.city.zipc_code_id
                    default_values['city'] = address.city.name
                    default_values['cityopt'] = address.city.name
                    default_values['county'] = address.city.zipc_code.county.name
                    default_values['state'] = address.city.zipc_code.county.state.name

        print('default Values Signup form:',default_values)


        kwargs.update(initial=default_values)
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        # self.fields['compname'].initial = 'pramod4s'


        # self.fields['compname'].initial = 'pramod44'

        self.fields['languagechecklist'] = forms.ModelMultipleChoiceField(queryset=Language.objects.all(),
                                                                          initial={'eng': 'English'},error_messages={'required': "Select Languages spoken in the company"},
                                                                          widget=ColumnCheckboxSelectMultiple())

        self.fields['personlanguagechecklist'] = forms.ModelMultipleChoiceField(queryset=Language.objects.all(),
                                                                          initial={'eng': 'English'}, error_messages={'required': "Select Languages you speak"},
                                                                          widget=ColumnCheckboxSelectMultiple())

    def clean(self):
        print('\nBaseSignupForm self.changed_data',self.changed_data)
        # if not self.compname.changed_data:
        cleaned_data = super(BaseSignupForm, self).clean()
        # if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
        #     email = cleaned_data.get('email')
        #     email2 = cleaned_data.get('email2')
        #     if (email and email2) and email != email2:
        #         self.add_error(
        #             'email2', _("You must type the same email each time.")
        #         )
        return cleaned_data

    def clean_compname(self):
        # print('\nBaseSignupForm _clean_compname() ', self.compname.has_changed())
        value = self.cleaned_data['compname']
        value = get_adapter().clean_compname(value)
        print('class BaseSignupForm__init__ def clean_compname :', self.has_error('clean_compname'))
        return value

    def clean_compemail(self):
        value = self.cleaned_data['compemail']
        value = get_adapter().clean_email(value)
        return value

    def clean_website(self):
        value = self.cleaned_data['website']
        value = get_adapter().clean_website(value)
        return value

    def clean_phone(self):
        value = self.cleaned_data['phone']
        value = get_adapter().clean_phone(value)
        return value


    def clean_fax(self):
        value = self.cleaned_data['fax']
        value = get_adapter().clean_fax(value)
        return value


    def clean_addressline1(self):
        value = self.cleaned_data['addressline1']
        value = get_adapter().clean_addressline1(value)
        return value

    def clean_addressline2(self):
        value = self.cleaned_data['addressline2']
        value = get_adapter().clean_addressline2(value)
        return value

    def clean_zipcode(self):
        value = self.cleaned_data['zipcode']
        value = get_adapter().clean_zipcode(value)
        # print(ValidationError.error_list[])
        return value

    def clean_cityopt(self):

        value = self.cleaned_data['cityopt']
        value = get_adapter().clean_cityopt(value)

        Form_Data_zipcode = self.cleaned_data.get('zipcode')
        updated_city_list = tuple(City.objects.values_list('city_id', 'name').filter(zipc_code=Form_Data_zipcode))

        # print('*************** City opt ********* ', value, updated_city_list)
        print('class BaseSignupForm__init__ def clean_cityopt :', self.has_error('cityopt'))
        print('class BaseSignupForm__init__ def clean_cityopt :', self.errors)
        return value

    def clean_city(self):
        # print(self)
        value = self.cleaned_data['city']

        Form_Data_zipcode = self.cleaned_data.get('zipcode')
        Form_Data_cityopt = self.cleaned_data.get('cityopt')
        Form_Data_city = value
        # print("Form_Data_cityopt :", Form_Data_cityopt)
        # print('*************** self.cleaned_data City opt ********* ', self.cleaned_data.get('cityopt'))
        try:
            if (Zipcode.objects.filter(zipc_code=Form_Data_zipcode).exists()):
                if (City.objects.filter(zipc_code=Form_Data_zipcode).exists() and Form_Data_cityopt != 'None'):
                    if Form_Data_cityopt is None:
                        # print("New city add 1")
                        value = get_adapter().clean_city(value, True)
                    else:
                        # print("New city add 2")
                        value = get_adapter().clean_city(value, False)
                else:
                    if (City.objects.filter(city_id=Form_Data_cityopt, zipc_code=Form_Data_zipcode).exists()
                        and Form_Data_city == ""):
                        # print("New city add 3")
                        city = City.objects.get(zipc_code_id=Form_Data_zipcode).city_id.__str__()
            else:
                # print("New city add 4")
                value = get_adapter().clean_city(value, False)
        except KeyError:
            # print("New city add 5")
            value = get_adapter().clean_city(value, False)

        return value

    def clean_county(self):
        value = self.cleaned_data['county']
        value = get_adapter().clean_county(value)
        print('cleaned_data --> County value :', value)
        return value

    def clean_state(self):
        value = self.cleaned_data['state']
        print('cleaned_data --> State value :', value)
        value = get_adapter().clean_state(value)
        return value

    def clean_naicslevel1opt(self):
        value = self.cleaned_data['naicslevel1opt']
        print('cleaned_data --> naicslevel1opt value :', value)
        value = get_adapter().clean_naicslevel1opt(value)
        return value

    def clean_naicslevel2opt(self):
        value = self.cleaned_data['naicslevel2opt']
        value = get_adapter().clean_naicslevel2opt(value)
        Form_Data_naicslevel1code = self.cleaned_data.get('naicslevel1opt')

        print('cleaned_data --> naicslevel2opt value :', Form_Data_naicslevel1code)

        updated_naicslevel2opt_list = tuple(NaicsLevel2.objects.values_list('naic_level_2_code', 'naic_level_2_desc').filter(naic_level_1_code=Form_Data_naicslevel1code))
        self.fields['naicslevel2opt'].queryset = NaicsLevel2.objects.filter(naic_level_1_code=Form_Data_naicslevel1code)
        # print('***updated_naicslevel2opt_list**** ', value, updated_naicslevel2opt_list)
        # print('Error messages......', self.errors)

        return value

    def clean_naicslevel3opt(self):
        value = self.cleaned_data['naicslevel3opt']
        value = get_adapter().clean_naicslevel3opt(value)
        Form_Data_naicslevel2code = self.cleaned_data.get('naicslevel2opt')
        self.fields['naicslevel3opt'].queryset = NaicsLevel3.objects.filter(naic_level_2_code=Form_Data_naicslevel2code)
        return value

    def clean_naicslevel4opt(self):
        value = self.cleaned_data['naicslevel4opt']
        value = get_adapter().clean_naicslevel4opt(value)
        Form_Data_naicslevel3code = self.cleaned_data.get('naicslevel3opt')
        self.fields['naicslevel4opt'].queryset = NaicsLevel4.objects.filter(naic_level_3_code=Form_Data_naicslevel3code)
        return value

    def clean_naicslevel5opt(self):
        value = self.cleaned_data['naicslevel5opt']
        value = get_adapter().clean_naicslevel5opt(value)
        Form_Data_naicslevel4code = self.cleaned_data.get('naicslevel4opt')
        self.fields['naicslevel5opt'].queryset = NaicsLevel5.objects.filter(naic_level_4_code=Form_Data_naicslevel4code)
        return value

    def clean_languagechecklist(self):
        value = self.cleaned_data["languagechecklist"]
        value = get_adapter().clean_languagechecklist(value)
        return value

    def clean_personlanguagechecklist(self):
        value = self.cleaned_data["personlanguagechecklist"]
        value = get_adapter().clean_personlanguagechecklist(value)
        return value


    def clean_personroles(self):
        value = self.cleaned_data["personroles"]
        value = get_adapter().clean_personroles(value)
        return value

    def clean_username(self):
        value = self.cleaned_data["username"]
        value = get_adapter().clean_username(value)
        return value

    # def clean_email(self):
    #     value = self.cleaned_data['email']
    #     value = get_adapter().clean_email(value)
    #     if value and app_settings.UNIQUE_EMAIL:
    #         value = self.validate_unique_email(value)
    #     return value

    def clean_secquestion1(self):
        value = self.cleaned_data["secquestion1"]
        value = get_adapter().clean_secquestion1(value)
        return value

    def clean_secanswer1(self):
        value = self.cleaned_data["secanswer1"]
        value = get_adapter().clean_secanswer1(value)
        return value

    def clean_secquestion2(self):
        value = self.cleaned_data["secquestion2"]
        value = get_adapter().clean_secquestion2(value)
        return value

    def clean_secanswer2(self):
        value = self.cleaned_data["secanswer2"]
        value = get_adapter().clean_secanswer2(value)
        return value

    def clean_secquestion3(self):
        value = self.cleaned_data["secquestion3"]
        value = get_adapter().clean_secquestion3(value)
        return value

    def clean_secanswer3(self):
        value = self.cleaned_data["secanswer3"]
        value = get_adapter().clean_secanswer3(value)
        return value

    def clean_secquestion4(self):
        value = self.cleaned_data["secquestion4"]
        value = get_adapter().clean_secquestion4(value)
        return value

    def clean_secanswer4(self):
        value = self.cleaned_data["secanswer4"]
        value = get_adapter().clean_secanswer4(value)
        return value

    def validate_unique_email(self, value):
        return get_adapter().validate_unique_email(value)



    def custom_signup(self, request, user):
        custom_form = super(BaseSignupForm, self)
        if hasattr(custom_form, 'signup') and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
            # Historically, it was called .save, but this is confusing
            # in case of ModelForm
            custom_form.save(user)

class SignupForm(BaseSignupForm):

    password1 = PasswordField(label=_("Password"),error_messages={'required': "Please enter password"})
    password2 = PasswordField(label=_("Password (again)"),error_messages={'required': "Please enter password"})

    def get_initial(self):
        initial = super(SignupForm, self).get_initial()
        print('class SignupForm(BaseSignupForm) def get_initial called :',initial)

        self.initial['compname'] = 'papau'
        return initial

    def __init__(self, *args, **kwargs):
        print("SignupForm__init__:")
        # self.fields['compname'].initial = 'pramod3'
        # print('kwargs.pop(person, None) : ', kwargs)
        # for key, value in kwargs.iteritems():
        #     print("%s = %s" % (key, value))
        # # print('SignupForm_self.request :',self.request)
        # person_pk_str = self.request.session.get('account_person', None)
        # company_pk_str = self.request.session.get('account_company', None)
        # print('person_pk_str , company_pk_str :->', person_pk_str, company_pk_str)
        super(SignupForm, self).__init__(*args, **kwargs)

        # self.fields['compname'].initial = 'pramod4'
        # self.initial['compname'] = 'papau'
        print('SignupForm_app_settings->',app_settings)
        print('app_settings.SIGNUP_PASSWORD_ENTER_TWICE',app_settings.SIGNUP_PASSWORD_ENTER_TWICE)
        print('app_settings.TEMPLATE_EXTENSION', app_settings.TEMPLATE_EXTENSION)
        if not app_settings.SIGNUP_PASSWORD_ENTER_TWICE:
            del self.fields["password2"]

    def clean(self):
        print('\nSignupForm self.changed_data\n', self.changed_data)
        # if not self.compname.changed_data:
        super(SignupForm, self).clean()

        # `password` cannot by of type `SetPasswordField`, as we don't
        # have a `User` yet. So, let's populate a dummy user to be used
        # for password validaton.
        # dummy_user = get_user_model()
        # user_username(dummy_user, self.cleaned_data.get("username"))
        # user_email(dummy_user, self.cleaned_data.get("email"))
        # password = self.cleaned_data.get('password1')
        # if password:
        #     try:
        #         get_adapter().clean_password(
        #             password,
        #             user=dummy_user)
        #     except forms.ValidationError as e:
        #         self.add_error('password1', e)

        if app_settings.SIGNUP_PASSWORD_ENTER_TWICE \
                and "password1" in self.cleaned_data \
                and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] \
                    != self.cleaned_data["password2"]:
                self.add_error(
                    'password2',
                    _("You must type the same password each time"))
        return self.cleaned_data

    def save(self, request, redirect_url=None):

        print('forms_SignupForm_save')
        from onhand.users.adapter import get_useradapter
        adapter = get_useradapter(request)

        user = adapter.new_user(request)
        adapter.save_user(request, user, self)

        # self.custom_signup(request, user)
        # # to do : Move into adapter `save_user` ?
        # # setup_user_email(request, user, [])
        return user


class BaseSignupServiceForm(forms.Form):



    def __init__(self,request, *args, **kwargs):
        print('BaseSignupServiceForm__init__ :')
        default_values = {}
        person = None
        company =None
        print('request.session.get(complianceselect, None)',request.session.get('complianceselect', None))
        person_pk_str = request.session.get('account_person', None)
        company_pk_str = request.session.get('account_company', None)
        print('person_pk_str , company_pk_str :->',person_pk_str , company_pk_str)

        if person_pk_str:
            person_pk = url_str_to_person_pk(person_pk_str)
            print('person_pk :' , person_pk )
            person = Person.objects.get(prsn_id=person_pk_str)
            if person_pk:
                default_values['compemail'] = person_field(person, 'email')
                default_values['username'] = person_field(person, 'email')

        if company_pk_str:
            company_pk = url_str_to_company_pk(company_pk_str)
            print('company_pk :' , company_pk)
            company = Company.objects.get(comp_id=company_pk_str)
        print('default Values Signup form:',default_values)

        kwargs.update(initial=default_values)
        super(BaseSignupServiceForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('\nBaseSignupServiceForm self.changed_data',self.changed_data)
        cleaned_data = super(BaseSignupServiceForm, self).clean()
        return cleaned_data


    def custom_signup(self, request, user):
        custom_form = super(BaseSignupServiceForm, self)
        if hasattr(custom_form, 'signup') and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
            # Historically, it was called .save, but this is confusing
            # in case of ModelForm
            custom_form.save(user)

class SignupServiceForm(BaseSignupServiceForm):
    def __init__(self,request, *args, **kwargs):
        from .utils import person_field, company_field, address_field
        print('BaseSignupServiceForm__init__ :')
        print('request.session.get(complianceselect, None)', request.session.get('compliancedropdown1', None))
        person_pk = None
        company_pk = None
        default_values = {}
        person = None
        company =None

        person_pk_str = request.session.get('account_person', None)
        company_pk_str = request.session.get('account_company', None)
        print('person_pk_str , company_pk_str :->',person_pk_str , company_pk_str)

        if person_pk_str:
            person_pk = url_str_to_person_pk(person_pk_str)
            print('person_pk :' , person_pk )
            person = Person.objects.get(prsn_id=person_pk_str)
            if person_pk:
                default_values['compemail'] = person_field(person, 'email')
                default_values['username'] = person_field(person, 'email')

        if company_pk_str:
            company_pk = url_str_to_company_pk(company_pk_str)
            print('company_pk :' , company_pk)
            company = Company.objects.get(comp_id=company_pk_str)

        print('default Values Signup form:',default_values)

        kwargs.update(initial=default_values)
        super(BaseSignupServiceForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('\nBaseSignupServiceForm self.changed_data',self.changed_data)
        cleaned_data = super(BaseSignupServiceForm, self).clean()
        return cleaned_data

    def save(self, request):
        print('forms_SignupServiceForm_save')
        # from onhand.users.adapter import get_useradapter
        from onhand.users.models import User
        # adapter = get_useradapter(request)
        # user = adapter.new_user(request)
        # adapter.save_user(request, user, self)
        user_pk_str = request.session.get('account_user', None)
        user = User.objects.get(pk=user_pk_str)

        return user


