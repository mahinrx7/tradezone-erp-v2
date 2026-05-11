from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash
)

from app.models import User

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

auth = Blueprint(
    "auth",
    __name__
)


# LOGIN
@auth.route("/login", methods=["GET", "POST"])
def login():

    # already logged in
    if current_user.is_authenticated:

        return redirect("/")


    # ONLY when form submitted
    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        user = User.query.filter_by(
            username=username
        ).first()


        # CORRECT LOGIN
        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect("/")


        # WRONG LOGIN
        flash(
            "Incorrect username or password"
        )


    return render_template(
        "login.html"
    )


# LOGOUT
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")