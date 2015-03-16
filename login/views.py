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
from posts.models import PRIVATE, FRIEND, FRIENDS, FOAF, PUBLIC, SERVERONLY
from posts.forms import *
@csrf_protect
def register(request):
    #Create both a user and an author every time someone registers
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email'],
            )
            user.is_active = False
            user.save()
            author= Author(user=user)
            author.vetted = False
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
def home(request, vars=None):
    #Note: attributes passed in here are all lowercase regardless of capitalization
    posts = Post.objects.all()
    author = request.user.author
    friends = [f for f in author.get_friends()]
    fof_dict = author.get_friends_of_friends()

    #Get everyone's public posts and get the posts from friends they received
    public_posts = [p for p in posts if p.visibility == PUBLIC]
    private_posts = [p for p in author.get_posts(visibility=PRIVATE)]
    to_me_posts = [p for p in author.get_received_posts()]

    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    for post in posts_to_friends:
        if post.send_author in author.get_friends() or post.send_author == author:
            friends_posts.append(post)

    foaf_posts = []
    for p in [p for p in posts if p.visibility == FOAF]:
        foaf = any([(p.send_author in fof) for fof in fof_dict.values()])
        if p.send_author in fof_dict.keys() or foaf:
            foaf_posts.append(p)

    all_posts = set(public_posts + private_posts + to_me_posts +
                    friends_posts + foaf_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

    #If there were no errors in commenting
    if vars == None:
        form= CommentForm()
    else:
        form= vars['form']
    #form= CommentForm()
    return render(request,
                  'home.html',
                  {
                      'user': request.user,
                      'author': request.user.author,
                      'posts': all_posts,
                      'form': form,
                  })
