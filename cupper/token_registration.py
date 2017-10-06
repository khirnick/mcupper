from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenRegistration(PasswordResetTokenGenerator):
    pass


token_registration = TokenRegistration()
