"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser_self = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser_other = User.signup(username="testuser_other",
                            email="testother@test.com",
                            password="testuser_other",
                            image_url=None)
        
        db.session.add_all([self.testuser_self, self.testuser_other])
        db.session.commit()
        
        self.test_message = Message(text = 'testmessage',user_id=self.testuser_other.id)

        db.session.add(self.test_message)
        db.session.commit()

    
        

    def test_add_message(self):
        """Can user add a message?"""
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_self.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msgs = Message.query.order_by(Message.id.desc()).all()

            self.assertEqual(len(msgs),2)

            self.assertEqual(msgs[0].text, "Hello")

    def test_view_message(self):
        message = Message.query.one()


        with self.client as c:
            resp = c.get(f'/messages/{message.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testmessage', resp.data)