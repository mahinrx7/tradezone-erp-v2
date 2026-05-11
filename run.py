from app import create_app, db

from app.models import User

from flask_bcrypt import Bcrypt


app = create_app()

bcrypt = Bcrypt(app)


with app.app_context():

    db.create_all()

    # CREATE ADMIN IF NOT EXISTS
    existing = User.query.filter_by(
        username="mahmood"
    ).first()

    if not existing:

        admin = User(

            username="mahmood",

            password=bcrypt.generate_password_hash(
                "mahmood123"
            ).decode("utf-8"),

            role="admin"
        )

        db.session.add(admin)

        db.session.commit()


if __name__ == "__main__":

    app.run(debug=True)