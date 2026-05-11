from flask import Blueprint, render_template, request, redirect, send_file
from flask_login import login_required
from app.models import db, Expense, Site, WorkEntry, Labour
from datetime import datetime
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
import os

expenses = Blueprint("expenses", __name__)


@expenses.route("/expenses")
@login_required
def view_expenses():

    site_id = request.args.get("site_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Expense.query

    if site_id and site_id != "all":
        query = query.filter_by(site_id=site_id)

    if start_date:
        query = query.filter(
            Expense.date >= datetime.strptime(start_date, "%Y-%m-%d").date()
        )

    if end_date:
        query = query.filter(
            Expense.date <= datetime.strptime(end_date, "%Y-%m-%d").date()
        )

    expenses_data = query.order_by(Expense.id.desc()).all()

    work_query = WorkEntry.query

    if site_id and site_id != "all":
        work_query = work_query.filter_by(site_id=site_id)

    work_entries = work_query.all()

    total_expense = sum(
        float(expense.amount or 0)
        for expense in expenses_data
    )

    labour_total = sum(
        float(entry.hours or 0) *
        float(entry.labour.hourly_rate or 0)
        for entry in work_entries
        if entry.labour
    )

    net_total = total_expense + labour_total

    sites = Site.query.all()

    return render_template(
        "expenses.html",
        expenses=expenses_data,
        sites=sites,
        total_expense=total_expense,
        labour_total=labour_total,
        net_total=net_total
    )


@expenses.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():

    if request.method == "POST":

        receipt = request.files.get("receipt")

        filename = None

        if receipt and receipt.filename != "":

            os.makedirs("app/static/receipts", exist_ok=True)

            filename = (
                str(datetime.now().timestamp()).replace(".", "")
                + "_"
                + receipt.filename
            )

            receipt.save(
                os.path.join("app/static/receipts", filename)
            )

        expense = Expense(
            site_id=request.form["site_id"],
            category=request.form["category"],
            description=request.form["description"],
            amount=request.form["amount"],
            date=datetime.strptime(
                request.form["date"],
                "%Y-%m-%d"
            ).date(),
            receipt_image=filename
        )

        db.session.add(expense)
        db.session.commit()

        return redirect("/expenses")

    sites = Site.query.all()

    return render_template(
        "add_expense.html",
        sites=sites
    )


@expenses.route("/delete_expense/<int:id>")
@login_required
def delete_expense(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect("/expenses")


@expenses.route("/export_expenses_excel")
@login_required
def export_expenses_excel():

    expenses_data = Expense.query.all()

    data = []

    for expense in expenses_data:

        data.append({
            "Site": expense.site.name if expense.site else "",
            "Category": expense.category,
            "Description": expense.description,
            "Amount": expense.amount,
            "Date": str(expense.date)
        })

    df = pd.DataFrame(data)

    file_path = "expenses.xlsx"

    df.to_excel(file_path, index=False)

    return send_file(
        file_path,
        as_attachment=True
    )


@expenses.route("/export_expenses_pdf")
@login_required
def export_expenses_pdf():

    expenses_data = Expense.query.all()

    file_path = "expenses.pdf"

    pdf = SimpleDocTemplate(
        file_path,
        pagesize=letter
    )

    data = [[
        "Site",
        "Category",
        "Description",
        "Amount",
        "Date"
    ]]

    for expense in expenses_data:

        data.append([
            expense.site.name if expense.site else "",
            expense.category,
            expense.description,
            str(expense.amount),
            str(expense.date)
        ])

    table = Table(data)

    pdf.build([table])

    return send_file(
        file_path,
        as_attachment=True
    )