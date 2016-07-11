from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_principal import Principal
from defines import *

db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'accounts.login'
principal = Principal()

def create_app():
    app = Flask(__name__,
                template_folder = DevConfig.TEMPLATE_PATH,
                static_folder = DevConfig.STATIC_PATH)
    app.config.from_object(DevConfig)
    DevConfig.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    principal.init_app(app)

    #register url
    from main.urls import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from main.urls import blog_admin as blog_admin_blueprint
    app.register_blueprint(blog_admin_blueprint, url_prefix="/admin")

    from account.urls import accounts as accounts_blueprint
    app.register_blueprint(accounts_blueprint, url_prefix="/accounts")

    return app

