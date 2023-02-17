"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr method work properly?"""

        u = User(
            email='a@b.co',
            username = 'test_user2',
            password='HASHED_PASSWORD'
        )

        db.session.add(u)
        db.session.commit()

        self.assertIn(f'User #{u.id}', u.__repr__())

    def test_follows(self):
        u1 = User(
            email='a@b.co',
            username = 'test_user1',
            password='HASHED_PASSWORD'
        )

        u2 = User(
            email='b@c.do',
            username = 'test_user2',
            password='HASHED_PASSWORD'
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertFalse(u1.is_following(u2))

        u1.following.append(u2)

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
        self.assertTrue(u2.is_followed_by(u1))

        