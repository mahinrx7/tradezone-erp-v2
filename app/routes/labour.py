from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)

from app import db

from app.models import Labour

labour = Blueprint(
    "labour",
    __name__
)


# VIEW LABOUR
@labour.route("/labour")
def view_labour():

    all_labour = Labour.query.all()

    return render_template(
        "labour.html",
        labour=all_labour
    )


# ADD LABOUR
@labour.route(
    "/add_labour",
    methods=["GET", "POST"]
)
def add_labour():

    if request.method == "POST":

        worker = Labour(

            name=request.form["name"],

            specialization=request.form["specialization"],

            hourly_rate=request.form["hourly_rate"]
        )

        db.session.add(worker)

        db.session.commit()

        return redirect("/labour")

    return render_template(
        "add_labour.html"
    )


# DELETE LABOUR
@labour.route("/delete_labour/<int:id>")
def delete_labour(id):

    worker = Labour.query.get_or_404(id)

    db.session.delete(worker)

    db.session.commit()

    return redirect("/labour")


# EDIT LABOUR
@labour.route(
    "/edit_labour/<int:id>",
    methods=["GET", "POST"]
)
def edit_labour(id):

    worker = Labour.query.get_or_404(id)

    if request.method == "POST":

        worker.name = request.form["name"]

        worker.specialization = request.form["specialization"]

        worker.hourly_rate = request.form["hourly_rate"]

        db.session.commit()

        return redirect("/labour")

    return render_template(
        "edit_labour.html",
        worker=worker
    )