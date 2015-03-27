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

from author.models import Author
from posts.models import Post
from posts.models import PRIVATE, FRIEND, FRIENDS, FOAF, PUBLIC, SERVERONLY
from posts.forms import *
from posts.remote import reset_remote_posts
from author.remote import reset_remote_authors

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from posts.remote import reset_remote_posts
from author.remote import reset_remote_authors

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
    #Note: attributes passed in here are all lowercase regardless of capitalization
    if request.user.is_superuser:
        return HttpResponseRedirect("/accounts/login/")
    elif '/accounts/login' in request.META['HTTP_REFERER']:
        reset_remote_authors()
        reset_remote_posts()

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

    #Get server posts
    server_posts=[p for p in posts if p.visibility==SERVERONLY]
    all_posts = set(public_posts + private_posts + to_me_posts +
                    friends_posts + foaf_posts+server_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

    form= CommentForm()
    personal_stream_toggle=True
    paginator= Paginator(all_posts,8) #Show 8 posts per page
    page= request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger: #If page isn't an integer deliver the first page
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
    author = Author.objects.get(uid=authorpage)
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
    except PageNotAnInteger:#If page isn't an integer deliver the first page
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)

    return render(request,
                  'authorhome.html',
                  {
                      'user': author.user.username if author.user else author.displayname,
                      'email': author.user.email if author.user else None,
                      'author': request.user.author,
                      'posts': posts,
                  })

def personal_stream(request):
    #Doesn't show all posts, just the posts an author is 'interested in'
    #Assumed to be your github activity/stream (to be done later), 
    #friends posts (both FRIENDS and PUBLIC visibilities), FOAF posts, private posts
    #Also includes public/server posts of the people an author is following.
    #Doesn't include public posts/server posts otherwise.

    posts= Post.objects.all()
    author = request.user.author
    friends = [f for f in author.get_friends()]
    fof_dict = author.get_friends_of_friends()

    #Get private posts 
    private_posts = [p for p in author.get_posts(visibility=PRIVATE)]

    #This part is rendered invalid by the coming change in post model 
    to_me_posts = [p for p in author.get_received_posts()]

    #Get posts you made regardless of visibility.
    by_me_posts= [p for p in author.get_posts()]

    #Get posts made by friends with visibility=FRIENDS
    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    for post in posts_to_friends:
        if post.send_author in author.get_friends():
            friends_posts.append(post)

    #Get posts made by friends with visibility=PUBLIC
    public_posts= [p for p in posts if p.visibility==PUBLIC]
    public_by_friends=[]
    for post in public_posts:
        if post.send_author in author.get_friends():
            public_by_friends.append(post)

    #Get FOAF posts
    foaf_posts = []
    for p in [p for p in posts if p.visibility == FOAF]:
        foaf = any([(p.send_author in fof) for fof in fof_dict.values()])
        if p.send_author in fof_dict.keys() or foaf:
            foaf_posts.append(p)

    #Get posts made by you/friends with visibility=SERVER
    all_server_posts=[p for p in posts if p.visibility==SERVERONLY]
    server_posts=[]
    for post in all_server_posts:
        if post.send_author in author.get_friends() or post.send_author==author:
            server_posts.append(post)


    #Get the people that you are following and get their public/server posts.
    #Presumably you shouldn't see their friends, private and foaf posts.
    following_posts=[]
    following= author.get_followees()
    for person in following:
        posts_public= person.get_posts(visibility=PUBLIC)
        posts_server= person.get_posts(visibility=SERVERONLY)
        for post in posts_public:
            following_posts.append(post)
        for post in posts_server:
            following_posts.append(post)


    all_posts = set(private_posts + friends_posts + foaf_posts + to_me_posts + by_me_posts + public_by_friends+server_posts+following_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

    #Have a toggle/button to go back to the global stream
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

def personal_stream_friends(request):
    #Get friends posts (ones made by friends) only
    #Has friends, public, FOAF and serveronly

    posts= Post.objects.all()
    author = request.user.author
    friends = [f for f in author.get_friends()]

    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    for post in posts_to_friends:
        if post.send_author in author.get_friends():
            friends_posts.append(post)

    #Get posts made by friends with visibility=PUBLIC
    public_posts= [p for p in posts if p.visibility==PUBLIC]
    #print(public_posts)
    public_by_friends=[]
    for post in public_posts:
        if post.send_author in author.get_friends():
            public_by_friends.append(post)

    #Get FOAF posts your friends made
    fof_dict = author.get_friends_of_friends()
    foaf_posts = []
    for p in [p for p in posts if p.visibility == FOAF]:
        foaf = any([(p.send_author in fof) for fof in fof_dict.values()])
        if p.send_author in fof_dict.keys() or foaf:
            #Only get FOAF posts that you didn't make and were made
            #only by your friends
            if p.send_author != author and p.send_author in author.get_friends():
                foaf_posts.append(p)

    #Get posts made by friends with visibility=SERVER
    server_posts=[p for p in posts if p.visibility==SERVERONLY]
    server_by_friends=[]
    for post in server_posts:
        if post.send_author in author.get_friends():
            server_by_friends.append(post)

    all_posts = set(friends_posts+public_by_friends+foaf_posts+server_by_friends)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

    #Have a toggle to go back to the global newsfeed
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