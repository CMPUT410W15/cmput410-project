from django.test import TestCase
from django.contrib.auth.models import User
from posts.models import Post, Comment, Category
from posts.models import PRIVATE, FRIEND, FRIENDS, FOAF, PUBLIC, SERVERONLY
from posts.models import PLAINTEXT, MARKDOWN
from author.models import Author

# Create your tests here.

class PostTests(TestCase):

    def setUp(self):
        user1 = User.objects.create(username='John')
        user2 = User.objects.create(username='Jack')
        user3 = User.objects.create(username='Josh')
        self.author1 = Author.objects.create(user=user1)
        self.author2 = Author.objects.create(user=user2)
        self.author3 = Author.objects.create(user=user3)

        self.post1 = {'title': 'Post1',
                      'content': 'I like to say hi :D',
                      'send_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': PRIVATE}
        self.post2 = {'title': 'Post2',
                      'content': 'stuff about things!',
                      'send_author': self.author2,
                      'content_type': PLAINTEXT,
                      'visibility': FRIENDS}
        self.post3 = {'title': 'Post3',
                      'content': 'stuff about things again!',
                      'send_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': PUBLIC}
        self.post4 = {'title': 'Post4',
                      'content': 'I choose you!',
                      'send_author': self.author3,
                      'receive_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': FRIEND}

        self.post5 = {'title': 'Post5',
                      'content': 'I do not choose you!',
                      'send_author': self.author1,
                      'receive_author': self.author2,
                      'content_type': PLAINTEXT,
                      'visibility': FRIEND}


        self.post6 = {'title': 'Post6',
                      'content': 'Not markdown',
                      'send_author': self.author2,
                      'receive_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': FRIEND}


        self.post7 = {'title': 'Post7',
                      'content': 'Still not markdown',
                      'send_author': self.author3,
                      'receive_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': FRIEND}

        self.post8 = {'title': 'Post8',
                      'content': 'stuff about things again and again!',
                      'send_author': self.author1,
                      'content_type': PLAINTEXT,
                      'visibility': PUBLIC}

    def test_get_all_friends_author1_posts(self):
        #Posts 5,6,7 are friend - 8 and 3 are public.
        # Author 1 should only receive posts 6 and 7
        post5= Post.objects.create(**self.post5)  
        post6= Post.objects.create(**self.post6)
        post7= Post.objects.create(**self.post7)
        post8= Post.objects.create(**self.post8) 
        post3= Post.objects.create(**self.post3)

        self.assertEqual(len(self.author1.get_received_posts(visibility=FRIEND)), 2)

    def get_public_posts(self):
        #Posts 5,6,7 are friend - 8 and 3 are public
        post5= Post.objects.create(**self.post5)  
        post6= Post.objects.create(**self.post6)
        post7= Post.objects.create(**self.post7)
        post8= Post.objects.create(**self.post8) 
        post3= Post.objects.create(**self.post3)
        all_posts = Post.objects.all()
        public=[]
        for p in all_posts:
            if (p.visibility==4):
                public.append(p)
            else:
                continue
        self.assertEqual(len(public),2)

    def test_create_post(self):
        post = Post.objects.create(**self.post1)
        self.assertEqual(post.send_author, self.author1)
        self.assertEqual(post.title, self.post1['title'])
        self.assertEqual(post.content, self.post1['content'])
        self.assertEqual(post.visibility, self.post1['visibility'])
        self.assertEqual(post.content_type, self.post1['content_type'])

    def test_create_post_to_specific_author(self):
        post = Post.objects.create(**self.post4)
        self.assertEqual(post.send_author, self.author3)
        self.assertEqual(post.receive_author, self.author1)
        self.assertEqual(post.visibility, FRIEND)

    def test_get_posts(self):
        post = Post.objects.create(**self.post1)
        self.assertEqual(self.author1.get_posts()[0], post)

    def test_get_specific_authors_posts(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        self.assertEqual(len(self.author1.get_posts()), 2)
        self.assertEqual(len(self.author2.get_posts()), 1)
        self.assertEqual(len(self.author3.get_posts()), 0)

    def test_get_specific_authors_posts(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        self.assertEqual(len(self.author1.get_posts()), 2)
        self.assertEqual(len(self.author2.get_posts()), 1)
        self.assertEqual(len(self.author3.get_posts()), 0)

    def test_get_specific_posts_visibility(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        self.assertEqual(len(self.author1.get_posts(visibility=PUBLIC)), 1)
        self.assertEqual(len(self.author1.get_posts(visibility=PRIVATE)), 1)
        self.assertEqual(len(self.author2.get_posts(visibility=FRIENDS)), 1)

    def test_get_friends_posts(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        self.author1.follow(self.author2)
        self.author1.follow(self.author3)
        self.author2.follow(self.author1)
        self.author2.follow(self.author3)
        self.author3.follow(self.author1)
        self.author3.follow(self.author2)
        friends = self.author3.get_friends()
        self.assertEqual(len([p for f in friends for p in f.get_posts()]), 3)

    def test_comment(self):
        post1 = Post.objects.create(**self.post1)
        c = post1.add_comment(self.author2, 'hello!')
        self.assertEqual(c.author, self.author2)
        self.assertEqual(c.post, post1)
        self.assertEqual(c.content, 'hello!')

    def test_get_no_comments(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        self.assertEqual(len(post1.get_comments()), 0)
        self.assertEqual(len(post2.get_comments()), 0)

    def test_get_comments(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        post1.add_comment(self.author2, 'hello!')
        post3.add_comment(self.author3, 'ello!')
        post2.add_comment(self.author1, 'llo!')
        post1.add_comment(self.author2, 'lo!')
        post2.add_comment(self.author3, 'o!')
        post1.add_comment(self.author1, '!')
        num = sum([len(p.get_comments()) for p in [post1, post2, post3]])
        self.assertEqual(num, 6)

    def test_get_author_comments(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        post1.add_comment(self.author2, 'hello!')
        post1.add_comment(self.author3, 'ello!')
        post1.add_comment(self.author3, 'llo!')
        post1.add_comment(self.author2, 'lo!')
        post1.add_comment(self.author3, 'o!')
        post2.add_comment(self.author1, '!')
        self.assertEqual(len(self.author1.get_comments()), 1)
        self.assertEqual(len(self.author2.get_comments()), 2)
        self.assertEqual(len(self.author3.get_comments()), 3)
        self.assertEqual(post2.get_comments()[0].content, '!')

    def test_get_specific_comments(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        post3 = Post.objects.create(**self.post3)
        post1.add_comment(self.author2, 'hello!')
        post1.add_comment(self.author3, 'ello!')
        post1.add_comment(self.author1, 'llo!')
        post1.add_comment(self.author2, 'lo!')
        post1.add_comment(self.author3, 'o!')
        post2.add_comment(self.author1, '!')
        self.assertEqual(len(post1.get_comments()), 5)
        self.assertEqual(len(post2.get_comments()), 1)
        self.assertEqual(len(post3.get_comments()), 0)
        self.assertEqual(post2.get_comments()[0].content, '!')

    def test_remove_comment(self):
        post1 = Post.objects.create(**self.post1)
        post1.add_comment(self.author2, 'hello!')
        post1.add_comment(self.author3, 'ello!')
        c = post1.add_comment(self.author1, 'llo!')
        post1.remove_comment(c.uid)
        self.assertEqual(len(post1.get_comments()), 2)

    def test_adding_categories(self):
        post1 = Post.objects.create(**self.post1)
        post2 = Post.objects.create(**self.post2)
        cat1 = Category.objects.create(category="Turtles")
        cat2 = Category.objects.create(category="Penguins")
        cat3 = Category.objects.create(category="Lizards")

        post1.add_category(cat1)
        post2.add_category(cat2)
        post2.add_category(cat3)
        self.assertEqual(len(post1.get_categories()), 1)
        self.assertEqual(post1.get_categories()[0].category, "Turtles")
        self.assertEqual(len(post2.get_categories()), 2)

        p2_categories = [c.category for c in post2.get_categories()]
        self.assertEqual("Penguins" in p2_categories, True)
        self.assertEqual("Lizards" in p2_categories, True)
