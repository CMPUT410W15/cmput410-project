from django.test import TestCase
from django.contrib.auth.models import User
from author.models import Author, FollowYourselfError

# Create your tests here.
class AuthorTests(TestCase):

    def setUp(self):
        user1 = User.objects.create(username='John')
        user2 = User.objects.create(username='Jack')
        user3 = User.objects.create(username='Josh')
        Author.objects.create(user=user1)
        Author.objects.create(user=user2)
        Author.objects.create(user=user3)

    def test_befriend_yourself(self):
        user1 = User.objects.get(username='John')

        author1 = Author.objects.get(user=user1)
        self.assertRaises(FollowYourselfError, author1.befriend, author1)

    def test_follow_yourself(self):
        user1 = User.objects.get(username='John')

        author1 = Author.objects.get(user=user1)
        self.assertRaises(FollowYourselfError, author1.follow, author1)

    def test_follow(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_followers()), 1)
        self.assertEqual(author1.get_followers()[0], author2)

    def test_follow2(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)
        author2.follow(author1)
        author3.follow(author1)
        self.assertEqual(len(author1.get_followers()), 2)
        self.assertTrue(author2 in author1.get_followers())
        self.assertTrue(author3 in author1.get_followers())

    def test_unfollow(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        author2.unfollow(author1)
        self.assertEqual(len(author1.get_followers()), 0)

    def test_empty_unfollow(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.unfollow(author1)
        self.assertEqual(len(author1.get_followers()), 0)

    def test_follow_circle(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)

        author2.follow(author1)
        author3.follow(author2)
        author1.follow(author3)
        follower = author1.get_followers()[0]
        followee = author1.get_followees()[0]
        self.assertEqual(follower.get_followees()[0], author1)
        self.assertEqual(followee.get_followers()[0], author1)
        self.assertEqual(follower.get_followers()[0], followee)
        self.assertEqual(followee.get_followees()[0], follower)

    def test_friends_none(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_friends()), 0)

    def test_friends1(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        author1.follow(author2)
        self.assertEqual(len(author1.get_friends()), 1)
        self.assertEqual(author1.get_friends()[0], author2)

    def test_friends2(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)
        author2.follow(author1)
        author1.follow(author2)
        author3.follow(author1)
        author1.follow(author3)
        self.assertEqual(len(author1.get_friends()), 2)
        self.assertTrue(author2 in author1.get_friends())
        self.assertTrue(author3 in author1.get_friends())

    def test_fofs(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)
        author1.follow(author2)
        author2.follow(author1)

        author2.follow(author3)
        author3.follow(author2)
        fof_dict = author1.get_friends_of_friends()
        self.assertEqual(len(fof_dict.keys()), 1)
        self.assertEqual(fof_dict.keys()[0], author2)
        self.assertEqual(len(fof_dict.values()), 1)
        self.assertEqual(author3 in fof_dict.values()[0], True)

    def test_no_friend_request(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_friend_requests()), 0)

    def test_friend_request(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)
        author2.befriend(author1)
        author3.follow(author1)
        self.assertEqual(len(author1.get_friend_requests()), 1)
        self.assertEqual(author1.get_friend_requests()[0], author2)

    def test_friend_request2(self):
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')
        user3 = User.objects.get(username='Josh')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)
        author1.befriend(author2)
        author1.befriend(author3)
        author2.befriend(author1)
        author3.befriend(author1)
        self.assertEqual(len(author1.get_friend_requests()), 2)
        self.assertEqual(len(author2.get_friend_requests()), 1)
        self.assertEqual(len(author3.get_friend_requests()), 1)
