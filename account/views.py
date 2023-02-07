from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginFrom
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def dashboard(request):
    template_name = 'account/dashboard.html'
    context = {'section': 'dashboard'}
    return render(request, template_name, context)


def user_login(request):
    template_name = 'account/login.html'
    if request.method == 'POST':
        form = LoginFrom(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginFrom()
    context = {'form': form}
    return render(request, template_name, context)
