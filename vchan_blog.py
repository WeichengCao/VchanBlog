from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_principal import Principal
from defines import *

db = MongoEngine()
login_manager = LoginManager()
principal = Principal()

def create_app():
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static",
                )
    app.config.from_object(DevConfig)

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


@login_manager.user_loader
def load_user(username):
    import account.models
    try:
        user = account.models.CUser.objects.get(username=username)
    except:
        user = None
    return user


if __name__ == '__main__':
    app = create_app()
    app.run()
