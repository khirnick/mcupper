def include_login_form(request):
    from cupper.forms import LoginForm
    form = LoginForm()
    return {'login_form': form}