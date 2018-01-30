import redis, os, sys
from flask import Flask
from flask_kvsession import KVSessionExtension
from simplekv.fs import FilesystemStore
from  config import app_config
from app.views import home, SESSION_FOLDER

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
            template_folder = os.path.join(sys._MEIPASS, 'templates')
            print(template_folder)
            app = Flask(__name__,
                        template_folder=template_folder)
        else:
            print(sys.path[0])
            app = Flask(__name__)
        app.config.from_object(app_config['development'])
    app.register_blueprint(home)
    """
    will use a kv sesssion to store session data in client side

    """
    store = FilesystemStore(SESSION_FOLDER)
    KVSessionExtension(store, app)

    return app
