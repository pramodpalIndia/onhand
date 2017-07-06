from django.apps import apps as django_apps
from django.conf import settings
from . import app_settings, apps
import json
import recurly
from django.core.exceptions import ImproperlyConfigured

import os, sys
import imp

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *


with open("secrets.json") as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    # print('get_secret..')
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

def recurlyonfiguration():
    try:
        recurly.SUB_DOMAIN = get_secret("SUB_DOMAIN")
        recurly.API_KEY = get_secret("API_KEY")
        recurly.DEFAULT_CURRENCY = get_secret("DEFAULT_CURRENCY")
        # print('recurlyonfiguration set Domain keys', recurly.SUB_DOMAIN ,recurly.API_KEY, recurly.DEFAULT_CURRENCY)
        # for plan in recurly.Plan.all():
        #     print(plan.name)
        # return secrets[setting]
    except KeyError:
        error_msg = "Set the environment variable for authentication credentials:"
        raise ImproperlyConfigured(error_msg)

def recurlyonfiguration():
    try:
        recurly.SUB_DOMAIN = get_secret("SUB_DOMAIN")
        recurly.API_KEY = get_secret("API_KEY")
        recurly.DEFAULT_CURRENCY = get_secret("DEFAULT_CURRENCY")
        # print('recurlyonfiguration set Domain keys', recurly.SUB_DOMAIN ,recurly.API_KEY, recurly.DEFAULT_CURRENCY)
        # for plan in recurly.Plan.all():
        #     print(plan.name)
        # return secrets[setting]
    except KeyError:
        error_msg = "Set the environment variable for authentication credentials:"
        raise ImproperlyConfigured(error_msg)

# recurlyonfiguration()


def AuthorizeNetConfiguration():
    try:
        # merchantAuth = apicontractsv1.merchantAuthenticationType()
        # merchantAuth.name = constants.apiLoginId
        # merchantAuth.transactionKey = constants.transactionKey

        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = get_secret("API_LOGIN_ID")
        merchantAuth.transactionKey = get_secret("API_TRANSACTION_KEY")


        # print('recurlyonfiguration set Domain keys', recurly.SUB_DOMAIN ,recurly.API_KEY, recurly.DEFAULT_CURRENCY)
        # for plan in recurly.Plan.all():
        #     print(plan.name)
        # return secrets[setting]
    except KeyError:
        error_msg = "Set the environment variable for authentication credentials:"
        raise ImproperlyConfigured(error_msg)

AuthorizeNetConfiguration()


def get_person_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.Person')
    except ValueError:
        raise ImproperlyConfigured("OH_PERSON_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "OH_PERSON_MODEL refers to model '%s' that has not been installed" % settings.OH_PERSON_MODEL
        )

def get_company_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.Company')
    except ValueError:
        raise ImproperlyConfigured("OH_PERSON_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "Company refers to model 'subscription.company' that has not been installed"
        )

def get_company_person_role_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.CompanyPersonRole')
    except ValueError:
        raise ImproperlyConfigured("oh_company_person_role must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "Company refers to model 'subscription.CompanyPersonRole' that has not been installed"
        )

def get_company_language_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.CompanyLanguage')
    except ValueError:
        raise ImproperlyConfigured("oh_company_language must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "Company refers to model 'subscription.CompanyLanguage' that has not been installed"
        )

def get_person_language_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.PersonLanguage')
    except ValueError:
        raise ImproperlyConfigured("oh_person_language must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "Company refers to model 'subscription.PersonLanguage' that has not been installed"
        )


def get_address_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('management.address')
    except ValueError:
        raise ImproperlyConfigured("OH_PERSON_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "OH_PERSON_MODEL refers to model '%s' that has not been installed" % settings.OH_PERSON_MODEL
        )

def get_user_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('users.user')
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % 'users.user'
        )

def get_subscription_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.Subscription')
    except ValueError:
        raise ImproperlyConfigured("oh_subscription must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_subscription refers to model '%s' that has not been installed" % 'subscription.Subscription'
        )


def get_subscriptiondetail_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('subscription.SubscriptionDetail')
    except ValueError:
        raise ImproperlyConfigured("oh_subscription_detail must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_subscription_detail refers to model '%s' that has not been installed" % 'subscription.SubscriptionDetail'
        )
