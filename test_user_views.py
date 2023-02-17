from unittest import TestCase
import os 
os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'
from app import app, CURR_USER_KEY
from models import db, User, Message, Likes, Follows

from seed import seed

app.config['WITH_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test User Views"""

    def setUp(self):
        self.client = app.test_client()
        seed(db)

    def test_user_view_not_logged_in(self):
        """Does /users/userid view return a page with the right user info?"""
        with self.client as c:
            resp = c.get('/users/2', follow_redirects = True)

        self.assertIn(b'Access unauthorized', resp.data)

    def test_user_view_logged_in(self):
        #manually edit session to appear logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            resp = c.get('/users/2', follow_redirects = True)

        self.assertIn(b'Decision professional real', resp.data)

    def test_user_view_add_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            get_resp = c.get('/messages/new', follow_redirects = True)
            post_resp = c.post('/messages/new', data={'text':'my_new_message'}, follow_redirects = True)

        #Post.  Check for form w/textarea placeholder text
        self.assertIn(b'Add my message!', get_resp.data)
        
        #Get.  check status code 201;
        self.assertEqual(post_resp.status_code, 201)
        #Get. check message content showing on next page; 
        self.assertIn(b'my_new_message', post_resp.data)