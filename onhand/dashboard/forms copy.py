import warnings

from django import forms
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from django.core import validators
from django.contrib.auth.tokens import default_token_generator

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

class BaseDashboardForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()

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

        print('DashboardForm__init__ :')
        super(BaseDashboardForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('\nBaseSignupServiceForm self.changed_data',self.changed_data)
        cleaned_data = super(BaseDashboardForm, self).clean()
        return cleaned_data

    def save(self, request):
        print('DashboardForm')
        # from onhand.users.adapter import get_useradapter
        from onhand.users.models import User
        # adapter = get_useradapter(request)
        # user = adapter.new_user(request)
        # adapter.save_user(request, user, self)
        user_pk_str = request.session.get('account_user', None)
        user = User.objects.get(pk=user_pk_str)

        return user
