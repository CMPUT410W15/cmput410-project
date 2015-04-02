"""Functions for dealing with remote posts."""
from author.models import Author
from posts.models import Post, Comment
from common.util import get_request_to_json, get_nodes
from common.util import HINDLEBOOK, HINDLE_AUTH, BUBBLE, BUBBLE_AUTH
from dateutil import parser


VISIBILITY = {
    'PRIVATE': 0,
    'FRIEND': 1,
    'FRIENDS': 2,
    'FOAF': 3,
    'PUBLIC': 4,
    'SERVERONLY': 5,
    'private': 0,
    'friend': 1,
    'friends': 2,
    'foaf': 3,
    'public': 4,
    'serveronly': 5
}

CONTENT_TYPE = {
    u'text/html': 0,
    u'text/x-markdown': 1,
}


def get_pubdate(dictionary):
    pd1 = dictionary.get('pubDate', None)
    pd2 = dictionary.get('pubdate', None)
    return pd1 or pd2


def add_remote_comment(comment, post, author):
    comment_data = {
        'uid': comment['guid'],
        'content': comment['comment'],
        'author': author,
        'post': post
    }
    if not len(Comment.objects.filter(uid=comment['guid'])):
        c, _ = Comment.objects.get_or_create(**comment_data)
        c.published = parser.parse(get_pubdate(comment))


def add_remote_post(post, author):
    post_data = {
        'uid': post['guid'],
        'title': post['title'],
        'description': post['description'],
        'content': post['content'],
        'content_type': CONTENT_TYPE.get(post['content-type'], 0),
        'visibility': VISIBILITY[post['visibility']],
        'send_author': author
    }

    if not len(Post.objects.filter(uid=post_data['uid'])):
        p = Post.objects.get_or_create(**post_data)[0]
        p.published = parser.parse(get_pubdate(post))
    else:
        p = Post.objects.get(uid=post_data['uid'])

    for comment in post['comments']:
        try:
            author = Author.objects.get(uid=comment['author']['id'])
            add_remote_comment(comment, p, author)
        except:
            pass


def reset_remote_posts():
    for node in get_nodes():
        for author in Author.objects.filter(user=None):
            if HINDLEBOOK in author.host:
                headers = {'Uuid': author.uid}
                data = get_request_to_json(node.url + 'author/posts',
                                           headers, HINDLE_AUTH)
            elif BUBBLE in author.host:
                data = get_request_to_json(node.url + 'author/posts2/',
                                           headers, BUBBLE_AUTH)
            else:
                data = 0

            if not isinstance(data, int):
                for post in data['posts']:
                    uid = post['author']['id']
                    try:
                        author = Author.objects.get(uid=uid)
                        add_remote_post(post, author)
                    except:
                        pass
