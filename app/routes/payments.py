from flask import Blueprint, render_template, request, redirect
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app import db
from app.models import ClientPayment, Site

payments = Blueprint("payments", __name__)


@payments.route("/payments")
@login_required
def view_payments():
    payments_list = ClientPayment.query.options(
        joinedload(ClientPayment.site)
    ).order_by(ClientPayment.id.desc()).all()

    sites = Site.query.all()
    return render_template("payments.html", payments=payments_list, sites=sites)


@payments.route("/add_payment", methods=["POST"])
@login_required
def add_payment():
    payment = ClientPayment(
        site_id=request.form["site_id"],
        amount=request.form["amount"],
        notes=request.form["notes"],
        date=request.form["date"]
    )
    db.session.add(payment)
    db.session.commit()
    return redirect("/payments")


@payments.route("/delete_payment/<int:id>")
@login_required
def delete_payment(id):
    payment = ClientPayment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return redirect("/payments")
