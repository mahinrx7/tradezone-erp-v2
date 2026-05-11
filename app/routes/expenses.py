from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import send_file

from flask_login import login_required

from app import db

from app.models import Expense
from app.models import Site
from app.models import Labour

import pandas as pd

from io import BytesIO


expenses = Blueprint(
    "expenses",
    __name__
)


@expenses.route("/expenses")
@login_required
def view_expenses():

    expenses_data = Expense.query.all()

    labour_data = Labour.query.all()

    sites = Site.query.all()

    total_expense = sum(
        float(expense.amount or 0)
        for expense in expenses_data
    )

    labour_total = sum(
        float(worker.hourly_rate or 0)
        for worker in labour_data
    )

    net_total = (
        total_expense +
        labour_total
    )

    return render_template(

        "expenses.html",

        expenses=expenses_data,

        labour_data=labour_data,

        sites=sites,

        total_expense=total_expense,

        labour_total=labour_total,

        net_total=net_total
    )


@expenses.route(
    "/add_expense",
    methods=["GET", "POST"]
)
@login_required
def add_expense():

    sites = Site.query.all()

    if request.method == "POST":

        expense = Expense(

            site_id=request.form["site_id"],

            category=request.form["category"],

            description=request.form["description"],

            amount=request.form["amount"],

            date=request.form["date"]
        )

        db.session.add(expense)

        db.session.commit()

        flash(
            "Expense added successfully"
        )

        return redirect(
            url_for(
                "expenses.view_expenses"
            )
        )

    return render_template(

        "add_expense.html",

        sites=sites
    )


@expenses.route(
    "/delete_expense/<int:expense_id>"
)
@login_required
def delete_expense(expense_id):

    expense = Expense.query.get_or_404(
        expense_id
    )

    db.session.delete(expense)

    db.session.commit()

    flash(
        "Expense deleted successfully"
    )

    return redirect(
        url_for(
            "expenses.view_expenses"
        )
    )


@expenses.route(
    "/export_expenses_excel"
)
@login_required
def export_expenses_excel():

    expenses_data = Expense.query.all()

    data = []

    for expense in expenses_data:

        data.append({

            "Site":
            expense.site.name
            if expense.site else "",

            "Category":
            expense.category,

            "Description":
            expense.description,

            "Amount":
            expense.amount,

            "Date":
            expense.date
        })

    df = pd.DataFrame(data)

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Expenses"
        )

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name="expenses.xlsx",

        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )