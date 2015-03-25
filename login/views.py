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
    # if '/accounts/login' in request.META['HTTP_REFERER']:
    #     reset_foreign_authors()

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
    #Don't show all posts, just the posts an author is 'interested in'
    #Assumed to be your github activity/stream (for later), 
    #friends posts (PUBLIC and FRIENDS category), FOAF posts, private posts
    #Does not include public posts/server posts

    posts= Post.objects.all()
    author = request.user.author

    friends = [f for f in author.get_friends()]
    fof_dict = author.get_friends_of_friends()

    #Get private posts you made
    private_posts = [p for p in author.get_posts(visibility=PRIVATE)]

    #This part is rendered invalid by change in post model 
    #to_me_posts = [p for p in author.get_received_posts()]

    #Get posts you made regardless of visibility?
    by_me_posts= [p for p in author.get_posts()]

    #Get posts made by friends with visibility=FRIENDS
    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    for post in posts_to_friends:
        if post.send_author in author.get_friends():
            friends_posts.append(post)

    #Get FOAF posts others sent (and probably yourself as well)
    foaf_posts = []
    for p in [p for p in posts if p.visibility == FOAF]:
        foaf = any([(p.send_author in fof) for fof in fof_dict.values()])
        if p.send_author in fof_dict.keys() or foaf:
            foaf_posts.append(p)

    #TODO: Need posts made by friends with visibility=PUBLIC, should be done
    public_posts= [p for p in posts if p.visibility==PUBLIC]
    print(public_posts)
    public_by_friends=[]
    for post in public_posts:
        if post.send_author in author.get_friends():
            public_by_friends.append(post)

    all_posts = set(private_posts + friends_posts + foaf_posts + by_me_posts + public_by_friends)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)
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
    #Get friends posts (ones by friends) only

    posts= Post.objects.all()
    author = request.user.author
    friends = [f for f in author.get_friends()]
    friends_posts = []
    posts_to_friends = [p for p in posts if p.visibility == FRIENDS]
    for post in posts_to_friends:
        if post.send_author in author.get_friends():
            friends_posts.append(post)

    all_posts = set(friends_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)
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

#Only see FOAF posts (not ones you made that is)
def personal_stream_foaf(request):
    posts= Post.objects.all()
    author = request.user.author

    fof_dict = author.get_friends_of_friends()

    foaf_posts = []
    for p in [p for p in posts if p.visibility == FOAF]:
        foaf = any([(p.send_author in fof) for fof in fof_dict.values()])
        if p.send_author in fof_dict.keys() or foaf:
            #Only get FOAF posts that you didn't make.
            if p.send_author != author:
                foaf_posts.append(p)

    all_posts = set(foaf_posts)
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

#Get the posts for people you are following, which means friends and followees.
#Because being friends=following and friend request=insta follow.
def personal_stream_following(request):
    posts=Post.objects.all()
    author= request.user.author

    #Get the people that you are following and get their public/server posts.
    #Presumably you shouldn't see their friends, private and foaf posts.
    the_posts=[]
    following= author.get_followees()
    for person in following:
        posts= person.get_posts(visibility=PUBLIC)
        for post in posts:
            the_posts.append(post)
    print(the_posts)
    all_posts=set(the_posts)
    all_posts=sorted(all_posts, key=lambda x: x.published, reverse=True)

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

#Get the posts that only you made, regardless of visibility
def personal_stream_me(request):
    author=request.user.author
    by_me_posts= [p for p in author.get_posts()]
    all_posts = set(by_me_posts)
    all_posts = sorted(all_posts, key=lambda x: x.published, reverse=True)

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

