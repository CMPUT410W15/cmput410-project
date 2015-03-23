from django.shortcuts import render, render_to_response, redirect
from models import *
from common.util import get_request_to_json, get_nodes

def friends(request):

    for node in get_nodes():
        for author in get_request_to_json(node.url + 'authors'):
            a = {'uid': author['id'],
                 'displayname': author['displayname'],
                 'host': author['host']}
            Author.objects.get_or_create(**a)

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
    me.befriend(Author.objects.get(uid=uid))
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
