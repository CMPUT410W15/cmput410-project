from django.shortcuts import render, render_to_response, redirect
from models import *
from common.util import post_request_to_json
from author.remote import send_remote_friend_request
from django.views.generic.edit import UpdateView
from author.forms import *
from posts.models import PRIVATE, FRIEND, FRIENDS, FOAF, PUBLIC, SERVERONLY
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.http import HttpResponseRedirect

def friends(request):
    me = Author.objects.get(user=request.user)
    authors = Author.objects.all()
    friends = me.get_friends()
    following = list(set(me.get_followees()) - set(friends))
    friend_requests = list(set(me.get_friend_requests()) - set(friends))
    not_friends = list(
        set(authors) - set(friends) - set(following) - set(friend_requests) -
        set([me])
    )

    return render(
        request,
        'friends.html',
        {
            "friends": friends,
            "following": following,
            "friend_requests": friend_requests,
            "not_friends": not_friends,
        }
    )

def befriend(request, uid):
    me = Author.objects.get(user=request.user)
    other = Author.objects.get(uid=uid)
    me.befriend(other)

    if other.user == None:
        send_remote_friend_request(me, other)

    return redirect('/friends/')

def unbefriend(request, uid):
    me = Author.objects.get(user=request.user)
    me.unfollow(Author.objects.get(uid=uid))
    return redirect('/friends/')

def follow(request, uid):
    me = Author.objects.get(user=request.user)
    me.follow(Author.objects.get(uid=uid))
    return redirect('/friends/')

def unfollow(request, uid):
    me = Author.objects.get(user=request.user)
    me.unfollow(Author.objects.get(uid=uid))
    return redirect('/friends/')


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['github', 'picture']
    template_name_suffix = '_update_form'

#Konrad's old edit function
# def edit(request):
#     me = Author.objects.get(user=request.user)
#     if 'email' in request.POST:
#         request.user.email = request.POST['email']
#         request.user.save()
#     if 'github' in request.POST:
#         me.github = request.POST['github']
#         me.save()
#     return redirect('/home')

@csrf_protect
def edit(request):
    me= Author.objects.get(user=request.user)
    me_as_user= request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            #Update the user's email and author github
            email=form.cleaned_data['email']
            me_as_user.email=email
            me_as_user.save()

            github= form.cleaned_data['github']
            me.github=github

            if 'picture' in request.FILES:
                picture = Image.objects.create(
                    image = request.FILES['picture'],
                    visibility=PUBLIC, 
                    )
                picture.save()
            else:
                picture= None

            me.picture=picture
            me.save()
                
            return HttpResponseRedirect('/home')
    else:
        form= UserUpdateForm()

    variables = RequestContext(request, { 'form': form, 'email':request.user.email, 'github':me.github, 'author':me, })
    return render_to_response('author_update_form.html',
        variables,
        )
    
