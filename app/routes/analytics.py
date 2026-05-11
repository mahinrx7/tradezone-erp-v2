from flask import (
    Blueprint,
    render_template,
    request
)

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

        categories[expense.category] += expense.amount


    # LABOUR COST
    labour_entries = WorkEntry.query.all()

    labour_total = 0

    for entry in labour_entries:

        if site_id:

            if str(entry.site_id) != str(site_id):

                continue

        labour_total += (

            entry.hours *
            entry.labour.hourly_rate
        )


    if labour_total > 0:

        categories["Labour"] = labour_total


    labels = list(categories.keys())

    values = list(categories.values())


    # CREATE CHART
    plt.figure(figsize=(7,5))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%"
    )

    plt.title(
        "Expense Distribution"
    )

    img = io.BytesIO()

    plt.savefig(
        img,
        format="png",
        bbox_inches="tight"
    )

    img.seek(0)

    chart = base64.b64encode(
        img.getvalue()
    ).decode()

    plt.close()

    return render_template(

        "analytics.html",

        chart=chart,

        sites=sites
    )