import redis, os, sys
from flask import Flask
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from  config import app_config
from app.views import home

# Initialize the app



def create_app(config_name):

    """

    the following  method implement  the application
    factory design pattern !
    it's responsible for creating all the app with 2
     configurations mode test ,develpement

    """

    if config_name == "test":
        app = Flask(__name__)
        app.config.from_object(app_config[config_name])

    else:

        #for template folder when runned as a package
        if getattr(sys, 'frozen', False):
            template_folder = os.path.join(os.getcwd(), 'templates')
            static_folder = os.path.join(os.getcwd(), 'static')
            print(template_folder, static_folder)
            app = Flask(__name__,
                        template_folder=template_folder,
                        static_folder=static_folder)
        else:
            app = Flask(__name__)
    app.config.from_object(app_config['development'])
    app.register_blueprint(home)
    """
    will youse a kv sesssion to store session data in client side

    """
    store = RedisStore(redis.StrictRedis())
    KVSessionExtension(store, app)

    return app
