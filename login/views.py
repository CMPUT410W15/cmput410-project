from django.shortcuts import render

# Create your views here.
### Source material taken from:
###		https://mayukhsaha.wordpress.com/2013/05/09/simple-login-and-user-registration-application-using-django/
### 	March 2, 2015
### No explicit license
from login.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from author.models import Author, reset_foreign_authors
from posts.models import Post
from posts.models import PRIVATE, FRIEND, FRIENDS, FOAF, PUBLIC, SERVERONLY
from posts.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    if '/accounts/login' in request.META['HTTP_REFERER']:
        reset_foreign_authors()

    #Note: attributes passed in here are all lowercase regardless of capitalization
    if request.user.is_superuser:
        return HttpResponseRedirect("/accounts/login/")
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

    form= CommentForm()
    personal_stream_toggle=True

    paginator= Paginator(all_posts,8) #Show 8 posts per page 
    page= request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        #If page isn't an integer deliver the first page
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)

    return render(request,
                  'home.html',
                  {
                      'user': request.user,
                      'author': request.user.author,
                      'posts': posts,
                      'form': form,
                      'personal_stream':personal_stream_toggle,
                  })

def authorhome(request, authorpage):
    #Who is viewing their page?
    viewer = request.user.author
    whose = User.objects.get(username=authorpage)
    author = User.objects.get(username=authorpage).author
    #Note: attributes passed in here are all lowercase regardless of capitalization
    posts = set()
    for post in Post.objects.all():
        if (post.send_author == author):
            posts.add(post)

    #friends = [f for f in author.get_friends()]
    friends = 0
    for f in author.get_friends():
        if (viewer == f):
            friends = 1

    #Get everyone's public posts and get the posts from friends they received
    public_posts = [p for p in posts if p.visibility == PUBLIC]
    if (viewer == author):
        private_posts = [p for p in author.get_posts(visibility=PRIVATE)]
        to_me_posts = [p for p in author.get_received_posts()]
    else:
        private_posts = list()
        to_me_posts = list()

    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    if (friends == 1) or (viewer==author):
        friends_posts = posts_to_friends

    foaf_posts = []
    ###TODO: FOAF *could* be implemented for an author's home page
    ### But currently I think it should just be posts made by that author.

    all_posts = set(public_posts + friends_posts + private_posts + to_me_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

    #Added pagination to the author page as well
    paginator= Paginator(all_posts,8) #Show 8 posts per page 
    page= request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        #If page isn't an integer deliver the first page
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)


    return render(request,
                  'authorhome.html',
                  {
                      'user': authorpage,
                      'email': whose.email,
                      'author': request.user.author,
                      'posts': posts,
                  })

def personal_stream(request):
    #Don't show all posts here, just the posts an author is 'interested in'
    #Assumed to be your github activity/stream (for later), friends posts, FOAF posts, private posts and posts they received
    #Does not include public posts/server posts

    posts= Post.objects.all()
    author = request.user.author

    friends = [f for f in author.get_friends()]
    fof_dict = author.get_friends_of_friends()

    #Get private posts, posts the author received, friends posts and FOAF posts
    private_posts = [p for p in author.get_posts(visibility=PRIVATE)]
    to_me_posts = [p for p in author.get_received_posts()]
    by_me_posts= [p for p in author.get_posts()]

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


    all_posts = set(private_posts + to_me_posts +by_me_posts + friends_posts + foaf_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)
    #print(all_posts)
    global_stream_toggle=True

    paginator= Paginator(all_posts,8) #Show 8 posts per page 
    page= request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        #If page isn't an integer deliver the first page
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)

    form= CommentForm()
    return render(request,
                  'home.html',
                  {
                      'user': request.user,
                      'author': request.user.author,
                      'posts': posts,
                      'form': form,
                      'global_stream':global_stream_toggle,
                  })


