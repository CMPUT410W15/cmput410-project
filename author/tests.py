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
        """Test that you cannot befriend yourself."""
        user1 = User.objects.get(username='John')

        author1 = Author.objects.get(user=user1)
        self.assertRaises(FollowYourselfError, author1.befriend, author1)

    def test_follow_yourself(self):
        """Test that you cannot follow yourself."""
        user1 = User.objects.get(username='John')

        author1 = Author.objects.get(user=user1)
        self.assertRaises(FollowYourselfError, author1.follow, author1)

    def test_follow(self):
        """Test that you can follow another author."""
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_followers()), 1)
        self.assertEqual(author1.get_followers()[0], author2)

    def test_follow2(self):
        """Check that get_followers return correct values."""

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
        """Test that you can unfollow someone."""
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        author2.unfollow(author1)
        self.assertEqual(len(author1.get_followers()), 0)

    def test_empty_unfollow(self):
        """Check that unfollow doesn't break.

        This is a case when you unfollow someone that you never followed to
        begin with.

        """
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.unfollow(author1)
        self.assertEqual(len(author1.get_followers()), 0)

    def test_follow_circle(self):
        """Test get_followers and get_followees navigation.

        Here A -> B, B -> C and C -> A. Check that you can navigate around
        this cycle using the methods mentioned.

        """
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
        """Test following doesn't cause friendship."""
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_friends()), 0)

    def test_friends1(self):
        """Test that following each other causes friendship."""
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        author1.follow(author2)
        self.assertEqual(len(author1.get_friends()), 1)
        self.assertEqual(author1.get_friends()[0], author2)

    def test_friends2(self):
        """Like test_friends1 except with two friends.

        Ensure get_friends returns correct values.

        """
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
        """Test the get_friends_of_friends method."""
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
        """Test that following doesn't send a friend request."""
        user1 = User.objects.get(username='John')
        user2 = User.objects.get(username='Jack')

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author2.follow(author1)
        self.assertEqual(len(author1.get_friend_requests()), 0)

    def test_friend_request(self):
        """Test that befriend sends a friend request."""
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
        """Test that get_friend_requests is correct."""
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
