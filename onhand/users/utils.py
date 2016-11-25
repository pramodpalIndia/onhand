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
