import unittest
import os, io
import json
from flask import abort, url_for, Flask
from app import create_app




class TestBase(unittest.TestCase):
    """this is the base case for ours tests"""

    def setUp(self):
        """this method will make all initialisation for ours tests"""

        if os.getenv('FLASK_CONFIG') == 'test': #if we are in CIRCLECI environement
            self.app = create_app(config_name="test")
            self.client = self.app.test_client


    def tearDown(self):

        """
        the method will remove all variables
        used for the tests
        """


class TestViews(TestBase):
    """
    this class will handle the testing of our front end page
    and view

    """
    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        with self.app.test_request_context():
            response = self.client().get(url_for('home.index'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('hello', str(response.data))


class TestUploads(TestBase):
    """
    this class will handle the testing of our uploadings files
    functions
    """


    def test_can_upload_product(self):
        """
        Test can upload a file , the test should check if the api raise
        an error in case of a wrong file is posted
        """
        data = {}
        data['file'] = (io.BytesIO(b"abcdef"), 'bom.xlsx')
        data['category'] = 'bom'
        with self.app.test_request_context():
            response = self.client().post(
                url_for('home.upload_bom'),
                data=data,
                follow_redirects=True,
                content_type='multipart/form-data'
            )
            self.assertRaises(Exception)
            self.assertIn(b'Erreur', response.data)
