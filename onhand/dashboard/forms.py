import warnings
from crispy_forms.bootstrap import StrictButton, InlineField

from django import forms
from django.contrib.admin.options import BaseModelAdmin
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from django.core import validators
from django.contrib.auth.tokens import default_token_generator
from suit_dashboard.box import Box
from suit_dashboard.layout import Grid, Row, Column
from suit_dashboard.views import DashboardView

from onhand.examples.models import CountryExample, CityExample, Fridge
from onhand.users.utils import (set_form_field_order,
                     build_absolute_uri,
                     get_username_max_length,
                     get_current_site)

from onhand.users.utils import (perform_login, url_str_to_user_pk,
                    user_username, user_pk_to_url_str,
                    get_user_model,
                    )
# from onhand.users.app_settings import AuthenticationMethod
from onhand.users.utils import app_settings
from onhand.users.adapter import get_adapter, get_useradapter

from onhand.subscription import app_settings

from onhand.subscription.forms import BaseSignupForm
# from allauth.account.forms import BaseSignupForm


from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, ModelForm, Textarea, Select

from onhand.compliance.models import ServiceJurisdiction
from suit.admin import SortableTabularInline, SortableModelAdmin, \
    SortableStackedInline
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, \
    EnclosedInput, LinkedSelect, AutosizedTextarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, MultiField, Div
from bootstrap4_datetime.widgets import DateTimePicker


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


class DashboardStatisticsView(DashboardView):
    # template_name = 'dashboard/main.html'
    # model = User
    # These next two lines tell the view to index lookups by username
    # slug_field = 'username'
    # slug_url_kwarg = 'username'
    # grid = Grid(Row(Column(BoxMachine(), width=12)))
    grid = Grid(
      Row(
        Column(
          Box(html_id='allitems',title=1,description='All Items'),
          width=1),
        Column(
          Box(html_id='services',title=1,description='Services'),
          width=1),
        Column(
              Box(html_id='insurance',title='2',description='Insurance'),
              width=1),
        Column(
              Box(html_id='filing',title='3',description='Filings & Permits'),
              width=1),
        Column(
              Box(html_id='violation',title='1',description='Violations & Suits'),
              width=1),
        Column(
              Box(html_id='current',title='20',description='Current'),
              width=1),
        Column(
              Box(html_id='attention',title='0',description='Coming Due'),
              width=1),
        Column(
              Box(html_id='pastdue',title='0',description='Past Due'),
              width=1),
      ),
        Row(
            Column(
                Box(),
                width=12),
        ),
        Row(
            Column(Row(
                Column(
                    Box(html_id='filtertitle', title='Showing :', description=''),
                    width=1),
                Column(
                    Box(html_id='showfilters', title='All Items'),
                    width=1))),
        ),

    )

class ExampleForm(forms.Form):
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
        label = "Do you like this website?",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '1',
        required = True,
    )

    favorite_food = forms.CharField(
        label = "What is your favorite food?",
        max_length = 80,
        required = False,
    )

    favorite_number = forms.IntegerField(
        label = "Favorite number",
        required = False,
    )

    notes = forms.CharField(
        label = "Additional notes or feedback",
        required = False,
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


class BaseDashboardForm(forms.Form):
    todo = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD",
                                       "pickTime": False}))
    reminder = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False}))
    # inlines = (FridgeInline)

    data = {'subject': 'hello',
             'message': 'Hi there'}


    widgets = {
        'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                              attrs={'class': 'input-small'}),
        'population': EnclosedInput(append='icon-user',
                                    attrs={'class': 'input-small'}),
    }

    def __init__(self,request, *args, **kwargs):
        print('BaseDashboardForm__init__ :')
        super(BaseDashboardForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('\nBaseDashboardForm self.changed_data',self.changed_data)
        cleaned_data = super(BaseDashboardForm, self).clean()
        return cleaned_data

    def custom_signup(self, request, user):
        custom_form = super(BaseDashboardForm, self)
        if hasattr(custom_form, 'signup') and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
            # Historically, it was called .save, but this is confusing
            # in case of ModelForm
            custom_form.save(user)

class DashboardForm(BaseDashboardForm):

    def __init__(self,request, *args, **kwargs):

        print('DashboardForm__init__ PP:')
        super(BaseDashboardForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('\nBaseSignupServiceForm self.changed_data',self.changed_data)
        cleaned_data = super(BaseDashboardForm, self).clean()
        return cleaned_data

    def save(self, request, redirect_url=None):
        print('DashboardForm save')
        # from onhand.users.adapter import get_useradapter
        from onhand.users.models import User
        # adapter = get_useradapter(request)
        # user = adapter.new_user(request)
        # adapter.save_user(request, user, self)
        user_pk_str = request.session.get('account_user', None)
        user = User.objects.get(pk=user_pk_str)

        return user


class CityExampleInlineForm(ModelForm):
    class Meta:
        widgets = {
            'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                                  attrs={'class': 'input-small'}),
            'population': EnclosedInput(append='icon-user',
                                        attrs={'class': 'input-small'}),
        }


class CityExampleInline(admin.TabularInline):
    form = CityExampleInlineForm
    model = CityExample
    extra = 3
    verbose_name_plural = 'Cities'
    suit_classes = 'suit-tab suit-tab-cities'


class CountryExampleForm(ModelForm):
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


class CountryExampleAdmin(ModelAdmin):
    form = CountryExampleForm
    # search_fields = ('name', 'code')
    list_display = ('name', 'code', 'continent', 'independence_day')
    list_filter = ('continent',)
    date_hierarchy = 'independence_day'
    list_select_related = True

    inlines = (CityExampleInline,)

    fieldsets = [
        (None, {
            'classes': ('suit-tab suit-tab-general',),
            'fields': ['name', 'continent', 'code', 'independence_day']
        }),
        ('Statistics', {
            'classes': ('suit-tab suit-tab-general',),
            'description': 'EnclosedInput widget examples',
            'fields': ['area', 'population']}),
        ('Autosized textarea', {
            'classes': ('suit-tab suit-tab-general',),
            'description': 'AutosizedTextarea widget example - adapts height '
                           'based on user input',
            'fields': ['description']}),
        ('Architecture', {
            'classes': ('suit-tab suit-tab-cities',),
            'description': 'Tabs can contain any fieldsets and inlines',
            'fields': ['architecture']}),
    ]

    suit_form_tabs = (('general', 'General'), ('cities', 'Cities'),
                      ('flag', 'Flag'), ('info', 'Info on tabs'))

    suit_form_includes = (
        ('admin/examples/CountryExample/tab_disclaimer.html', 'middle', 'cities'),
        ('admin/examples/CountryExample/tab_flag.html', '', 'flag'),
        ('admin/examples/CountryExample/tab_info.html', '', 'info'),
    )

admin.site.register(CountryExample, CountryExampleAdmin)


