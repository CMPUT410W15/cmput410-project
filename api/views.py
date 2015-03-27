# REST API for socialdistribution
# See documentation at /docs/APIDoc.md

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import serializers
import json

from author.models import *
from posts.models import *

#TODO restrict methods
#TODO ordering
#TODO paging

# Get all posts visible to the currently authenticated user.
def posts(request):
    return HttpResponse(
        json.dumps(
            [
                x.to_dict()
                for x in Post.objects.all()
                if x.visible_to(request.user)
            ]
        )
    )

# Get all posts marked as public on the server.
def public_posts(request):
    return HttpResponse(
        json.dumps(
            [x.to_dict() for x in Post.objects.filter(visibility=PUBLIC)]
        )
    )

# Get all posts by a specific author visible to the currently authenticated user.
def author_posts(request, author_id):
    # check author existence
    try:
        author = Author.objects.get(uid=author_id)
    except:
        return HttpResponseBadRequest('{"message": "No such author"}')

    return HttpResponse(
        json.dumps(
            [
                x.to_dict()
                for x in Post.objects.filter(send_author=author)
                if x.visible_to(request.user)
            ]
        )
    )

# Get a specific single post.
def post(request, post_id):
    # check post existence
    try:
        post = Post.objects.get(uid=post_id)
    except:
        return HttpResponseNotFound('{"message": "No such post"}')

    # check post permissions
    if not post.visible_to(request.user):
        return HttpResponse('{"message": "Authentication Rejected"}', status=401)

    return HttpResponse(json.dumps(post.to_dict()))

# Add a comment to a post.
@csrf_exempt
def comment(request, post_id):
    # check post existence
    try:
        post = Post.objects.get(uid=post_id)
    except:
        return HttpResponseBadRequest('{"message": "No such post"}')

    # check post permissions
    if not post.visible_to(request.user):
        return HttpResponse('{"message": "Authentication Rejected"}', status=401)

    comment = post.add_comment(
        request.user,
        request.body
    )

    # return the comment. Maybe they want the id...
    return HttpResponse(json.dumps(comment.to_dict()), status=201)

# Get all authors on host.
def friends(request):
    return HttpResponse(
        json.dumps(
            [x.to_dict() for x in Author.objects.all()]
        )
    )

# Get information and connections about one author on host.
@csrf_exempt
def friend(request, author_id):

    # Posts are forwarded to which_following
    if request.method == 'POST':
        return which_following(request, author_id)

    # check author existence
    try:
        author = Author.objects.get(uid=author_id)
    except:
        return HttpResponseNotFound('{"message": "No such author"}')

    # add connections
    d = author.to_dict()
    d['connections'] = [i.to_dict() for i in author.get_followees()]

    return HttpResponse(json.dumps(d))

# Query whether one author is following another.
def is_following(request, author_id1, author_id2):
    # check existence of both authors
    try:
        author1 = Author.objects.get(uid=author_id1)
        author2 = Author.objects.get(uid=author_id2)
    except:
        return HttpResponseBadRequest('{"message": "No such author"}')

    return HttpResponse(
        json.dumps(
            {
                "query": "friends",
                "authors": [
                    author_id1,
                    author_id2,
                ],
                "friends" : "YES" if author1.is_followee(author2) else "NO",
            }
        )
    )

# Query which members of a list of authors are following a specified author.
def which_following(request, author_id):
    # check author existence
    try:
        author = Author.objects.get(uid=author_id)
    except:
        return HttpResponseBadRequest('{"message": "No such author"}')

    # attempt to parse JSON body
    try:
        request_object = json.loads(request.body)

        # check JSON contains all required fields
        if  request_object['query'] != 'friends' or \
            not 'author' in request_object or \
            not isinstance(request_object['authors'], list):
            raise Error()

        # check that redundant author field matches requested URL
        if request_object['author'] != author_id:
            return HttpResponseBadRequest('{"message": "Author IDs must match"}')

        author_ids = set(request_object['authors'])
    except:
        return HttpResponseBadRequest('{"message": "JSON could not be parsed"}')

    all_followee_ids = set([i.uid for i in author.get_followees()])

    return HttpResponse(
        json.dumps(
            {
                "query": "friends",
                "author": author_id,
                "authors": list(all_followee_ids & author_ids), #intersection
            }
        )
    )

# Get the authors on the host following a specific author.
def following(request, author_id):
    # check author existence
    try:
        author = Author.objects.get(uid=author_id)
    except:
        return HttpResponseBadRequest('{"message": "No such author"}')

    all_follower_ids = [i.uid for i in author.get_followers()]

    return HttpResponse(
        json.dumps(
            {
                "query": "friends",
                "author": author_id,
                "authors": all_follower_ids,
            }
        )
    )


def friendrequest(request):
    """ The following is an example request.

    POST /api/friendrequest HTTP/1.1
    Host: http://cs410.cs.ualberta.ca:41081
    Content-Type: application/json

    {
      "query": "friendrequest",
      "author": {
          "displayname": "John"
          "id": "270f39c0cf6011e48ba1000c29737de1",
          "host": "http://hindlebook.tamarabyte.com",
      },
      "friend": {
          "displayname":"Jake",
          "id": "745a20b31faa78a88cbae4a000013d32",
          "host":"http://cs410.cs.ualberta.ca:41081",
          "url":"http://cs410.cs.ualberta.ca:41081/author/745a20b31faa78a88cbae4a000013d32"
      }
    }
    """

    # attempt to parse JSON body
    try:
        request_object = json.loads(request.body)
    except:
        return HttpResponseBadRequest('{"message": "JSON could not be parsed"}')

    try:
        author_id = request_object['friend']['id']
        author = Author.objects.get(uid=author_id)

        rauthor_info = request_object['author']
        rauthor_data = {'uid': rauthor_info['id'],
                        'displayname': rauthor_info['displayname'],
                        'host': rauthor_info['host']}
        rauthor, _ = Author.objects.get_or_create(**rauthor_data)
        rauthor.befriend(author)
    except:
        return HttpResponseNotFound('{"message": "No such author"}')
    return HttpResponse()
