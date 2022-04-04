import os

import bcrypt
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    if not os.path.isdir(os.path.join(app.instance_path, "Campaigns")):
        os.makedirs(os.path.join(app.instance_path,
                    "Campaigns"), exist_ok=True)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/db.sqlite'.format(
        app.instance_path)

    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path,  'Campaigns')
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for the campaign manager parts of the app
    from .campaignmanager import campaignmanager as campaignmanager_blueprint
    app.register_blueprint(campaignmanager_blueprint)

    from .responsemanager import responsemanager as responsemanager_blueprint
    app.register_blueprint(responsemanager_blueprint)

    # blueprint for email manager parts of the app
    # blueprint for email manager parts of the app
    from .emailmanager import emailmanager as emailmanager_blueprint
    app.register_blueprint(emailmanager_blueprint)

    return app


app = create_app()
db.create_all(app=app)