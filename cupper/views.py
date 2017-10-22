from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from cupper.forms import SignupForm, LoginForm, ProfileSettingsForm
from cupper.models import Profile, News
from cupper.token_registration import token_registration


def signup(request):
    """
    Вьюха регистрации

    При корректности всей введенной информации происходит занесение пользователя
    в БД с параметром 'is_active' = False
    Высылается e-mail на указанный почтовый адрес для активации аккаунта
    :param request: запрос
    :return: перенаправление / рендер формы регистрации
    """

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            our_site = get_current_site(request)
            activation_token = token_registration.make_token(user)

            message_to_send = render_to_string('cupper/signup_message.html', {
                'user': user,
                'domain': our_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': activation_token
            })

            message_subject = 'Активация аккаунта'
            email_address = form.cleaned_data.get('email')

            email = EmailMessage(message_subject, message_to_send, to=[email_address])
            email.send()

            return HttpResponseRedirect('/signup_success')

    else:
        form = SignupForm()

    return render(request, 'cupper/signup.html', {'form': form})


def signup_success(request):
    """
    Вьюха успешной регистрации
    :param request: запрос
    :return: рендер страницы
    """

    return render(request, 'cupper/signup_success.html')


def activate(request, uidb64, token):
    """
    Вьюха активации

    Происходит активации по токену и id пользователя (в кодировке base64) в URL
    :param request: запрос
    :param uidb64: id пользователя в base64 кодировке
    :param token: токен регистрации
    :return: рендер страницы успешной регистрации/неуспешной регистрации
    """

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_registration.check_token(user, token):
        user.is_active = True
        user.save()

        return redirect('/activation_success')
    else:
        return render(request, 'cupper/activation_bad_token.html')


def activation_success(request):
    """
    Вьюха успешной активации
    :param request: запрос
    :return: рендер страницы успешной активации
    """

    return render(request, 'cupper/activation_success.html')


def index(request):
    """
    Вьюха главной страницы
    :param request: запрос
    :return: рендер главной страницы
    """

    return render(request, 'cupper/index.html')


def do_login(request):
    """
    Вьюха страницы авторизации
    :param request: запрос
    :return: рендер главной страницы при успешной авторизации / рендер логин страницы при неудаче
    """

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            auth.login(request, user)

            return HttpResponseRedirect('/')
        else:
            pass
    else:
        form = LoginForm()

        print(form.errors)

    return render(request, 'cupper/login.html', {'form': form})


def logout(request):
    """
    Вьюха логаута
    :param request: запрос
    :return: рендер главной страницы
    """

    auth.logout(request)
    return HttpResponseRedirect('/')


def profile(request):
    """
    Вьюха профиля

    Вывод информации о профиле
    :param request: запрос
    :return: рендер страницы профиля
    """

    return render(request, 'cupper/profile.html')


def profile_settings(request):
    """
    Вьюха страницы изменения пароля пользователя

    :param request: запрос
    :return: рендер страницы для изменения информации / рендер страницы с информацией о успешном
    изменении пароль
    """

    user = request.user
    default_form_when_password_changed = ProfileSettingsForm(user, initial={'email': user.email,
                                                                            'username': user.username})

    if request.method == "POST":
        form = ProfileSettingsForm(user, request.POST)
        if form.is_valid():
            form.save()

            auth.login(request, user)

            return render(request, 'cupper/profile_settings.html', {'form': default_form_when_password_changed,
                                                                    'if_password_changed': 'Пароль успешно изменен'})
    else:
        form = ProfileSettingsForm(user, initial={'email': user.email, 'username': user.username})

    return render(request, 'cupper/profile_settings.html', {'form': form})


def game_rules(request):
    return render(request, 'cupper/game_rules.html')


def best(request):
    best_users = Profile.get_best_users()
    print(best_users)

    return render(request, 'cupper/best.html', {'best_users': best_users})


def news(request):
    news_list = News.get_news_by_relevance()
    paginator = Paginator(news_list, 2)

    page = request.GET.get('page')
    try:
        news_current = paginator.page(page)
    except PageNotAnInteger:
        news_current = paginator.page(1)
    except EmptyPage:
        news_current = paginator.page(paginator.num_pages)

    return render(request, 'cupper/news.html', {'news_list': news_current})