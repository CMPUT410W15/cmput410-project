"""Functions for dealing with remote authors."""
from author.models import Author
from common.util import get_request_to_json, get_nodes


def add_remote_connections(author1, remote_authors, node):
    for author2 in remote_authors:
        friends_url = 'friends/%s/%s' % (author1.uid, author2.uid)
        result = get_request_to_json(node.url + friends_url)
        if result not in [401, 404] and result['friends'] == 'YES':
            author1.follow(author2)
            author2.follow(author1)

    for author2 in Author.objects.all():
        friends_url = 'friends/%s/%s' % (author1.uid, author2.uid)
        result = get_request_to_json(node.url + friends_url)
        if result not in [401, 404] and result['friends'] == 'YES':
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
