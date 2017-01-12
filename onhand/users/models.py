from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager, Group, Permission
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from onhand.management.models import Role, UserPreferenceType
from onhand.subscription.models import CompanyPersonRole, Subscription
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models.manager import EmptyManager
from django.utils import six, timezone
from django.utils.deprecation import CallableFalse, CallableTrue
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .validators import ASCIIUsernameValidator, UnicodeUsernameValidator


def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
user_logged_in.connect(update_last_login)



class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,db_column='user_name',
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'), db_column='user_is_staff',
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.CharField(
        _('active'), db_column='user_is_active',max_length=1,
        default='Y',
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    # date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table='oh_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

@python_2_unicode_compatible
class User(AbstractUser):
    id = models.AutoField(primary_key=True,default=1,db_column='user_id')
    password = models.CharField(max_length=2000, db_column='user_password', verbose_name=('password'))
    role_code = models.ForeignKey(Role, models.DO_NOTHING, db_column='role_code',
                                  verbose_name=('role'),default='custom')
    cprs_id = models.ForeignKey(CompanyPersonRole, models.DO_NOTHING,db_column='cprs_id', verbose_name=('companypersonrole'),default=1)
    user_security_question1 = models.CharField(max_length=60, blank=True, null=True, verbose_name=('question1'))
    user_security_answer1 = models.CharField(max_length=20, blank=True, null=True, verbose_name=('answer1'))
    user_security_question2 = models.CharField(max_length=60, blank=True, null=True, verbose_name=('question2'))
    user_security_answer2 = models.CharField(max_length=20, blank=True, null=True, verbose_name=('answer2'))
    user_security_question3 = models.CharField(max_length=60, blank=True, null=True, verbose_name=('question3'))
    user_security_answer3 = models.CharField(max_length=20, blank=True, null=True, verbose_name=('answer3'))
    user_last_logon_date = models.DateTimeField(blank=True, null=True, verbose_name=('lastlogon'),default=timezone.now)
    user_password_change_date = models.DateTimeField(blank=True, null=True, verbose_name=('passwordreset'),default=timezone.now)


@python_2_unicode_compatible
class AnonymousUser(object):
    id = None
    pk = None
    username = ''
    # is_staff = False
    is_active = False
    is_superuser = False
    _groups = EmptyManager(Group)
    _user_permissions = EmptyManager(Permission)

    def __init__(self):
        pass

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def save(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def delete(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def set_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def check_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def _get_groups(self):
        return self._groups
    groups = property(_get_groups)

    def _get_user_permissions(self):
        return self._user_permissions
    user_permissions = property(_get_user_permissions)

    def get_group_permissions(self, obj=None):
        return set()

    # def get_all_permissions(self, obj=None):
    #     return _user_get_all_permissions(self, obj=obj)
    #
    # def has_perm(self, perm, obj=None):
    #     return _user_has_perm(self, perm, obj=obj)
    #
    # def has_perms(self, perm_list, obj=None):
    #     for perm in perm_list:
    #         if not self.has_perm(perm, obj):
    #             return False
    #     return True
    #
    # def has_module_perms(self, module):
    #     return _user_has_module_perms(self, module)

    @property
    def is_anonymous(self):
        return CallableTrue

    @property
    def is_authenticated(self):
        return CallableFalse

    def get_username(self):
        return self.username


class UserPreference(models.Model):
    from onhand.users.models import User
    uprf_id = models.AutoField(primary_key=True, db_column='uprf_id', verbose_name=('UserPreferencId'))
    user = models.ForeignKey(User, models.DO_NOTHING, verbose_name='User')
    uprt_code = models.ForeignKey(UserPreferenceType, models.DO_NOTHING, db_column='uprt_code', verbose_name='UserPreferenceType')
    uprf_value = models.CharField(max_length=40, verbose_name='UserPreferenceValue')

    def __str__(self):
        return "%s / %s " % (self.user, self.uprt_code)

    class Meta:
        db_table = 'oh_user_preference'
        verbose_name = "UserPreference"
        verbose_name_plural = "UserPreferences"
