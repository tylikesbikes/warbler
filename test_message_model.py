from unittest import TestCase
import os
from sqlalchemy.orm.exc import NoResultFound

#set os environ variable for TEST database before itinializing app to the prod db
os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app
from models import db, Follows, Likes, User, Message

db.drop_all()

class MessageModelTestCase(TestCase):
    """Tests for message db model"""

    def setUp(self):
        db.create_all()

        self.client = app.test_client()

        self.usr1 = User.signup(username='testuser',
                      email='a@b.co',
                      password = 'password',
                      image_url = 'asdf.jpg'
                   )
        
        self.usr2 = User.signup(username='testuser2',
                email='b@c.do',
                password = 'password2',
                image_url = 'bsdf.jpg'
            )
    
        db.session.add_all([self.usr1, self.usr2])
        db.session.commit()
    
        self.test_msg = Message(text='new test message', user_id = self.usr1.id)

        db.session.add(self.test_msg)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        

    def test_create_messge(self):
        """Can we retrieve the test message from the db?"""

        msg = Message.query.one()

        self.assertTrue(msg.text, 'new test message')

    def test_like_message(self):
        """can user two like user one's message?"""
        
        msg = Message.query.one()

        self.usr2.likes.append(msg)

        likes = Likes.query.one()

        self.assertTrue(likes.user_id, self.usr2.id)  #Did user two like user one's message?

        #Can we delete a liked message?
        db.session.delete(msg)
        db.session.commit()
        with self.assertRaises(NoResultFound):  #Message is deleted if test passes
            Message.query.one()

        #Did the likes get deleted along with it?
        with self.assertRaises(NoResultFound):
            Likes.query.one()

    def test_msg_likes_count(self):
        """Does Message.likes return a list of appropriate length?"""

        msg2 = Message(text = 'msg2', user_id = self.usr2.id)
        msg3 = Message(text = 'msg3', user_id = self.usr2.id)

        db.session.add_all([msg2, msg3])
        db.session.commit()

        self.usr1.likes.append(self.test_msg)
        self.usr1.likes.append(msg2)
        self.usr1.likes.append(msg3)

        db.session.commit()
        self.assertEqual(len(self.usr1.likes), 3)

    def test_msg_user_relationship(self):
        """Does Message.user return the correct username of the message creator?"""

        self.assertEqual(self.test_msg.user_id, self.usr1.id)