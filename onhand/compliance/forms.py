from __future__ import absolute_import

import datetime
import warnings

from django import forms
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

from onhand.compliance.models import ComplianceServiceType, ServiceJurisdiction, V_Service_jurisdiction
from onhand.subscription.models import Person, Company, CompanyRole
from onhand.subscription.utils import  provider_create_account, person_field, ColumnCheckboxSelectMultiple, \
    url_str_to_company_pk, url_str_to_address_pk,  complete_signup_prelim_registration, set_form_field_order
# from onhand.users.adapter import get_useradapter
from onhand.users.models import User
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


class BaseComplianceRegisterForm(forms.Form):

    complianceservice = forms.ModelChoiceField(queryset=None,required=False, initial='None', disabled=False,
                                               label='Service',
                                               widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown"}))
    factorvalue = forms.CharField(required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}))

    frequency = forms.ModelChoiceField(queryset=Basis.objects.all(),
                                               required=False, initial='None', disabled=False,
                                               label='Frequency',
                                               widget=forms.Select(attrs={'class': "inp_card_info_city_dropdown",'style':"position:relative; left:1px; top:76px;"}))

    lastservicedate = forms.CharField(label="Last Service Date", required=False,disabled=True,widget=forms.TextInput(
                                                               attrs={ 'class':"inp_card_info_firstname",'style':"position:relative; left:134px; top:25px; width:78px;"}))


    nextservicedate = forms.CharField(label="Next Service Date", required=True, widget=forms.TextInput(
        attrs={'class': "inp_card_info_firstname", 'style': "position:relative; left:388px; top:25px; width:78px;"}))


    servicenote = forms.CharField(required=False,label="Compliance Service note", widget=forms.Textarea(attrs={'class': "form-control", 'style': "position:relative; left:135px; top:20px; width:440px; height:120px;"}))


    def __init__(self, request,*args, **kwargs):
        print("BaseComplianceRegisterForm , request.session['account_county'] ",request.session['account_county'])
        super(BaseComplianceRegisterForm, self).__init__(*args, **kwargs)
        self.fields['complianceservice'].queryset = ServiceJurisdiction.objects.filter(srvj_id__in= V_Service_jurisdiction.objects.filter(cont_id=request.session['account_county']).values('srvj_id'))

    def clean_complianceservice(self):
        print("Validate complianceservice")
        value = self.cleaned_data["complianceservice"]
        value = get_adapter().clean_complianceservice(value)
        return value

    def clean_factorvalue(self):
        print("Validate factorvalue")
        value = self.cleaned_data["factorvalue"]
        value = get_adapter().clean_factorvalue(value)
        return value

    def clean_frequency(self):
        print("Validate frequency")
        value = self.cleaned_data["frequency"]
        value = get_adapter().clean_frequency(value)
        return value

    def clean_lastservicedate(self):
        print("Validate lastservicedate")
        value = self.cleaned_data["lastservicedate"]
        value = get_adapter().clean_lastservicedate(value)
        return value

    def clean_nextservicedate(self):
        print("Validate nextservicedate")
        value = self.cleaned_data["nextservicedate"]
        value = get_adapter().clean_nextservicedate(value)
        return value

    def clean_servicenote(self):
        print("Validate servicenote")
        value = self.cleaned_data["servicenote"]
        value = get_adapter().clean_servicenote(value)
        return value


    def clean(self):
        print("2:BaseComplianceRegisterForm clean")
        cleaned_data = super(BaseComplianceRegisterForm, self).clean()
        return cleaned_data


class ComplianceForm(BaseComplianceRegisterForm):

    def __init__(self, *args, **kwargs):
        # self.plan = Product.objects.all()
        print("ComplianceForm")
        super(ComplianceForm, self).__init__(*args, **kwargs)


    def clean(self):
        print("1:ComplianceForm clean")
        super(ComplianceForm, self).clean()
        return self.cleaned_data

    def save(self, request, redirect_url=None):
        print("ComplianceForm save")
        adapter = get_adapter(request)
        print(adapter)

        """
        Create seperate address for each Person and Company;
        Reason: Address can be changed for each instances
        """

        complianceservice = adapter.new_complianceservice(request)
        print('Created new complianceservice object', complianceservice)
        complianceservice_new = adapter.save_complianceservice(request, complianceservice, self)
        print('Created  complianceservice_new object',complianceservice_new)

        form_factor = request.GET.get('factorvalue', None)
        if form_factor:
            compliancefactor = adapter.new_complianceservicefactor(request)
            compliancefactor = adapter.save_complianceservicefactor(request, compliancefactor, complianceservice_new, self)

        responsible_data = {}
        responsible_data['form_recordtype_id'] = int(complianceservice_new.csrv_id)

        if request.method == 'POST':
            responsible_data['form_responsible'] = request.POST.get('responsiblelist', User.objects.get(
                pk=request.session['_auth_user_id']).cprs_id_id)
        if request.method == 'GET':
            responsible_data['form_responsible'] = request.GET.get('responsiblelist',  User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id)

        print('responsible_data[form_responsible]',responsible_data['form_responsible'])
        responsible_data['form_assigner'] = User.objects.get(pk=request.session['_auth_user_id']).cprs_id_id
        responsible_data['form_notes'] =  ""

        if responsible_data['form_recordtype_id']:
            compserviceresponsible = adapter.new_ComplianceResponsibility(request)
            adapter.save_complianceresponsibility(compserviceresponsible, responsible_data)
            print('Created New Responsible', compserviceresponsible.cres_id)

        ret =HttpResponseRedirect(reverse('home'))

        return ret
