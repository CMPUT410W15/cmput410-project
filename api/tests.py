from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import HttpRequest

from posts.models import *
from author.models import *
from management.models import *
from middleware_custom import APIMiddleware

import base64
import json

class TestClient(Client):

    auth = "Basic " + base64.b64encode("user:host:password")

    def get(self, path):
        return super(TestClient, self).get(
            '/api/' + path, 
            HTTP_AUTHORIZATION=TestClient.auth
        )

    def post(self, path, data, content_type="application/json"):
        return super(TestClient, self).post(
            '/api/' + path, 
            data,
            content_type,
            HTTP_AUTHORIZATION=TestClient.auth
        )


class APITests(TestCase):

    def setUp(self):
        user1 = User.objects.create(username='John')
        user2 = User.objects.create(username='Jack')
        user3 = User.objects.create(username='Josh')
        self.author1 = Author.objects.create(user=user1, uid="user", host="host")
        self.author2 = Author.objects.create(user=user2, host="host")
        self.author3 = Author.objects.create(user=user3, host="host2")

        # authors 1 and 3 are friends
        Connection.objects.create(
            from_author=self.author1, to_author=self.author3
        )
        Connection.objects.create(
            from_author=self.author3, to_author=self.author1
        )

        self.post1 = Post.objects.create(
                        title='Post1',
                        content='I like to say hi :D',
                        send_author=self.author1,
                        content_type=PLAINTEXT,
                        visibility=PRIVATE
                     )
        self.post2 = Post.objects.create(
                         title='Post2',
                         content='stuff about things!',
                         send_author=self.author2,
                         content_type=PLAINTEXT,
                         visibility=FRIENDS
                     )
        self.post3 = Post.objects.create(
                         title='Post3',
                         content='stuff about things again!',
                         send_author=self.author1,
                         content_type=PLAINTEXT,
                         visibility=PUBLIC
                     )
        self.post4 = Post.objects.create(
                         title='Post4',
                         content='I choose you!',
                         send_author=self.author3,
                         receive_author=self.author1,
                         content_type=PLAINTEXT,
                         visibility=FRIEND
                     )
        self.post5 = Post.objects.create(
                         title='Post5',
                         content='post5',
                         send_author=self.author3,
                         content_type=PLAINTEXT,
                         visibility=SERVERONLY
                     )
        self.post6 = Post.objects.create(
                         title='Post6',
                         content='post6',
                         send_author=self.author2,
                         content_type=PLAINTEXT,
                         visibility=SERVERONLY
                     )
        self.post7 = Post.objects.create(
                         title='Post7',
                         content='post7',
                         send_author=self.author3,
                         content_type=PLAINTEXT,
                         visibility=FRIENDS
                     )

        Node.objects.create(url="host")

        self.c = TestClient()

    def test_auth(self):
        c = Client()

        # test no auth
        response = c.get('/api/friends')
        self.assertEqual(response.status_code, 401)
        obj = json.loads(response.content)
        self.assertTrue('message' in obj)
        self.assertEqual(obj['message'], "Must authenticate")

        # test bad auth
        response = c.get('/api/friends', HTTP_AUTHORIZATION="bad")
        self.assertEqual(response.status_code, 401)
        obj = json.loads(response.content)
        self.assertTrue('message' in obj)
        self.assertEqual(obj['message'], "Authentication Rejected")

        # test bad password
        auth = "Basic " + base64.b64encode("user:host:bad_password")
        response = c.get('/api/friends', HTTP_AUTHORIZATION=auth)
        obj = json.loads(response.content)
        self.assertTrue('message' in obj)
        self.assertEqual(obj['message'], "Authentication Rejected")

        # test bad host
        auth = "Basic " + base64.b64encode("user:bad_host:password")
        response = c.get('/api/friends', HTTP_AUTHORIZATION=auth)
        obj = json.loads(response.content)
        self.assertTrue('message' in obj)
        self.assertEqual(obj['message'], "Authentication Rejected")

        # test good auth
        auth = "Basic " + base64.b64encode("user:host:password")
        response = c.get('/api/friends', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        # test auth user found
        req = HttpRequest()
        auth = "Basic " + base64.b64encode(self.author1.uid + ":host:password")
        req.META['HTTP_AUTHORIZATION'] = auth
        req.path = '/api/example'
        self.assertEqual(APIMiddleware().process_request(req), None)
        self.assertEqual(req.user, self.author1)

        # test auth user not found
        req = HttpRequest()
        auth = "Basic " + base64.b64encode("bad:host:password")
        req.META['HTTP_AUTHORIZATION'] = auth
        req.path = '/api/example'
        self.assertEqual(APIMiddleware().process_request(req), None)
        self.assertEqual(req.user.uid, "bad")
        self.assertFalse(hasattr(req.user, 'user'))
        self.assertEqual(User.objects.all().count(), 3)
        self.assertEqual(Author.objects.all().count(), 3)

    def test_contentType(self):

        # check for json header on good auth
        response = self.c.get('friends')
        self.assertTrue('Content-Type' in response)
        self.assertEqual(response['Content-Type'], 'application/json')

        c = Client() 

        # test for json header on bad auth
        response = c.get('/api/friends')
        self.assertTrue('Content-Type' in response)
        self.assertEqual(response['Content-Type'], 'application/json')

        # test for no json header on non API endpoint
        response = c.get('/friends')
        self.assertNotEqual(response['Content-Type'], 'application/json')

    def test_posts(self):

        response = self.c.get('posts')
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, list))
        self.assertEqual(len(obj), 5)
        titles = [i["title"] for i in obj]
        self.assertTrue("Post1" in titles)
        self.assertTrue("Post3" in titles)
        self.assertTrue("Post4" in titles)
        self.assertTrue("Post6" in titles)
        self.assertTrue("Post7" in titles)

    def test_public_posts(self):

        response = self.c.get('posts/public')
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, list))
        self.assertEqual(len(obj), 1)
        titles = [i["title"] for i in obj]
        self.assertTrue("Post3" in titles)

    def test_post(self):

        # test found
        response = self.c.get('posts/' + self.post1.uid)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertEqual(obj["title"], "Post1")

        # test not visible
        response = self.c.get('posts/' + self.post2.uid)
        self.assertEqual(response.status_code, 401)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "Authentication Rejected")

        # test not found
        response = self.c.get('posts/asdf')
        self.assertEqual(response.status_code, 404)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such post")

    def test_comment(self):

        # test found
        response = self.c.post(
            'posts/' + self.post1.uid + "/comment", 
            data="comment", 
            content_type="text/plain"
        )
        self.assertEqual(response.status_code, 201)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("comment" in obj)
        self.assertEqual(obj["comment"], "comment")
        self.assertTrue("author" in obj)
        self.assertEqual(obj["author"]["id"], "user")
        self.assertEqual(self.post1.get_comments().count(), 1)

        # test not visible
        response = self.c.post(
            'posts/' + self.post2.uid + "/comment", data="comment"
        )
        self.assertEqual(response.status_code, 401)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "Authentication Rejected")

        # test not found
        response = self.c.post(
            'posts/asdf/comment', data="comment"
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such post")

    def test_friends(self):
       
        response = self.c.get("friends")
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, list))
        self.assertEqual(len(obj), 3)

        names = [i["displayname"] for i in obj]
        self.assertTrue("John" in names)
        self.assertTrue("Jack" in names)
        self.assertTrue("Josh" in names)
        
    def test_friend(self):

        # test found
        response = self.c.get("friends/" + self.author1.uid)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("displayname" in obj)
        self.assertEqual(obj["displayname"], "John")
        self.assertTrue("connections" in obj)
        self.assertTrue(isinstance(obj["connections"], list))
        self.assertEqual(len(obj["connections"]), 1)
        self.assertEqual(obj["connections"][0]["id"], self.author3.uid)

        # test not found
        response = self.c.get("friends/asdf")
        self.assertEqual(response.status_code, 404)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such author")

    def test_is_following(self):

        # test YES
        response = self.c.get(
            "friends/" + self.author1.uid + "/" + self.author3.uid
        )
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("query" in obj)
        self.assertEqual(obj["query"], "friends")
        self.assertTrue("authors" in obj)
        self.assertTrue(isinstance(obj["authors"], list))
        self.assertEqual(len(obj["authors"]), 2)
        self.assertEqual(obj["authors"][0], self.author1.uid)
        self.assertEqual(obj["authors"][1], self.author3.uid)
        self.assertTrue("friends" in obj)
        self.assertEqual(obj["friends"], "YES")

        # test NO
        response = self.c.get(
            "friends/" + self.author1.uid + "/" + self.author2.uid
        )
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("query" in obj)
        self.assertEqual(obj["query"], "friends")
        self.assertTrue("authors" in obj)
        self.assertTrue(isinstance(obj["authors"], list))
        self.assertEqual(len(obj["authors"]), 2)
        self.assertEqual(obj["authors"][0], self.author1.uid)
        self.assertEqual(obj["authors"][1], self.author2.uid)
        self.assertTrue("friends" in obj)
        self.assertEqual(obj["friends"], "NO")

        # test not found
        response = self.c.get(
            "friends/asdf/" + self.author3.uid
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such author")
        response = self.c.get(
            "friends/" + self.author3.uid + "/asdf"
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such author")

    def test_which_following(self):

        # test found 
        query = {
            "query": "friends",
            "author": self.author1.uid,
            "authors": [
                self.author1.uid,
                self.author2.uid,
                self.author3.uid
            ]
        }
        response = self.c.post(
            'friends/' + self.author1.uid,
            data=json.dumps(query)
        )
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("query" in obj)
        self.assertEqual(obj["query"], "friends")
        self.assertTrue("authors" in obj)
        self.assertTrue(isinstance(obj["authors"], list))
        self.assertEqual(len(obj["authors"]), 1)
        self.assertEqual(obj["authors"][0], self.author3.uid)
        self.assertTrue("author" in obj)
        self.assertEqual(obj["author"], self.author1.uid)

        # test not found
        response = self.c.post(
            'friends/asdf',
            data=json.dumps(query)
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such author")

        # test bad JSON
        response = self.c.post(
            'friends/' + self.author1.uid,
            data="bad"
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "JSON could not be parsed")

        # test non matching IDs
        query["author"] = "bad"
        response = self.c.post(
            'friends/' + self.author1.uid,
            data=json.dumps(query)
        )
        self.assertEqual(response.status_code, 400)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "Author IDs must match")
