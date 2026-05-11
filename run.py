from app import create_app, db

from app.models import *

from flask_bcrypt import Bcrypt


app = create_app()

bcrypt = Bcrypt(app)


with app.app_context():

    db.drop_all()

    db.create_all()


    existing = User.query.filter_by(
        username="mahmood"
    ).first()

    if not existing:

        admin = User(

            username="mahmood",

            password=bcrypt.generate_password_hash(
                "tradezone786"
            ).decode("utf-8"),

            role="admin"
        )

        db.session.add(admin)

        db.session.commit()


if __name__ == "__main__":

    app.run(debug=True)