"""Functions for dealing with remote authors."""
from author.models import Author
from common.util import get_request_to_json, post_request_to_json, get_nodes


def add_remote_connections(author1, remote_authors, node):
    authors = [a for a in Author.objects.all()] + remote_authors

    url = node.url + 'friends/%s' % author1.uid
    auth = ('api', 'test')
    headers = {
        'Content-Type': 'application/json',
        'Uuid': author1.uid
    }
    body = {
        "query": "friends",
        "author": author1.uid,
        "authors": [a.uid for a in authors]
    }

    ret_val = post_request_to_json(url, body, headers=headers, auth=auth)
    if isinstance(ret_val, dict):
        for uuid in ret_val['friends']:
            author2 = Author.objects.get(uuid=friend)
            author1.follow(author2)
            author2.follow(author1)


def reset_remote_authors():
    #Author.objects.filter(user=None).delete()

    for node in get_nodes():
        remote_authors = []
        for author in get_request_to_json(node.url + 'authors'):
            author_data = {'uid': author['id'],
                           'displayname': author['displayname'],
                           'host': author['host']}
            author_obj, _ = Author.objects.get_or_create(**author_data)
            remote_authors.append(author_obj)

        for author in remote_authors[:]:
            remote_authors.remove(author)
            add_remote_connections(author, remote_authors, node)
