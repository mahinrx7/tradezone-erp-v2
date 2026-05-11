from flask import (
    Blueprint,
    render_template
)

from sqlalchemy import func

from app.models import (
    Site,
    Expense,
    ClientPayment,
    WorkEntry
)

from app import db

dashboard = Blueprint(
    "dashboard",
    __name__
)


@dashboard.route("/")
def home():

    sites = Site.query.all()

    total_sites = Site.query.count()

    total_expenses = db.session.query(
        func.sum(Expense.amount)
    ).scalar() or 0

    total_payments = db.session.query(
        func.sum(ClientPayment.amount)
    ).scalar() or 0

    dashboard_sites = []

    for site in sites:

        # EXPENSES
        expense_total = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.site_id == site.id
        ).scalar() or 0


        # PAYMENTS
        payment_total = db.session.query(
            func.sum(ClientPayment.amount)
        ).filter(
            ClientPayment.site_id == site.id
        ).scalar() or 0


        # LABOUR COST
        work_entries = WorkEntry.query.filter_by(
            site_id=site.id
        ).all()

        labour_total = 0

        for entry in work_entries:

            labour_total += (
                entry.hours *
                entry.labour.hourly_rate
            )


        # TOTAL COST
        total_cost = expense_total + labour_total


        # PROFIT
        profit = payment_total - total_cost


        # REMAINING
        remaining = (
            site.contract_amount -
            payment_total
        )


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

        total_expenses=round(
            total_expenses,
            2
        ),

        total_payments=round(
            total_payments,
            2
        ),

        dashboard_sites=dashboard_sites
    )