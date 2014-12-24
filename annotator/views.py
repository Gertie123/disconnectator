from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


@login_required
def dashboard(request):
    return render(request,  'annotator/dashboard.html', {'title': 'Dashboard', 'username': request.user.username})

def thanks(request, token=None):
    if token is not None:
        logout(request)
        login_with_token(request, token)
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(dashboard))
    else:
        return render(request, 'annotator/thanks.html')

# -- Ajax functions -- #

def ajax(request):
    if request.method == 'POST' and request.is_ajax():
        fnc = request.POST['fnc']
        if fnc == 'logout':
            logout(request)
            return HttpResponse()
        elif fnc == 'login':
            login_with_token(request, request.POST['token'])
            return HttpResponse()

    return HttpResponseServerError()

def login_with_token(request, token):
    user = authenticate(username=token, password=token)
    if user is not None and user.is_active:
        login(request, user)
