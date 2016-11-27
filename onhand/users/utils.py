from datetime import timedelta
from django.db import models
from django.http.response import HttpResponseRedirect
from django.utils.http import int_to_base36, base36_to_int
from django.core.exceptions import ValidationError
from django.contrib import messages

import recurly

import math
from itertools import chain

from django import forms
# from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from onhand.provider import adapter, get_subscription_model
from onhand.provider import app_settings
from onhand.provider.adapter import get_adapter
from onhand.users import signals
from onhand.users.exceptions import ImmediateHttpResponse

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


from django.utils import six


from django.contrib.sites.models import Site

from allauth.compat import OrderedDict, importlib

from . import  get_user_model






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
                v = v[0:User._meta.get_field(field).max_length]
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
    if url and callable(url):
        # In order to be able to pass url getters around that depend
        # on e.g. the authenticated state.
        url = url()
    redirect_url = (
        url or
        get_next_redirect_url(
            request,
            redirect_field_name=redirect_field_name) or
        get_adapter(request).get_login_redirect_url(request))
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
    adapter = get_adapter(request)
    if not user.is_active:
        return adapter.respond_user_inactive(request, user)

    try:
        adapter.login(request, user)
        response = HttpResponseRedirect(
            get_login_redirect_url(request, redirect_url))

        if signal_kwargs is None:
            signal_kwargs = {}
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
        signal_kwargs = {}
    signals.user_signed_up.send(sender=user.__class__,
                                request=request,
                                user=user,
                                **signal_kwargs)
    return perform_login(request, user,
                         email_verification=email_verification,
                         signup=True,
                         redirect_url=success_url,
                         signal_kwargs=signal_kwargs)
