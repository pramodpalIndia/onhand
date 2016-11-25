from django.apps import apps as django_apps
from django.conf import settings
import json
import recurly
from django.core.exceptions import ImproperlyConfigured


with open("secrets.json") as f:
    secrets = json.loads(f.read())


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
