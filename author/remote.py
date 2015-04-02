"""Functions for dealing with remote authors."""
from author.models import Author, Connection
from common.util import HINDLE_AUTH, BUBBLE_AUTH
from common.util import get_request_to_json, post_request_to_json, get_nodes
from common.util import BUBBLE, HINDLEBOOK


def add_remote_connections(author1, remote_authors, node):
    authors = [a for a in Author.objects.all()] + remote_authors
    body = {
        "query": "friends",
        "author": author1.uid,
        "authors": [a.uid for a in authors if a.uid != author1.uid]
    }

    if HINDLEBOOK in node.url:
        url = node.url + 'friends/%s' % author1.uid
        headers = {
            'Content-Type': 'application/json',
            'Uuid': author1.uid
        }
        ret_val = post_request_to_json(url, body, headers=headers,
                                       auth=HINDLE_AUTH)
    elif BUBBLE in node.url:
        url = node.url + "checkfriends/?user=%s" % author1.uid
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }

        ret_val = post_request_to_json(url, body, headers=headers,
                                       auth=BUBBLE_AUTH)
    if isinstance(ret_val, dict):
        for uuid in ret_val['friends']:
            author2 = Author.objects.get(uid=uuid)
            author1.follow(author2)
            author2.follow(author1)


def reset_remote_authors():
    for author in Author.objects.filter(user=None):
        Connection.objects.filter(from_author=author).delete()

    for node in get_nodes():
        remote_authors = []
        if HINDLEBOOK in node.url:
            authors = get_request_to_json(node.url + 'authors')
        elif BUBBLE in node.url:
            authors = get_request_to_json(node.url + 'getallauthors/',
                                          auth=BUBBLE_AUTH)
            authors = authors['authors']

        for author in authors:
            if BUBBLE in author['host'] or HINDLEBOOK in author['host']:
                author_data = {'uid': author['id'],
                               'displayname': author['displayname'],
                               'host': author['host']}
                author_obj, _ = Author.objects.get_or_create(**author_data)
                remote_authors.append(author_obj)

        for author in remote_authors[:]:
            remote_authors.remove(author)
            add_remote_connections(author, remote_authors, node)


def send_remote_friend_request(local_author, remote_author):
    body = {
        "query": "friendrequest",
        "author": {
            "id": local_author.uid,
            "host": local_author.host,
            "displayname": local_author.user.username
        },
        "friend": {
            "id": remote_author.uid,
            "host": remote_author.host,
            "displayname": remote_author.displayname,
            "url": "%s/author/%s" % (remote_author.host,
                                            remote_author.uid)
        }
    }

    if HINDLEBOOK in remote_author.host:
        url = "%s/api/friendrequest" % remote_author.host
        headers = {
            "Content-Type": "application/json",
            "Uuid": remote_author.uid
        }
        post_request_to_json(url, body, headers=headers,
                             auth=HINDLE_AUTH)
    elif BUBBLE in remote_author.host:
        url = "http://%s/main/api/newfriendrequest" % remote_author.host
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        post_request_to_json(url, body, headers=headers)
