from django.contrib.auth.models import User
from django import forms


class SignupForm(forms.Form):
    """
    Форма регистрации
    """

    username = forms.CharField(max_length=30, label='Логин',
                               help_text='Логин должен состоять не более чем из 30 сиволов',
                               widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'email@domain.com'}),
                             label='Email', help_text='Введите Ваш e-mail')

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='Пароль',
                               help_text='Пароль должен содержать минимум 4 символа')

    password_check = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
                                     label='Пароль',
                                     help_text='Пароль должен состоять не меньше чем из 4 символов')

    def clean_username(self):
        """
        Проверка логина пользователя

        Логин обязательно должен быть больше 4 символов
        :return: логин
        """

        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Имя занято', code='username_already_used')
        return self.cleaned_data['username']

    def clean_password(self):
        """
        Проверка пароль

        Пароль обязательно должен быть больше 4 символов
        :return: пароль
        """

        if len(self.cleaned_data['password']) < 4:
            raise forms.ValidationError('Длинна пароля меньше 4 символов', code='password_is_short')
        return self.cleaned_data['password']

    def clean_email(self):
        """
        Проверка e-mail

        E-mail обязательно должен быть уникальным
        :return: e-mail
        """

        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('Данный email уже используется', code='email_is_already_used')
        return self.cleaned_data['email']

    def clean(self):
        """
        Общая проверка

        Пароли обязательно должны совпадать
        """

        cd = self.cleaned_data
        password = cd.get('password')
        password_check = cd.get('password_check')

        if password and password_check and password != password_check:
            raise forms.ValidationError('Введенные пароли не совпадают', code='passwords_dont_match')

    def save(self):
        """
        При корректности всей информации происходит сохранение
        :return: созданный пользователь
        """

        cd = self.cleaned_data
        user = User.objects.create_user(cd['username'], password=cd['password'], email=cd['email'])
        user.save()

        return user


class LoginForm(forms.Form):
    """
    Форма авторизации
    """

    username = forms.CharField(max_length=30, label='Логин',
                               help_text='Логин должен состоять не более чем из 30 сиволов',
                               widget=forms.TextInput(attrs={'placeholder': 'Логин'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='Пароль',
                               help_text='Пароль должен содержать минимум 4 символа')

    def clean_username(self):
        """
        Проверка логина

        Логин обязательно должен существовать (очевидно...)
        :return: логин
        """

        try:
            user = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователь с таким именем не существует',
                                        code='user_doesnt_exist')

        if not user.is_active:
            raise forms.ValidationError('Пользователь не активирован',
                                        code='user_not_active')

        return self.cleaned_data['username']


class ProfileSettingsForm(forms.Form):
    """
    Форма изменения информации аккаунта - пароля
    """

    username = forms.CharField(max_length=30, label='Логин', widget=forms.TextInput(attrs={'readonly': True}))

    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'readonly': True}))

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='Пароль',
                                   help_text='Пароль должен содержать минимум 4 символа')

    new_password_check = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), label='Пароль',
                                         help_text='Пароль должен содержать минимум 4 символа')

    def __init__(self, user, *args, **kwargs):
        """
        Инициализация объекта формы
        :param user: пользователь из запроса
        """

        super(ProfileSettingsForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean(self):
        """
        Общая проверка

        Новые пароли обязательно должны совпадать
        """

        cd = self.cleaned_data
        new_password = cd.get('new_password')
        new_password_check = cd.get('new_password_check')

        if new_password and new_password_check and new_password != new_password_check:
            raise forms.ValidationError('Введенные пароли не совпадают', code='passwords_dont_match')

    def save(self):
        """
        Установка нового пароля и сохранение в БД
        """

        cd = self.cleaned_data
        new_password = cd['new_password']

        self.user.set_password(new_password)
        self.user.save()

        return self.user
