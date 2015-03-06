from django.shortcuts import render

# Create your views here.
### Source material taken from:
###		https://mayukhsaha.wordpress.com/2013/05/09/simple-login-and-user-registration-application-using-django/
### 	March 2, 2015
### No explicit license 
from login.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from author.models import Author
from posts.models import Post
@csrf_protect
def register(request):
    #Create both a user and an author every time someone registers
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            author= Author(user=user)
            author.save()
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })
 
    return render_to_response(
    'registration/register.html',
    variables,
    )
 
def register_success(request):
    return render_to_response(
    'registration/success.html',
    )
 
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
 
@login_required
def home(request):
    #Note: attributes passed in here are all lowercase regardless of capitalization
    posts= Post.objects.all()
    return render(request,
    'home.html',
    { 'user': request.user , 'author': request.user.author, 'posts':posts}
    )
