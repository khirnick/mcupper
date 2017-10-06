from django.contrib.auth.models import User
from django import forms

from cupper.models import Profile


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, label='Логин',
                               help_text='Логин должен состоять не более чем из 30 сиволов',
                               widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'your_email@example.com'}),
                             label='Email', help_text='Введите Ваш e-mail')

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='Пароль',
                               help_text='Пароль должен содержать минимум 4 символа')

    password_check = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
                                     label='Пароль',
                                     help_text='Пароль должен состоять не меньше чем из 4 символов')

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Имя занято', code='username_already_used')
        return self.cleaned_data['username']

    def clean_password(self):
        if len(self.cleaned_data['password']) < 4:
            raise forms.ValidationError('Длинна пароля меньше 4 символов', code='password_is_short')
        return self.cleaned_data['password']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('Данный email уже используется', code='email_is_already_used')
        return self.cleaned_data['email']

    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        password_check = cd.get('password_check')

        if password and password_check and password != password_check:
            raise forms.ValidationError('Введенные пароли не совпадают', code='passwords_dont_match')

    def save(self):
        cd = self.cleaned_data
        user = User.objects.create_user(cd['username'], password=cd['password'], email=cd['email'])
        user.save()

        return user
