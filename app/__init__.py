from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from dotenv import load_dotenv

import os


load_dotenv()


db = SQLAlchemy()

login_manager = LoginManager()


def create_app():

    app = Flask(__name__)


    # ENV CONFIG
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY"
    )


    database_url = os.getenv(
        "DATABASE_URL"
    )


    # RAILWAY FIX
    if database_url and database_url.startswith("postgres://"):

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )


    # DATABASE
    app.config["SQLALCHEMY_DATABASE_URI"] = (

        database_url

        if database_url

        else "sqlite:///tradezone.db"
    )


    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # UPLOADS
    app.config["UPLOAD_FOLDER"] = os.path.join(
        "app",
        "static",
        "uploads"
    )


    db.init_app(app)


    # LOGIN
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"


    from app.models import User


    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )


    # BLUEPRINTS
    from app.routes.dashboard import dashboard

    from app.routes.sites import sites

    from app.routes.expenses import expenses

    from app.routes.labour import labour

    from app.routes.work_entries import work_entries

    from app.routes.payments import payments

    from app.routes.analytics import analytics

    from app.routes.auth import auth

    from app.routes.admin import admin

    from app.routes.backup import backup


    # REGISTER
    app.register_blueprint(dashboard)

    app.register_blueprint(sites)

    app.register_blueprint(expenses)

    app.register_blueprint(labour)

    app.register_blueprint(work_entries)

    app.register_blueprint(payments)

    app.register_blueprint(analytics)

    app.register_blueprint(auth)

    app.register_blueprint(admin)

    app.register_blueprint(backup)


    return app