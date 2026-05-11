from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import login_required

from app.models import (
    Expense,
    Site,
    WorkEntry
)

from sqlalchemy import func

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import io
import base64


analytics = Blueprint(
    "analytics",
    __name__
)


@analytics.route("/analytics")
@login_required
def analytics_page():

    site_id = request.args.get("site_id")

    start_date = request.args.get("start_date")

    end_date = request.args.get("end_date")

    sites = Site.query.all()

    query = Expense.query


    # SITE FILTER
    if site_id:

        query = query.filter(
            Expense.site_id == site_id
        )


    # CUSTOM DATE FILTER
    if start_date and end_date:

        query = query.filter(
            Expense.date >= start_date,
            Expense.date <= end_date
        )


    expenses = query.all()


    categories = {}


    # NORMAL EXPENSES
    for expense in expenses:

        if expense.category not in categories:

            categories[expense.category] = 0

        categories[expense.category] += float(expense.amount or 0)


    # LABOUR COST
    labour_entries = WorkEntry.query.all()

    labour_total = 0

    for entry in labour_entries:

        if entry.labour is None:
            continue

        if site_id:

            if str(entry.site_id) != str(site_id):

                continue

        labour_total += (

            float(entry.hours or 0) *
            float(entry.labour.hourly_rate or 0)
        )


    if labour_total > 0:

        categories["Labour"] = labour_total


    # Handle empty data
    chart = ""

    if categories:

        labels = list(categories.keys())

        values = list(categories.values())

        # CREATE CHART
        fig, ax = plt.subplots(figsize=(7, 5))

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            textprops={"fontsize": 11}
        )

        ax.set_title(
            "Expense Distribution",
            fontsize=14,
            fontweight="bold",
            pad=20
        )

        fig.tight_layout()

        img = io.BytesIO()

        fig.savefig(
            img,
            format="png",
            dpi=150,
            bbox_inches="tight",
            facecolor="white"
        )

        img.seek(0)

        chart = base64.b64encode(
            img.getvalue()
        ).decode()

        plt.close(fig)


    return render_template(

        "analytics.html",

        chart=chart,

        sites=sites
    )
