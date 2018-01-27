import os
from os.path import abspath, dirname, join



class DevellopementConfig(object):
    """ developement configurations """
    DEBUG = True
    SECRET_KEY = 'this is my secret key 9874'



class TestingConfig(object):
    """ for testing """

    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_ENABLED = False
    TESTING = True
    HASH_ROUNDS = 1
    LOGIN_DISABLED = True


    #to sisable login required
    #DATABASE_FILE='testRevit.sqlite'
    #SESSION_TYPE='filesystem'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE

    # Since we want our unit tests to run quickly
    # we turn this down - the hashing is still done
    # but the time-consuming part is left out.
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')


app_config ={
    'development':DevellopementConfig,
    'test':TestingConfig
}
