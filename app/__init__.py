from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_compress import Compress
from flask_caching import Cache
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
compress = Compress()
cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url if database_url else "sqlite:///tradezone.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if database_url:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 5,
            "max_overflow": 10,
        }

    app.config["UPLOAD_FOLDER"] = os.path.join("app", "static", "uploads")
    app.config["COMPRESS_MIMETYPES"] = ["text/html", "text/css", "application/javascript", "application/json"]
    app.config["COMPRESS_LEVEL"] = 6
    app.config["COMPRESS_MIN_SIZE"] = 500
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400

    db.init_app(app)
    compress.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

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

    @app.route("/health")
    def health():
        return "ok", 200

    return app
