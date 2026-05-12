from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app.models import Site, Expense, ClientPayment, WorkEntry, Labour
from app import db

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@login_required
def home():
    sites = Site.query.all()
    total_sites = len(sites)

    expense_sums = dict(
        db.session.query(
            Expense.site_id,
            func.sum(Expense.amount)
        ).group_by(Expense.site_id).all()
    )

    payment_sums = dict(
        db.session.query(
            ClientPayment.site_id,
            func.sum(ClientPayment.amount)
        ).group_by(ClientPayment.site_id).all()
    )

    labour_sums = dict(
        db.session.query(
            WorkEntry.site_id,
            func.sum(WorkEntry.hours * Labour.hourly_rate)
        ).join(
            Labour, WorkEntry.labour_id == Labour.id
        ).group_by(WorkEntry.site_id).all()
    )

    total_expenses = sum(expense_sums.values()) or 0
    total_payments = sum(payment_sums.values()) or 0

    dashboard_sites = []

    for site in sites:
        expense_total = float(expense_sums.get(site.id) or 0)
        payment_total = float(payment_sums.get(site.id) or 0)
        labour_total = float(labour_sums.get(site.id) or 0)
        total_cost = expense_total + labour_total
        profit = payment_total - total_cost
        remaining = float(site.contract_amount or 0) - payment_total

        dashboard_sites.append({
            "site": site,
            "expenses": expense_total,
            "labour": labour_total,
            "payments": payment_total,
            "profit": profit,
            "remaining": remaining
        })

    return render_template(
        "dashboard.html",
        total_sites=total_sites,
        total_expenses=round(float(total_expenses), 2),
        total_payments=round(float(total_payments), 2),
        dashboard_sites=dashboard_sites
    )
