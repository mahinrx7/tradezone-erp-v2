from app import create_app, db

from app.models import User

from flask_bcrypt import Bcrypt


app = create_app()

bcrypt = Bcrypt()


with app.app_context():

    existing = User.query.filter_by(
        username="admin"
    ).first()

    if not existing:

        user = User(

            username="mahmood",

            password=bcrypt.generate_password_hash(
                "mahmood123"
            ).decode("utf-8"),

            role="admin"
        )

        db.session.add(user)

        db.session.commit()

        print("Admin Created")

    else:

        print("Admin already exists")