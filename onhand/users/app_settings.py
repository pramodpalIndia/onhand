class AppSettings(object):

    class AuthenticationMethod:
        USERNAME = 'username'
        EMAIL = 'email'
        USERNAME_EMAIL = 'username_email'

    def __init__(self, prefix):
        self.prefix = prefix
        # If login is by email, email must be required
        assert (self.AUTHENTICATION_METHOD ==
                self.AuthenticationMethod.USERNAME)
        if not self.USER_MODEL_USERNAME_FIELD:
            assert not self.USERNAME_REQUIRED
            assert self.AUTHENTICATION_METHOD \
                   not in (self.AuthenticationMethod.USERNAME)


    def _setting(self, name, dflt):
        # print('called_setting',self)
        from django.conf import settings
        getter = getattr(settings,
                         'ONHAND_SETTING_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        # print('getter(self.prefix + name, dflt)->',getter(self.prefix + name, dflt))
        return getter(self.prefix + name, dflt)

    @property
    def LOGOUT_REDIRECT_URL(self):
        return self._setting('LOGOUT_REDIRECT_URL', '/')

    @property
    def AUTHENTICATION_METHOD(self):
        ret = self.AuthenticationMethod.USERNAME
        return ret

    @property
    def USERNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("USERNAME_MIN_LENGTH", 5)

    @property
    def USERNAME_REQUIRED(self):
        """
        The user is required to enter a username when signing up
        """
        return self._setting("USERNAME_REQUIRED", True)

    @property
    def USER_MODEL_USERNAME_FIELD(self):
        return self._setting('USER_MODEL_USERNAME_FIELD', 'username')

    @property
    def DEFAULT_USER_ENROLMENT_ROLE(self):
        return self._setting("DEFAULT_USER_ENROLMENT_ROLE", "CUSTOM")

    @property
    def LOGIN_ATTEMPTS_LIMIT(self):
        """
        Number of failed login attempts. When this number is
        exceeded, the user is prohibited from logging in for the
        specified `LOGIN_ATTEMPTS_TIMEOUT`
        """
        return self._setting('LOGIN_ATTEMPTS_LIMIT', 5)

    @property
    def LOGIN_ATTEMPTS_TIMEOUT(self):
        """
        Time period from last unsuccessful login attempt, during
        which the user is prohibited from trying to log in.  Defaults to
        5 minutes.
        """
        return self._setting('LOGIN_ATTEMPTS_TIMEOUT', 60 * 5)

    @property
    def SESSION_COOKIE_AGE(self):
        """
        Deprecated -- use Django's settings.SESSION_COOKIE_AGE instead
        """
        from django.conf import settings
        return self._setting('SESSION_COOKIE_AGE', settings.SESSION_COOKIE_AGE)

    @property
    def SESSION_REMEMBER(self):
        """
        Controls the life time of the session. Set to `None` to ask the user
        ("Remember me?"), `False` to not remember, and `True` to always
        remember.
        """
        return self._setting('SESSION_REMEMBER', None)




# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa
app_settings = AppSettings('USER_')
# print('__name__',__name__)
app_settings.__name__ = __name__
# print('app_settings ->',app_settings.TEMPLATE_EXTENSION)
sys.modules[__name__] = app_settings
# print('app_settings ->',app_settings.TEMPLATE_EXTENSION)
# print('app_settings->',app_settings)
