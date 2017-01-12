from __future__ import absolute_import

import datetime
import warnings

from django import forms
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

from onhand.compliance.models import ComplianceServiceType, ServiceJurisdiction
from onhand.subscription.models import Person, Company, CompanyRole
from onhand.subscription.utils import  provider_create_account, person_field, ColumnCheckboxSelectMultiple, \
    url_str_to_company_pk, url_str_to_address_pk,  complete_signup_prelim_registration, set_form_field_order
# from onhand.users.adapter import get_useradapter
from onhand.users.utils import get_username_max_length, perform_login
from . import app_settings
from .adapter import get_adapter
# from .validators import validate_all_city_choices
# from .utils import person_pk_to_url_str,url_str_to_person_pk
from django.forms import TextInput, ModelForm, Textarea, Select
from suit.admin import SortableTabularInline, SortableModelAdmin, \
    SortableStackedInline
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, \
    EnclosedInput, LinkedSelect, AutosizedTextarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import TabHolder, Tab

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from onhand.products.models import ProductType,Product,ProductBasis,ProductDiscount,Discount
from onhand.management.models import Country,State,County,City, Zipcode, Language, NaicsLevel1, NaicsLevel2, NaicsLevel3, NaicsLevel4, NaicsLevel5, \
    Address, Basis

from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, \
    EnclosedInput, LinkedSelect, AutosizedTextarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, MultiField, Div
from bootstrap4_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import StrictButton, InlineField

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

class CommonLayout(Layout):
    username = forms.CharField(
        label = "username",
        max_length = 80,
        required = True,
    )
    lastname = forms.CharField(
        label="lastname",
        max_length=80,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(CommonLayout, self).__init__(
            MultiField(
                'username',
                'lastname',
            )
        )


class ExampleForm(forms.Form):
    complianceservice = forms.ModelChoiceField(queryset=ComplianceServiceType.objects.all(),
                                               required=False, initial='None', disabled=False,
                                               label='Compliance Service',
                                               widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))

    factorvalue = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))

    frequency = forms.ModelChoiceField(queryset=Basis.objects.all(),
                                       required=False, initial='None', disabled=False,
                                       label='Frequency',
                                       widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))
    # lastservicedate = forms.DateField(label='Last Service Date',
    #                                   widget=DateTimePicker(options={"format": "YYYY-MM-DD",
    #                                                                  "pickTime": False}))
    #
    # nextservicedate = forms.DateField(label='Next Service Date',
    #                                   widget=DateTimePicker(options={"format": "YYYY-MM-DD",
    #                                                                  "pickTime": False}))

    servicenote = forms.CharField(label="Compliance Service note",
                                  widget=forms.TextInput(attrs={"class": "form-control"}))

    todo = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))
    reminder = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False}))

    like_website = forms.TypedChoiceField(
        label="Do you like this website?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=True,
    )

    favorite_food = forms.CharField(
        label="What is your favorite food?",
        max_length=80,
        required=False,
    )

    favorite_number = forms.IntegerField(
        label="Favorite number",
        required=False,
    )

    notes = forms.CharField(
        label="Additional notes or feedback",
        required=False,
    )


    def __init__(self, *args, **kwargs):
        super(ExampleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        # self.helper.field_template = 'bootstrap3/layout/inline_field.html'

        self.helper.layout = Layout(
            # InlineField('like_website', readonly=True),
            # 'like_website',
            # CommonLayout,
            TabHolder(
                Tab(
                    'New Service',
                    'complianceservice'
                ),
                Tab(
                     'Service action',
                    'complianceservice',
                    'factorvalue',
                    'frequency',
                    # 'lastservicedate',
                    # 'nextservicedate',
                    'servicenote'
                )
            ),



            # StrictButton('Sign in', css_class='btn-default'),
        )
        self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        self.helper.add_input(Submit('submit', 'Submit'))


# class ComplianceRegistrationForm(forms.Form):
#
#     # person = None
#
#     error_messages = {
#         'cc_error':
#         _("Correct the information for the credit card."),
#
#         'first_name_empty':
#         _("The first name you specified is not correct.")
#     }
#
#     def __init__(self, *args, **kwargs):
#         print("RegistrationForm__init__")
#         self.request = kwargs.pop('request', None)
#         super(ComplianceRegistrationForm, self).__init__(*args, **kwargs)
#
#
#     def clean(self):
#         super(ComplianceRegistrationForm, self).clean()
#         return self.cleaned_data
#
# def _base_register_form_class():
#         return  RegistrationForm


class BaseComplianceRegisterForm(forms.Form):

    complianceservice = forms.ModelChoiceField(queryset=ServiceJurisdiction.objects.all(),
                                               required=False, initial='None', disabled=False,
                                               label='Compliance Service',
                                               widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))




    factorvalue = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))

    frequency = forms.ModelChoiceField(queryset=Basis.objects.all(),
                                               required=False, initial='None', disabled=False,
                                               label='Frequency',
                                               widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))
    lastservicedate = forms.DateField(label='Last Service Date',
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))

    nextservicedate = forms.DateField(label='Next Service Date',
                                      widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                                                     "pickTime": False}))

    servicenote = forms.CharField(label="Compliance Service note", widget=forms.TextInput(attrs={"class": "form-control"}))

    # reminder = forms.DateTimeField(
    #     required=False,
    #     widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
    #                                    "pickSeconds": False}))
    #
    # like_website = forms.TypedChoiceField(
    #     label="Do you like this website?",
    #     choices=((1, "Yes"), (0, "No")),
    #     coerce=lambda x: bool(int(x)),
    #     widget=forms.RadioSelect,
    #     initial='1',
    #     required=True,
    # )
    #
    # favorite_food = forms.CharField(
    #     label="What is your favorite food?",
    #     max_length=80,
    #     required=False,
    # )
    #
    # favorite_number = forms.IntegerField(
    #     label="Favorite number",
    #     required=False,
    # )
    #
    # notes = forms.CharField(
    #     label="Additional notes or feedback",
    #     required=False,
    # )

    # hidden_field_sel_plan = forms.HiddenInput()
    # onhandplans = Product.objects.filter(prdt_code='PLAN').order_by('prod_code')
    # print('Provider_Forms, Queryset : onhandplans :',onhandplans )
    #
    # plan_choices = ProductBasis.objects.values_list('prdb_id', 'prod_code' ).filter(prdb_is_active='Y',prod_code__in=onhandplans.values('prod_code')).order_by('prod_code',
    #                                                                                                        'prdb_id')
    #
    # print('Provider_Forms, Queryset : plan_choices :', plan_choices)
    #
    # ohplanselect = forms.ChoiceField(widget=forms.RadioSelect, choices=plan_choices)
    #
    # print('Printing Radio select', ohplanselect.choices)
    #
    # discount = forms.CharField(label=_("Have a promotion code?"), required=False,
    #                             widget=forms.TextInput(
    #                                 attrs={'placeholder':
    #                                            _('Enter promotion code'),
    #                                        'class': "inp_card_info_discount_code"}))
    #
    # firstname = forms.CharField(label=_("First name"),required=True,
    #                            min_length=app_settings.FIRSTNAME_MIN_LENGTH,
    #                            error_messages={'required': "Last name is is mandatory."},
    #                            widget=forms.TextInput(
    #                                attrs={'placeholder':
    #                                       _('First name'),
    #                                       'autofocus': 'autofocus' ,'class':"inp_card_info_firstname"}))
    #
    # lastname = forms.CharField(label=_("Last name"),
    #                             min_length=app_settings.LASTNAME_MIN_LENGTH,
    #                             error_messages={'required':"Last name is mandatory."},
    #                             widget=forms.TextInput(
    #                                 attrs={'placeholder':
    #                                            _('Last name'),'class':"inp_card_info_lastname"}))
    #
    # email = forms.EmailField(label=_("Email"),error_messages={'required':"Email is  mandatory."},
    #                          widget=forms.TextInput(attrs={'type': 'email','placeholder': _('E-mail address'),'class':"inp_card_info_email"}))
    #
    # compname = forms.CharField(label=_("Business Name"),error_messages={'required':"Business name is mandatory."},
    #                            min_length=4,
    #                            widget=forms.TextInput(
    #                                attrs={'placeholder':
    #                                           _('Enter the name of your business'), 'class': "inp_card_info_business"}))
    #
    # addressline1 = forms.CharField(label=_("Address line 1"),error_messages={'required':"Address line 1 is mandatory."},
    #                            min_length=4,
    #                            widget=forms.TextInput(
    #                                attrs={'placeholder':
    #                                           _('Enter the street address'), 'class': "inp_card_info_addressline1"}))
    #
    # addressline2 = forms.CharField(label=_("Address line 2"),required=False,
    #                            widget=forms.TextInput(
    #                                attrs={'placeholder':
    #                                           _('Address line 2'),'class': "inp_card_info_addressline2"}))
    #
    # zipcode = forms.CharField(label=_("Zipcode"),required=True,
    #                              error_messages={'required': 'Enter a US 5 digit ZIP Codes.',
    #                                              'invalid': 'Enter a US 5 digit ZIP Codes.'},
    #                              widget=forms.NumberInput(
    #                                  attrs={'placeholder':_('Enter zipcode first'),
    #                                         'autocomplete': 'off',
    #                                         'class': "inp_card_info_zip"}))
    #
    # BLANK_CHOICE = (('None', '---------'), ('add', 'Add city'))
    # # city_choices = (
    # #     (None, 'Select City'),
    # # )
    # # city_choices = BLANK_CHOICE + tuple(City.objects.values_list('city_id', 'name').filter())
    # # city_choices = BLANK_CHOICE +tuple((o.city_id, str(o.name)) for o in City.objects.filter(zipc_code=zipcode))
    # # print('******* City Choices*******')
    # # print(city_choices)
    # #

    # cityopt = AjaxModelChoiceField(City,required=False, initial='None', disabled=False,
    #                                  widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))
    #
    # city = forms.CharField(label=_("City"),required=False,error_messages={'required':"Valid city."},
    #                                widget=forms.TextInput(
    #                                    attrs={'placeholder':
    #                                           _('city name'),'class': "inp_card_info_city"}))
    #
    #
    # county = forms.CharField(label=_("County"), required=False, disabled=False,
    #                        widget=forms.TextInput(
    #                            attrs={'placeholder':
    #                                       _('county name'), 'class': "inp_card_info_county"}))
    # state = forms.CharField(label=_("State"), required=False, disabled=False,
    #                        widget=forms.TextInput(
    #                            attrs={'placeholder':
    #                                       _('state name'), 'class': "inp_card_info_state"}))
    #
    #
    # cardnumber = forms.IntegerField(label=_("Card Number"), required=True,error_messages={'required':"Enter credit card details."},
    #                                 widget=forms.NumberInput(
    #                                  attrs={'placeholder':_(' Enter the credit card number'),
    #                                         'class': "inp_card_info"}))
    #
    # cardmonth = forms.ChoiceField(choices=MONTHS, required=True,initial=datetime.datetime.now().month,
    #                               widget=forms.Select(
    #                                   attrs={'class': "inp_card_info_expire_month"})
    #                               )
    #
    # cardyear = forms.ChoiceField(choices=YEARS, required=True,initial=datetime.datetime.now().year,
    #                              widget=forms.Select(
    #                                  attrs={'class': "inp_card_info_expire_year"})
    #                              )
    #
    # cardcvv = forms.IntegerField(label=_("CVV"), required=True,
    #                              error_messages={'required': "CVV is mandatory."},
    #                                 widget=forms.NumberInput(
    #                                     attrs={'placeholder':
    #                                                _(' CVV'),
    #                                            'class': "inp_card_info_cvv"}))


    # city = forms.CharField(label=_("City"), required=True,
    #                                widget=forms.Select(choices=City.objects.get('name').order_by('name')),
    #                                    attrs={'class': "inp_card_info_state"}))


    def __init__(self, request,*args, **kwargs):
        print("BaseComplianceRegisterForm ")

        super(BaseComplianceRegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        # self.helper.field_template = 'bootstrap3/layout/inline_field.html'

        self.helper.layout = Layout(
            # InlineField('like_website', readonly=True),
            # 'like_website',
            # CommonLayout,
            'todo',
            'date',
            'reminder',

            InlineField('favorite_food'),
            InlineField('favorite_number'),
            InlineField('notes'),
            Div(
                'favorite_food',
                'favorite_bread',
                css_class='container-fluid'
            ),
            # StrictButton('Sign in', css_class='btn-default'),
        )
        self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        self.helper.add_input(Submit('submit', 'Submit'))

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

        super(BaseComplianceRegisterForm, self).__init__(*args, **kwargs)

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
        cleaned_data = super(BaseComplianceRegisterForm, self).clean()
        return cleaned_data


class ComplianceForm(BaseComplianceRegisterForm):
    class Meta:
        widgets = {
            'code': TextInput(attrs={'class': 'input-mini'}),
            'independence_day': SuitDateWidget,
            'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                                  attrs={'class': 'input-small'}),
            'population': EnclosedInput(prepend='icon-user',
                                        append='<input type="button" '
                                               'class="btn" onclick="window'
                                               '.open(\'https://www.google'
                                               '.com/\')" value="Search">',
                                        attrs={'class': 'input-small'}),
            'description': AutosizedTextarea,
            'architecture': AutosizedTextarea(attrs={'class': 'span5'}),
        }

    suit_form_tabs = (('general', 'General'), ('cities', 'Cities'),
                      ('flag', 'Flag'), ('info', 'Info on tabs'))

    def __init__(self, *args, **kwargs):
        # self.plan = Product.objects.all()
        print("ComplianceForm")
        super(ComplianceForm, self).__init__(*args, **kwargs)


    def clean(self):

        print("1:RegisterForm clean")
        super(ComplianceForm, self).clean()
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

