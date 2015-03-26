"""Functions for dealing with remote posts."""
from author.models import Author
from posts.models import Post, Comment
from common.util import get_request_to_json, get_nodes
from dateutil import parser


VISIBILITY = {
    'PRIVATE': 0,
    'FRIEND': 1,
    'FRIENDS': 2,
    'FOAF': 3,
    'PUBLIC': 4,
    'SERVERONLY': 5
}

CONTENT_TYPE = {
    'text/html': 0,
    'markdown': 1,
}



def add_remote_comment(comment, post):
    author = Author.objects.get(uid=comment['author']['id'])
    comment_data = {
        'uid': comment['guid'],
        'content': comment['comment'],
        'author': author,
        'post': post
    }
    if not len(Comment.objects.filter(uid=comment['guid'])):
        c, _ = Comment.objects.get_or_create(**comment_data)
        c.published = parser.parse(comment['pubDate'])


def add_remote_post(post):
    author = Author.objects.get(uid=post['author']['id'])
    post_data = {
        'uid': post['guid'],
        'title': post['title'],
        'description': post['description'],
        'content': post['content'],
        'content_type': CONTENT_TYPE[post['content-type']],
        'visibility': VISIBILITY[post['visibility']],
        'send_author': author
    }

    if not len(Post.objects.filter(uid=post_data['uid'])):
        p = Post.objects.get_or_create(**post_data)[0]
        p.published = parser.parse(post['pubDate'])
    else:
        p = Post.objects.get(uid=post_data['uid'])

    for comment in post['comments']:
        add_remote_comment(comment, p)


def reset_remote_posts():
    for node in get_nodes():
        for author in Author.objects.filter(user=None):
            headers = {'Uuid': author.uid}
            data = get_request_to_json(node.url + 'author/posts',
                                       headers, ('api', 'test'))
            for post in data['posts']:
                add_remote_post(post)
