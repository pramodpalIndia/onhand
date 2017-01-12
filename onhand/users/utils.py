from django.core import urlresolvers
from django.db import models
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import int_to_base36, base36_to_int, urlencode
from django.contrib import messages
# from onhand.subscription import app_settings
from . import app_settings
# from .adapter import get_useradapter
from onhand.subscription.adapter import get_adapter
from onhand.users import signals
from onhand.users.exceptions import ImmediateHttpResponse


from django.core.validators import  ValidationError

from django.utils.six.moves.urllib.parse import urlsplit


from django.utils import six


from django.contrib.sites.models import Site

from onhand.subscription.compat import OrderedDict, importlib

from . import  get_user_model

try:
    from django.utils.encoding import force_text, force_bytes
except ImportError:
    from django.utils.encoding import force_unicode as force_text

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

def set_form_field_order(form, fields_order):
    assert isinstance(form.fields, OrderedDict)
    form.fields = OrderedDict(
        (f, form.fields[f])
        for f in fields_order)

def build_absolute_uri(request, location, protocol=None):
    """request.build_absolute_uri() helper

    Like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    from onhand.subscription import app_settings as account_settings

    if request is None:
        site = get_current_site()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = '{proto}://{domain}{url}'.format(
                proto=account_settings.DEFAULT_HTTP_PROTOCOL,
                domain=site.domain,
                url=location)
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)

def get_username_max_length():
    # from .app_settings import USER_MODEL_USERNAME_FIELD
    # if USER_MODEL_USERNAME_FIELD is not None:
    #     User = get_user_model()
    #     max_length = User._meta.get_field(USER_MODEL_USERNAME_FIELD).max_length
    max_length = 45
    # else:
    #     max_length = 0
    return max_length


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


def user_field(user, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(user, field):
        if args:
            # Setter
            v = args[0]
            if v:
                User = get_user_model()
                # v = v[0:User._meta.get_field(field).max_length]
            setattr(user, field, v)
        else:
            # Getter
            return getattr(user, field)

def user_username(user, *args):
    return user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, *args)


def get_request_param(request, param, default=None):
    return request.POST.get(param) or request.GET.get(param, default)

def get_next_redirect_url(request, redirect_field_name="next"):
    """
    Returns the next URL to redirect to, if it was explicitly passed
    via the request.
    """
    redirect_to = get_request_param(request, redirect_field_name)
    if not get_adapter(request).is_safe_url(redirect_to):
        redirect_to = None
    return redirect_to


def get_login_redirect_url(request, url=None, redirect_field_name="next"):
    from onhand.users.adapter import get_useradapter
    # adapter = get_useradapter(request)

    if url and callable(url):
        # In order to be able to pass url getters around that depend
        # on e.g. the authenticated state.
        url = url()
    redirect_url = (
        url or
        get_next_redirect_url(
            request,
            redirect_field_name=redirect_field_name) or
        get_useradapter(request).get_login_redirect_url(request))
    return redirect_url

_user_display_callable = None


def perform_login(request, user, email_verification,
                  redirect_url=None, signal_kwargs=None,
                  signup=False):
    """
    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """
    # Local users are stopped due to form validation checking
    # is_active, yet, adapter methods could toy with is_active in a
    # `user_signed_up` signal. Furthermore, social users should be
    # stopped anyway.
    from onhand.users.adapter import get_useradapter
    adapter = get_useradapter(request)
    if user.is_active != 'Y':
        return adapter.respond_user_inactive(request, user)

    try:
        # redirect_url =reverse('account_inactive')
        adapter = get_useradapter(request)
        adapter.login(request, user)

        # if signal_kwargs is None:
            # print('signal_kwargs.pop(newsignup)',signal_kwargs.get('newsignup'))
            # redirect_url = reverse('account:account_inactive')

        response = HttpResponseRedirect(
            get_login_redirect_url(request, redirect_url))

        if signal_kwargs is None:
            signal_kwargs = {}
        # else:
            # print('signal_kwargs.pop(newsignup)',signal_kwargs.pop('newsignup'))
            # # redirect_url = reverse('account:account_inactive')
            # adapter.add_message(
            #     request,
            #     messages.SUCCESS,
            #     'account/messages/servicesetup.txt',
            #     {'user': user})

        signals.user_logged_in.send(sender=user.__class__,
                                    request=request,
                                    response=response,
                                    user=user,
                                    **signal_kwargs)
        adapter.add_message(
            request,
            messages.SUCCESS,
            'account/messages/logged_in.txt',
            {'user': user})
    except ImmediateHttpResponse as e:
        response = e.response
    return response

def complete_signup(request, user, email_verification, success_url,
                    signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {'newsignup' : True}
    signals.user_signed_up.send(sender=user.__class__,
                                request=request,
                                user=user,
                                **signal_kwargs)

    print(' User util.py -> complete_signup')
    return perform_login(request, user,
                         email_verification=email_verification,
                         signup=True,
                         redirect_url=success_url,
                         signal_kwargs=signal_kwargs)




def passthrough_next_redirect_url(request, url, redirect_field_name):
    assert url.find("?") < 0  # TODO: Handle this case properly
    next_url = get_next_redirect_url(request, redirect_field_name)
    if next_url:
        url = url + '?' + urlencode({redirect_field_name: next_url})
    return url


def user_pk_to_url_str(user):
    """
    This should return a string.
    """
    User = get_user_model()
    if (hasattr(models, 'UUIDField') and issubclass(
            type(User._meta.pk), models.UUIDField)):
        if isinstance(user.pk, six.string_types):
            return user.pk
        return user.pk.hex

    ret = user.pk
    if isinstance(ret, six.integer_types):
        ret = int_to_base36(user.pk)
    return str(ret)


def url_str_to_user_pk(s):
    User = get_user_model()
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    if getattr(User._meta.pk, 'rel', None):
        pk_field = User._meta.pk.rel.to._meta.pk
    else:
        pk_field = User._meta.pk
    if (hasattr(models, 'UUIDField') and issubclass(
            type(pk_field), models.UUIDField)):
        return s
    try:
        pk_field.to_python('a')
        pk = s
    except ValidationError:
        pk = base36_to_int(s)
    return pk


def resolve_url(to):
    """
    Subset of django.shortcuts.resolve_url (that one is 1.5+)
    """
    try:
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
