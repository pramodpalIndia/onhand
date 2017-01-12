import warnings

from django import forms
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from django.core import validators
from django.contrib.auth.tokens import default_token_generator

from .utils import (set_form_field_order,
                     build_absolute_uri,
                     get_username_max_length,
                     get_current_site)

from .utils import (perform_login, url_str_to_user_pk,
                    user_username, user_pk_to_url_str,
                    get_user_model,
                    )
# from onhand.users.app_settings import AuthenticationMethod
from . import app_settings
from .adapter import get_adapter, get_useradapter

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
        user = get_useradapter(self.request).authenticate(
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
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data['remember']
        if remember:
            request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            request.session.set_expiry(0)
        return ret


class ServiceJurisdictionForm(ModelForm):
    class Meta:

        widgets = {
            'srvj_help_text': AutosizedTextarea(
                attrs={'class': 'input-medium', 'rows': 2,
                       'style': 'width:95%'}),
            'govl_code': Select(attrs={'class': 'input-small'}),
        }

        # model = ServiceJurisdiction

# admin.site.register(ServiceJurisdictionForm)


# class ServiceJurisdictionForm(ModelForm):
#     class Meta:
#         widgets = {
#             'srvj_id': TextInput(attrs={'class': 'input-small'}),
#             # 'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
#             # 'date_widget': SuitDateWidget,
#             # 'datetime_widget': SuitSplitDateTimeWidget,
#             # 'textfield': AutosizedTextarea(attrs={'rows': '2'}),
#             # 'linked_foreign_key': LinkedSelect,
#
#             # 'enclosed1': EnclosedInput(append='icon-plane',
#             #                            attrs={'class': 'input-medium'}),
#             # 'enclosed2': EnclosedInput(prepend='icon-envelope',
#             #                            append='<input type="button" '
#             #                                   'class="btn" value="Send">',
#             #                            attrs={'class': 'input-medium'}),
#         }
#         model = ServiceJurisdiction
#
# class ServiceJurisdiction(ModelForm):
#     class Meta:
#         widgets = {
#             'srvj_id': TextInput(attrs={'class': 'input-small'}),
#             # 'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
#             # 'date_widget': SuitDateWidget,
#             # 'datetime_widget': SuitSplitDateTimeWidget,
#             # 'textfield': AutosizedTextarea(attrs={'rows': '2'}),
#             # 'linked_foreign_key': LinkedSelect,
#             #
#             # 'enclosed1': EnclosedInput(append='icon-plane',
#             #                            attrs={'class': 'input-medium'}),
#             # 'enclosed2': EnclosedInput(prepend='icon-envelope',
#             #                            append='<input type="button" '
#             #                                   'class="btn" value="Send">',
#             #                            attrs={'class': 'input-medium'}),
#         }
#         model = ServiceJurisdiction
#
#
# # Kitchen sink model admin
# class ServiceJurisdictionAdmin(admin.ModelAdmin):
#     # raw_id_fields = ()
#     form = ServiceJurisdictionForm
#     # inlines = (FridgeInline, MicrowaveInline)
#     # search_fields = ['name']
#     # radio_fields = {"horizontal_choices": admin.HORIZONTAL,
#     #                 'vertical_choices': admin.VERTICAL}
#     # list_editable = ('boolean', )
#     # list_filter = ('choices', 'date')
#     # readonly_fields = ('readonly_field',)
#     # raw_id_fields = ('raw_id_field',)
#     fieldsets = [
#         (None, {'fields': ['srvj_id']}),
#         # (None, {'fields': ['name', 'help_text', 'textfield',
#         #                    ('multiple_in_row', 'multiple2'),
#         #                    'file', 'readonly_field']}),
#         # ('Date and time', {
#         #     'description': 'Improved date/time widgets (SuitDateWidget, '
#         #                    'SuitSplitDateTimeWidget) . Uses original JS.',
#         #     'fields': ['date_widget', 'datetime_widget']}),
#         #
#         # ('Foreign key relations',
#         #  {'description': 'Original select and linked select feature',
#         #   'fields': ['country', 'linked_foreign_key', 'raw_id_field']}),
#         #
#         # ('EnclosedInput widget',
#         #  {
#         #      'description': 'Supports Twitter Bootstrap prepended, '
#         #                     'appended inputs',
#         #      'fields': ['enclosed1', 'enclosed2']}),
#         #
#         # ('Boolean and choices',
#         #  {'fields': ['boolean', 'boolean_with_help', 'choices',
#         #              'horizontal_choices', 'vertical_choices']}),
#         #
#         # ('Collapsed settings', {
#         #     'classes': ('collapse',),
#         #     'fields': ['hidden_checkbox', 'hidden_choice']}),
#         # ('And one more collapsable', {
#         #     'classes': ('collapse',),
#         #     'fields': ['hidden_charfield', 'hidden_charfield2']}),
#
#     ]
#     # list_display = (
#     #     'name', 'help_text', 'choices', 'horizontal_choices', 'boolean')
#     list_display = (
#         'srvj_id' )
#
#     def get_formsets(self, request, obj=None):
#         """
#         Set extra=0 for inlines if object already exists
#         """
#         for inline in self.get_inline_instances(request):
#             formset = inline.get_formset(request, obj)
#             if obj:
#                 formset.extra = 0
#             yield formset


# admin.site.register(ServiceJurisdiction, ServiceJurisdictionAdmin)
