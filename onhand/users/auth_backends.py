from django.contrib.auth.backends import ModelBackend
from .utils import get_user_model
# from .app_settings import
from . import app_settings


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        ret = None
        # if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
        #     ret = self._authenticate_by_email(**credentials)
        # elif app_settings.AUTHENTICATION_METHOD \
        #         == AuthenticationMethod.USERNAME_EMAIL:
        #     ret = self._authenticate_by_email(**credentials)
        #     if not ret:
        #         ret = self._authenticate_by_username(**credentials)
        # else:
        ret = self._authenticate_by_username(**credentials)
        return ret

    def _authenticate_by_username(self, **credentials):
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        username = credentials.get('username')
        password = credentials.get('password')

        User = get_user_model()

        if not username_field or username is None or password is None:
            return None
        try:
            # Username query is case insensitive
            query = {username_field+'__iexact': username}
            user = User.objects.get(**query)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
