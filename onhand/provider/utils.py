from datetime import timedelta
from django.db import models
from django.utils.http import int_to_base36, base36_to_int
from django.core.exceptions import ValidationError

import recurly

import math
from itertools import chain

from django import forms
# from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from onhand.provider import adapter, get_subscription_model
from onhand.provider import app_settings

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

from . import signals, get_person_model, get_company_model, get_address_model, get_user_model
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


def person_field(person, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(person, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Person = get_person_model()
                # v = v[0:Person._meta.get_field(field).max_length]
            setattr(person, field, v)
        else:
            # Getter
            return getattr(person, field)

def company_field(company, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(company, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Company = get_company_model()
                # v = v[0:Company._meta.get_field(field).max_length]
            setattr(company, field, v)
        else:
            # Getter
            return getattr(company, field)

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

def address_field(address, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(address, field):
        if args:
            # Setter
            v = args[0]
            if v:
                Address = get_address_model()
                v = v[0:Address._meta.get_field(field).max_length]
            setattr(address, field, v)
        else:
            # Getter
            return getattr(address, field)

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

def provider_create_account(request, person, company, address, account):

    try:
        print("Create Account -> Using Recurly API : Start")
        print("person.prsn_id : ", person,company,address)
        print("person.prsn_id : ",person.prsn_id)
        account = recurly.Account(account_code=person.prsn_id)
        print("person.prsn_id : ", account)
        account.email = person.email
        account.first_name = person.first_name
        account.last_name = person.last_name


        print('Account created  Sucessfully')

        #Create an Accounts Billing Info (Credit Card)
        # account = recurly.Account.get(person.prsn_id)
        print('getting IP ',get_client_ip(request))
        billing_info = recurly.BillingInfo

        billing_info.first_name = person.first_name
        billing_info.last_name = person.last_name

        print(company.name, company)
        billing_info.company = company.name

        print('getting IP ', get_client_ip(request))

        billing_info.ip_address = get_client_ip(request)

        billing_info.country = "United States"
        billing_info.address1 = address.address_line_1
        billing_info.address2 = address.address_line_2
        billing_info.city = address.city.name

        print('address.address_line_1 :', address.address_line_1)
        print('address.address_line_2 :', address.address_line_2)
        print('address.city.name :', address.city.name)
        print('address.city.zipc_code :', address.city.zipc_code_id)
        print('address.city.zipc_code_id.county_id.state_id.name :', address.city.zipc_code.county.state.name)

        billing_info.state = address.city.zipc_code.county.state.name
        billing_info.zip = address.city.zipc_code_id

        print('request.GET.get(cardnumber, None)', request.POST.get('cardnumber', None))
        print('request.GET.get(cardcvv, None)', request.POST.get("cardcvv", ""))
        print('request.GET.get(cardmonth, None)', request.POST.get("cardmonth", ""))
        print('request.GET.get(cardyear, None)', request.POST.get("cardyear", ""))

        billing_info.number =request.POST.get("cardnumber", None)
        billing_info.verification_value = request.POST.get("cardcvv", None)
        billing_info.month = request.POST.get("cardmonth", None)
        billing_info.year = request.POST.get("cardyear", None)
        billing_info.currency = 'USD'

        account.save()

        print(billing_info)



        # account.update_billing_info(billing_info)

        print("Create Account -> Using Recurly API : End")

    except:
        return None
    return account

def complete_signup(request, person, company, address, provider_subscription_api_id, signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    signals.user_signed_up.send(sender=person.__class__,
                                request=request,
                                person=person,
                                **signal_kwargs)
    adapter = get_adapter(request)
    adapter.stash_person(request, person)
    adapter.stash_company( request, company)
    print('adapter.stash_subscription(request, provider_subscription_api_id)',provider_subscription_api_id)
    adapter.stash_providersubscription(request, provider_subscription_api_id)

    return adapter.respond_person_registered(request)

def url_str_to_person_pk(s):
    Person = get_person_model()
    print('Person = get_person_model()' , Person)
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    if getattr(Person._meta.pk, 'rel', None):
        pk_field = Person._meta.pk.rel.to._meta.pk
        print('Person._meta.pk.rel.to._meta.pk', pk_field)
    else:
        pk_field = Person._meta.pk
    if (hasattr(models, 'UUIDField') and issubclass(
            type(pk_field), models.UUIDField)):
        print('hasattr -> return s', s)
        return str(s)
    try:
        pk_field.to_python('a')
        pk = s
    except ValidationError:
        pk = base36_to_int(str(s))
    return pk

def url_str_to_address_pk(s):
    Address = get_address_model()
    print('Person = get_person_model()' , Address)
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    if getattr(Address._meta.pk, 'rel', None):
        pk_field = Address._meta.pk.rel.to._meta.pk
        print('Person._meta.pk.rel.to._meta.pk', pk_field)
    else:
        pk_field = Address._meta.pk
    if (hasattr(models, 'UUIDField') and issubclass(
            type(pk_field), models.UUIDField)):
        print('hasattr -> return s', s)
        return str(s)
    try:
        pk_field.to_python('a')
        pk = s
    except ValidationError:
        pk = base36_to_int(str(s))
    return pk

def person_pk_to_url_str(person):
    """
    This should return a string.
    """
    Person = get_person_model()
    if (hasattr(models, 'UUIDField') and issubclass(
            type(Person._meta.pk), models.UUIDField)):
        if isinstance(person.pk, six.string_types):
            return person.pk
        return person.pk.hex

    ret = person.pk
    if isinstance(ret, six.integer_types):
        ret = int_to_base36(person.pk)
    return str(ret)

def url_str_to_company_pk(s):
    Company = get_company_model()
    print('Person = get_person_model()' , Company)
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    if getattr(Company._meta.pk, 'rel', None):
        pk_field = Company._meta.pk.rel.to._meta.pk
        print('Company._meta.pk.rel.to._meta.pk', pk_field)
    else:
        pk_field = Company._meta.pk
    if (hasattr(models, 'UUIDField') and issubclass(
            type(pk_field), models.UUIDField)):
        print('hasattr -> return s', s)
        return str(s)
    try:
        pk_field.to_python('a')
        pk = s
    except ValidationError:
        pk = base36_to_int(str(s))
    return pk

class ColumnCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Widget that renders multiple-select checkboxes in columns.
    Constructor takes number of columns and css class to apply
    to the <ul> elements that make up the columns.
    """

    def __init__(self, columns=2, css_class=None, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.columns = columns
        self.css_class = css_class

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        choices_enum = list(enumerate(chain(self.choices, choices)))

        # This is the part that splits the choices into columns.
        # Slices vertically.  Could be changed to slice horizontally, etc.
        column_sizes = columnize(len(choices_enum), self.columns)
        columns = []
        for column_size in column_sizes:
            columns.append(choices_enum[:column_size])
            choices_enum = choices_enum[column_size:]
        output = []
        for column in columns:
            if self.css_class:
                output.append(u' class="%s" ' % self.css_class)
            else:
                output.append(u'')
            # Normalize to strings
            str_values = set([(v) for v in value])
            for i, (option_value, option_label) in column:
                # If an ID attribute was given, add a numeric index as a suffix,
                # so that the checkboxes don't all have the same ID attribute.
                if has_id:
                    final_attrs = dict(final_attrs, id='%s_%s' % (
                        attrs['id'], i))
                    label_for = u' for="%s"  style="margin-right: 20px;"' % final_attrs['id']
                else:
                    label_for = ''

                cb = forms.CheckboxInput(
                    final_attrs, check_test=lambda value: value in str_values)
                # option_value = option_value)
                rendered_cb = cb.render(name, option_value)
                option_label = conditional_escape(option_label)
                output.append(u'<label%s>%s %s</label>' % (
                    label_for, rendered_cb, option_label))
            output.append(u'')
        return mark_safe(u'\n'.join(output))


def columnize(items, columns):
    """
    Return a list containing numbers of elements per column if `items` items
    are to be divided into `columns` columns.

    >>> columnize(10, 1)
    [10]
    >>> columnize(10, 2)
    [5, 5]
    >>> columnize(10, 3)
    [4, 3, 3]
    >>> columnize(3, 4)
    [1, 1, 1, 0]
    """
    elts_per_column = []
    for col in range(columns):
        col_size = int(math.ceil(float(items) / columns))
        elts_per_column.append(col_size)
        items -= col_size
        columns -= 1
    return elts_per_column


