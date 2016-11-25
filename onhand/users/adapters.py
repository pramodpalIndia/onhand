# -*- coding: utf-8 -*-
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from onhand.management.models import Role
from onhand.users.utils import user_username, user_field


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        # from .utils import user_username, user_email, user_field

        data = form.cleaned_data
        username = data.get('username')
        if username:
            user_username(user, username)

        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        if(form == 'onhand.provider.forms.SignupForm'):
            user_field(user, 'role_code', Role.objects.get(pk='custom'))



        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)

        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user
