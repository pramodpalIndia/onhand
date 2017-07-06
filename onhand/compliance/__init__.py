from django.apps import apps as django_apps
from django.conf import settings
from . import app_settings, apps
import json
import recurly
from django.core.exceptions import ImproperlyConfigured

import os, sys
import imp


def get_complianceservice_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('compliance.ComplianceService')
    except ValueError:
        raise ImproperlyConfigured("oh_compliance_service must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_compliance_service refers to model 'compliance.ComplianceService' that has not been installed"
        )

def get_complianceservicefactor_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model('compliance.FactorValue')
    except ValueError:
        raise ImproperlyConfigured("oh_factor_value must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_factor_value refers to model 'compliance.FactorValue' that has not been installed"
        )


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


def get_complianceserviceschedule_model():
    """
    Returns the User model that is active in this project.
    """
    # print('compliance.ComplianceServiceSchedule- get_complianceserviceschedule_model',django_apps.get_model('compliance.ComplianceServiceSchedule'))
    try:
        return django_apps.get_model('compliance.ComplianceServiceSchedule')
    except ValueError:
        raise ImproperlyConfigured("oh_compliance_service_schedule must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_compliance_service_schedule refers to model compliance.ComplianceServiceSchedule"
        )

def get_complianceserviceaction_model():
    """
    Returns the User model that is active in this project.
    """
    # print('compliance.ComplianceServiceSchedule- get_complianceserviceschedule_model',django_apps.get_model('compliance.ComplianceServiceSchedule'))
    try:
        return django_apps.get_model('compliance.ComplianceServiceAction')
    except ValueError:
        raise ImproperlyConfigured("oh_compliance_service_action must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_compliance_service_action refers to model compliance.ComplianceServiceAction"
        )

def get_providerserviceperson_model():
    """
    Returns the User model that is active in this project.
    """
    # print('compliance.ComplianceServiceSchedule- get_complianceserviceschedule_model',django_apps.get_model('compliance.ComplianceServiceSchedule'))
    try:
        return django_apps.get_model('compliance.ProviderServicePerson')
    except ValueError:
        raise ImproperlyConfigured("oh_provider_service_person must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_compliance_service_action refers to model compliance.ProviderServicePerson"
        )

def get_complianceresponsibility_model():
    """
    Returns the User model that is active in this project.
    """
    # print('compliance.ComplianceServiceSchedule- get_complianceserviceschedule_model',django_apps.get_model('compliance.ComplianceServiceSchedule'))
    try:
        return django_apps.get_model('compliance.ComplianceResponsibility')
    except ValueError:
        raise ImproperlyConfigured("oh_compliance_responsibility must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "oh_compliance_responsibility refers to model compliance.ComplianceResponsibility"
        )
