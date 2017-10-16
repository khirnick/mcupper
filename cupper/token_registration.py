from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenRegistration(PasswordResetTokenGenerator):
    """
    Класс для получения токена регистрации для активации аккаунта
    """
    pass


token_registration = TokenRegistration()
