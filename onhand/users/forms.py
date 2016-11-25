
from allauth.account.forms import BaseSignupForm


class RegistrationForm(BaseSignupForm):
    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        pass
