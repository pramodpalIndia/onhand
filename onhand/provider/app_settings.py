# from django.conf import settings

# PERSON_MODEL = getattr(settings, 'OH_PERSON_MODEL')
# COMPANY_MODEL = getattr(settings, 'OH_COMPANY_MODEL')
PERSON_MODEL_FIRSTNAME_FIELD = 'firstname'

class AppSettings(object):

    class AuthenticationMethod:
        USERNAME = 'username'
        # EMAIL = 'email'
        # USERNAME_EMAIL = 'username_email'

    def __init__(self, prefix):
        self.prefix = prefix
        assert (self.AUTHENTICATION_METHOD ==
                self.AuthenticationMethod.USERNAME)
        if not self.USER_MODEL_USERNAME_FIELD:
            assert not self.USERNAME_REQUIRED
            # assert self.AUTHENTICATION_METHOD \
            #     not in (self.AuthenticationMethod.USERNAME,
            #             self.AuthenticationMethod.USERNAME)



    def _setting(self, name, dflt):
        # print('called_setting',self)
        from django.conf import settings
        getter = getattr(settings,
                         'ONHAND_SETTING_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        # print('getter(self.prefix + name, dflt)->',getter(self.prefix + name, dflt))
        return getter(self.prefix + name, dflt)

    # def _setting(self, name, dflt):
    #     from django.conf import settings
    #     getter = getattr(settings,
    #                      'ALLAUTH_SETTING_GETTER',
    #                      lambda name, dflt: getattr(settings, name, dflt))
    #     print('AppSettings_getter->', getter)
    #     return getter(self.prefix + name, dflt)

    @property
    def AUTHENTICATION_METHOD(self):
        ret = self.AuthenticationMethod.USERNAME
        return ret

    @property
    def UNIQUE_PERSON(self):
        """
        Enforce uniqueness of person
        """
        return self._setting("UNIQUE_PERSON", True)

    @property
    def USER_MODEL_USERNAME_FIELD(self):
        return self._setting('USER_MODEL_USERNAME_FIELD', 'username')

    @property
    def DEFAULT_COMPANY_PERSON_ROLE(self):
        return self._setting("DEFAULT_COMPANY_PERSON_ROLE", "owner").lower()

    @property
    def DEFAULT_COMPANY_LANGUAGE(self):
        return self._setting("DEFAULT_COMPANY_LANGUAGE", "english").lower()

    @property
    def DEFAULT_PERSON_LANGUAGE(self):
        return self._setting("DEFAULT_PERSON_LANGUAGE", "english").lower()

    @property
    def PERSON_MODEL_FIRSTNAME_FIELD(self):
        return self._setting("PERSON_MODEL_FIRSTNAME_FIELD", "first_name").lower()

    @property
    def ADAPTER(self):
        return self._setting('ADAPTER',
                             'onhand.provider.adapter.DefaultAccountAdapter')

    @property
    def FIRSTNAME_REQUIRED(self):
        """
        The user is required to enter a first name when signing up
        """
        return self._setting("FIRSTNAME_REQUIRED", True)

    @property
    def FIRSTNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("FIRSTNAME_MIN_LENGTH", 3)

    @property
    def LASTNAME_REQUIRED(self):
        """
        The user is required to enter a lastname name when signing up
        """
        return self._setting("LASTNAME_REQUIRED", True)

    @property
    def LASTNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("LASTNAME_MIN_LENGTH", 3)

    @property
    def EMAIL_REQUIRED(self):
        """
        The user is required to hand over an e-mail address when signing up
        """
        return self._setting("EMAIL_REQUIRED", False)

    @property
    def ADAPTER(self):
        return self._setting('ADAPTER',
                             'onhand.provider.adapter.DefaultAccountAdapter')

    @property
    def UNIQUE_EMAIL(self):
        """
        Enforce uniqueness of e-mail addresses
        """
        return self._setting("UNIQUE_EMAIL", True)

    @property
    def TEMPLATE_EXTENSION(self):
        """
        A string defining the template extension to use, defaults to `html`.
        """
        return 'html'
        # return self._setting("TEMPLATE_EXTENSION", 'html')

    @property
    def SIGNUP_FORM_CLASS(self):
        """
        Signup form
        """
        return "'onhand.provider.forms.SignupForm'"
        # return self._setting("SIGNUP_FORM_CLASS", None)


    @property
    def USERNAME_REQUIRED(self):
        """
        The user is required to enter a username when signing up
        """
        return self._setting("USERNAME_REQUIRED", True)

    @property
    def USERNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("USERNAME_MIN_LENGTH", 5)

    @property
    def USERNAME_BLACKLIST(self):
        """
        List of usernames that are not allowed
        """
        return self._setting("USERNAME_BLACKLIST", [])

    @property
    def PASSWORD_INPUT_RENDER_VALUE(self):
        """
        render_value parameter as passed to PasswordInput fields
        """
        return self._setting("PASSWORD_INPUT_RENDER_VALUE", False)

    @property
    def SIGNUP_PASSWORD_ENTER_TWICE(self):
        """
        Signup password verification
        """
        legacy = self._setting('SIGNUP_PASSWORD_VERIFICATION', True)
        return self._setting('SIGNUP_PASSWORD_ENTER_TWICE', legacy)

    @property
    def PASSWORD_MIN_LENGTH(self):
        """
        Minimum password Length
        """
        import django
        from django.conf import settings
        ret = None
        has_validators = (
            django.VERSION[:2] >= (1, 9) and
            bool(getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])))
        if not has_validators:
            ret = self._setting("PASSWORD_MIN_LENGTH", 6)
        return ret

    @property
    def FORMS(self):
        return self._setting('FORMS', {})



# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa
app_settings = AppSettings('PROVIDER_')
# print('__name__',__name__)
app_settings.__name__ = __name__
# print('app_settings ->',app_settings.TEMPLATE_EXTENSION)
sys.modules[__name__] = app_settings
# print('app_settings ->',app_settings.TEMPLATE_EXTENSION)
# print('app_settings->',app_settings)
