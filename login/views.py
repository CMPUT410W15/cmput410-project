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
from author.remote import reset_remote_authors
from posts.remote import reset_remote_posts

import json
import requests
import unicodedata
from datetime import datetime
from dateutil import tz

@csrf_protect
def register(request):
    #Create both a user and an author every time someone registers
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email'],
            )
            user.is_active = False
            user.save()

            #Create author object with user=current user and host being team 8
            #if an account is created on our server
            author= Author(user=user,host='team8')
            #Assuming that the profile picture should have public visibility
            if 'picture' in request.FILES:
                image = Image.objects.create(image = request.FILES['picture'],
                visibility=PUBLIC)
                image.save()
            else:
                image= None
            author.picture=image   
            author.save()
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form,
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

    #Only if you are viewing your own page can you see your profile picture.
    view_picture=False
    if viewer==author:
        if author.has_picture():
            view_picture=True

    return render(request,
                  'authorhome.html',
                  {
                      'user': author.user.username if author.user else author.displayname,
                      'email': author.user.email if author.user else None,
                      'author': request.user.author,
                      'posts': posts,
                      'view_picture':view_picture,
                  })

def personal_stream(request):
    #Doesn't show all posts, just the posts an author is 'interested in'
    #Assumed to be your github activity/stream,
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

    #Github stuff here
    github_username=author.github

    #If there is a github username, try and get their github activity.
    if github_username!="":
        activity=get_github_activity(github_username)
        #If retrieving github activity was successful, pass it to the template
        if activity !=None:
            return render(request,
              'home.html',
              {
                  'user': request.user,
                  'author': request.user.author,
                  'posts': posts,
                  'form': form,
                  'global_stream':global_stream_toggle,
                  'github_activity':activity,
              })
        else:
            return render(request,
              'home.html',
              {
                  'user': request.user,
                  'author': request.user.author,
                  'posts': posts,
                  'form': form,
                  'global_stream':global_stream_toggle,
              })     

    #If there's no github username, don't bother.
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

'''Used to convert github time to local time'''
def convert_git_time(github_time):
    #Get the time at which you pushed to github, normalize and convert it to your local time
    time=unicodedata.normalize("NFKD",github_time).encode("ascii","ignore")
    new_time=time.split("T")
    new_time= new_time[0]+" "+new_time[1][0:-1]
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone to current time zone
    the_time = utc.astimezone(to_zone)
    the_time= the_time.strftime("%B %d, %Y, %I:%M%p")

    return the_time


'''
There are 25 events, not gonna support all of them cause that's too much. Only cover the most used/relevant ones.
Supporting these 8 events because they seem like the most common ones and we are team 8: 
IssueCommentEvent, PullRequestEvent, PushEvent, CreateEvent, DeleteEvent, 
IssuesEvent, GollumEvent, PullRequestReviewCommentEvent.
'''
def get_github_activity(github_username):

    #The URL for to get github activity from 
    url="https://api.github.com/users/"+github_username+"/events"

    #Get all the events pertaining to a user's github URL 
    req= requests.get(url)
    all_events= req.json()

    status_code=req.status_code

    #If status code isn't 200, some error happened. Return activity as None
    if status_code!=200:
        activity=None
        return activity

    #Put all github activity in this array
    activity=[]
    for event in all_events:

        #The 'payload' of every event object
        payload=event["payload"]

        #The repository name of every event object
        repo_name=event["repo"]["name"]
        repo_name= unicodedata.normalize('NFKD', repo_name).encode('ascii','ignore')

        #Covers push events in github activity. Won't put the various commit messages here because there could
        #be up to 20 commits per push event as documented in the events API.
        if event["type"] == "PushEvent":
            #Get the branch you pushed to
            branch= event["payload"]["ref"]

            #Get branch name by doing this because "ref" is seemingly always in this format: "refs/heads/Your_branch_name_here",
            branch=branch[11:]
            branch=unicodedata.normalize('NFKD', branch).encode('ascii','ignore')

            #Get the time at which you pushed to github, normalize and convert it to your local time
            time=event["created_at"]
            the_time=convert_git_time(time)
            info= "("+ the_time +")"+ ": "+github_username +" pushed to "+branch+" at " + repo_name
            activity.append(info)

        #Covers IssueCommentEvents, need to fix the case where there are pictures embedded in the comments body and all
        elif event["type"]=="IssueCommentEvent":

            #Get the issue number
            issue= payload["issue"]
            issue_number= issue["number"]

            #Get the contents of a comment aka the body
            comment=payload["comment"]
            body= comment["body"]
            body= unicodedata.normalize('NFKD', body).encode('ascii','ignore')

            #Get the time at which you pushed to github, normalize and convert it to local time
            time=comment["updated_at"]
            the_time=convert_git_time(time)
            
            info= "("+the_time+"): "+ github_username+ " commented on issue "+str(issue_number)+ " for " +repo_name + " : " + body
            #Note to self: Apply html to markdown thing on the body later. Might just work
            activity.append(info)


        elif event["type"]== "PullRequestEvent":
            #Get the pull request number
            number=payload["number"]

            #Get the action associated with the pull request
            action=payload["action"]
            action= unicodedata.normalize('NFKD', action).encode('ascii','ignore')

            #Only handle the case where action is 'synchronize' just for grammar's sake
            if action=="synchronize":
                action="synchronized"

            #Get title of the pull request
            title=payload["pull_request"]["title"]
            title= unicodedata.normalize('NFKD', title).encode('ascii','ignore')

            #Get the potentially empty body of the pull request event
            body=payload["pull_request"]["body"]
            body= unicodedata.normalize('NFKD',body).encode('ascii','ignore')

            #Get the time of the pull request, normalize and convert it to local timezone
            time=payload["pull_request"]["updated_at"]
            the_time=convert_git_time(time)

            #Check if a comment exists for the pull request action- if not, just show the title of the pull request.
            if body == "":
                info= "("+ the_time +")"+ ": "+github_username +" "+action+" pull request " +str(number)+ " for "+repo_name+" : "+title
            else:
                info= "("+ the_time +")"+ ": "+github_username +" "+action+" pull request " +str(number)+ " for "+repo_name+" : "+title+" - "+body

            activity.append(info)

        elif event["type"]=="CreateEvent":
            #Get ref_type because it holds what you created - a branch, repo, whatever.
            ref_type= payload["ref_type"]
            ref_type=unicodedata.normalize('NFKD',ref_type).encode('ascii','ignore')

            #Get ref because it holds the name of what you created. Don't need to normalize this?
            ref= payload["ref"]
            #ref= unicodedata.normalize('NFKD',created).encode('ascii','ignore')

            #Get the time, normalize it and convert it to local timezone
            time= event["created_at"]
            the_time=convert_git_time(time)
            
            info="("+the_time+")" +": "+github_username+" created "+ref_type+" "+ref+" at "+repo_name
            activity.append(info)

        elif event["type"]=="PullRequestReviewCommentEvent":
            #Get the pull request number
            number=payload["pull_request"]["number"]

            comment=payload["comment"]
            #Body of a comment cannot be blank so don't need to handle that case
            body=comment["body"]
            body= unicodedata.normalize('NFKD',body).encode('ascii','ignore')

            #Get the time, normalize it and convert it to local timezone
            time= comment["updated_at"]
            the_time=convert_git_time(time)
            info="("+the_time+")" +": "+github_username+" commented on pull request #" +str(number) +" at " +repo_name+": "+body
            activity.append(info)

        elif event["type"]== "IssuesEvent":
            #Get the issue number
            issue= payload["issue"]
            number=issue["number"]

            #Get the action associated with the issue
            action=payload["action"]
            action=unicodedata.normalize('NFKD',action).encode('ascii','ignore')

            #Get title of the issue
            title=issue["title"]
            title= unicodedata.normalize('NFKD', title).encode('ascii','ignore')

            # Don't need body
            # body=issue["body"]
            # body= unicodedata.normalize('NFKD',body).encode('ascii','ignore')

            time= issue['updated_at']
            the_time=convert_git_time(time)
            info= "("+ the_time + ")" + ": " +github_username+ " " + action +" issue #"+ str(number) + " at "+repo_name+ " : " + title
            activity.append(info)

        elif event["type"]=="DeleteEvent":
            #Get the name of what was deleted
            ref=payload['ref']
            ref= unicodedata.normalize('NFKD',ref).encode('ascii','ignore')

            #Get what was deleted - a branch, whatever.
            ref_type=payload['ref_type']
            ref_type=unicodedata.normalize('NFKD',ref_type).encode('ascii','ignore')

            #Get the time, normalize and convert it to local timezone
            time= event["created_at"]
            the_time=convert_git_time(time)
            info="("+the_time+")" + ": "+ github_username+" deleted " +ref_type+" "+ref+" at "+ repo_name
            activity.append(info)

        elif event["type"]== "GollumEvent":

            #Get the page referred to in the pages object
            pages=payload["pages"][0]

            #Get the action associated with the event
            action=pages["action"]
            action= unicodedata.normalize('NFKD',action).encode('ascii','ignore')

            #Get title of the wiki page
            title=pages['title']
            title= unicodedata.normalize('NFKD',title).encode('ascii','ignore')

            #Get the time, normalize and convert to local timezone
            time= event["created_at"]
            the_time=convert_git_time(time)
            info="("+the_time+")" +": "+github_username+ " "+action+ " page "+title+" of the " +repo_name +" wiki."
            activity.append(info)

        #If the event is not of the 8 types above, don't do anything for it. Just skip it
        else:
            continue

    return activity

