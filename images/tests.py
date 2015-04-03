from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.core.files import File

from posts.models import *
from author.models import *
from images.models import *
from django.test.utils import override_settings
from management.models import *

import base64
import json

class TestClient(Client):

    auth = "Basic " + base64.b64encode("user:host:password")

    def get(self, path):
        return super(TestClient, self).get(
            '/images/' + path,
            HTTP_AUTHORIZATION=TestClient.auth,
        )

    def post(self, path, data, content_type="application/json"):
        return super(TestClient, self).post(
            '/images/' + path,
            data,
            content_type,
            HTTP_AUTHORIZATION=TestClient.auth
        )


class APITests(TestCase):

    @override_settings(MEDIA_ROOT='/tmp/django_test')
    def setUp(self):
        user1 = User.objects.create(username='user')
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
        self.sample_image = Image.objects.create(image=File(open("images/sample_image.png")), visibility=PUBLIC)
        self.sample_image2 = Image.objects.create(image=File(open("images/sample_image.png")), visibility=PRIVATE)
        
        self.post2 = Post.objects.create(
                         title='Post2',
                         content='stuff about things!',
                         send_author=self.author2,
                         content_type=PLAINTEXT,
                         visibility=FRIENDS,
                         image=self.sample_image2
                     )

        self.post8 = {'title': 'Post8',
              'content': 'stuff',
              'send_author': self.author3,
              'content_type': PLAINTEXT,
              'visibility': PUBLIC,
              'image' : self.sample_image,
              }

        self.post9 = {'title': 'Post9',
              'content': 'stuff',
              'send_author': self.author2,
              'content_type': PLAINTEXT,
              'visibility': FRIENDS,
              'image' : self.sample_image2,
              }

        Node.objects.create(url="host")

        self.c = TestClient()
    
    def test_create_image_post(self):
        """Test Post with Image creation.

        Make sure that any post created will have the same image content
        that a user provided.

        """
        post = Post.objects.create(**self.post8)
        self.assertEqual(post.image, self.sample_image)

        post = Post.objects.create(**self.post9)
        self.assertEqual(post.image, self.sample_image2)

    @override_settings(MEDIA_ROOT='/tmp/django_test')
    def test_get_image(self):
        
        # test found, check for file validity, NOT file contents
        response = self.c.get(self.sample_image.uid)
        self.assertEqual(response.status_code, 200)

        # Write image bytes to file 'img.png'
        fname = 'images/img.png'
        with open(fname, 'wb') as out_file:
            out_file.write(response.content)

        # Check file 'img.png' validity
        import os
        self.assertTrue(os.path.isfile(fname))

        # Check length with original 
        test_size = os.path.getsize('images/img.png')
        sample_size = os.path.getsize('images/sample_image.png')
        self.assertEqual(test_size, sample_size )

        # test not visible
        response = self.c.get(self.sample_image2.uid)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, 'Unauthorized')

        # test not found
        response = self.c.get('images/asdf')
        self.assertEqual(response.status_code, 404)
        obj = json.loads(response.content)
        self.assertTrue(isinstance(obj, dict))
        self.assertTrue("message" in obj)
        self.assertEqual(obj["message"], "No such image")