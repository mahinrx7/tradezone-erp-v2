from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)

from flask_login import login_required

from app import db

from app.models import Site

sites = Blueprint(
    "sites",
    __name__
)


# VIEW SITES
@sites.route("/sites")
@login_required
def view_sites():

    all_sites = Site.query.all()

    return render_template(
        "sites.html",
        sites=all_sites
    )


# ADD SITE
@sites.route(
    "/add_site",
    methods=["GET", "POST"]
)
@login_required
def add_site():

    if request.method == "POST":

        name = request.form["name"]

        client_name = request.form["client_name"]

        contract_amount = request.form["contract_amount"]

        new_site = Site(

            name=name,

            client_name=client_name,

            contract_amount=contract_amount
        )

        db.session.add(new_site)

        db.session.commit()

        return redirect("/sites")

    return render_template(
        "add_site.html"
    )


# DELETE SITE
@sites.route("/delete_site/<int:id>")
@login_required
def delete_site(id):

    site = Site.query.get_or_404(id)

    db.session.delete(site)

    db.session.commit()

    return redirect("/sites")


# EDIT SITE
@sites.route(
    "/edit_site/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_site(id):

    site = Site.query.get_or_404(id)

    if request.method == "POST":

        site.name = request.form["name"]

        site.client_name = request.form["client_name"]

        site.contract_amount = request.form["contract_amount"]

        db.session.commit()

        return redirect("/sites")

    return render_template(
        "edit_site.html",
        site=site
    )
