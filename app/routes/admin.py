from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)

from flask_login import (
    login_required,
    current_user
)

from flask_bcrypt import Bcrypt

from app.models import User

from app import db


bcrypt = Bcrypt()

admin = Blueprint(
    "admin",
    __name__
)


# ADMIN PANEL
@admin.route("/admin")
@login_required
def admin_panel():

    if current_user.role != "admin":

        return redirect("/")

    users = User.query.all()

    return render_template(

        "admin.html",

        users=users
    )


# ADD SUPERVISOR
@admin.route("/add_supervisor", methods=["POST"])
@login_required
def add_supervisor():

    if current_user.role != "admin":

        return redirect("/")

    username = request.form["username"]

    password = request.form["password"]

    existing = User.query.filter_by(
        username=username
    ).first()

    if existing:

        return redirect("/admin")

    user = User(

        username=username,

        password=bcrypt.generate_password_hash(
            password
        ).decode("utf-8"),

        role="supervisor"
    )

    db.session.add(user)

    db.session.commit()

    return redirect("/admin")


# DELETE USER
@admin.route("/delete_user/<int:id>")
@login_required
def delete_user(id):

    if current_user.role != "admin":

        return redirect("/")


    user = User.query.get(id)


    # PREVENT DELETE OWN ACCOUNT
    if user.id == current_user.id:

        return redirect("/admin")


    db.session.delete(user)

    db.session.commit()

    return redirect("/admin")