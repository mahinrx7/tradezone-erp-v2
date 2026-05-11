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

from datetime import datetime

import pandas as pd

import os

from io import BytesIO

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


expenses = Blueprint(
    "expenses",
    __name__
)


@expenses.route("/expenses")
@login_required
def view_expenses():

    site_id = request.args.get("site_id")

    start_date = request.args.get("start_date")

    end_date = request.args.get("end_date")

    expense_query = Expense.query

    labour_query = Labour.query

    if site_id and site_id != "all":

        expense_query = expense_query.filter_by(
            site_id=site_id
        )

        labour_query = labour_query.filter_by(
            site_id=site_id
        )

    if start_date and end_date:

        expense_query = expense_query.filter(
            Expense.date >= start_date,
            Expense.date <= end_date
        )

        labour_query = labour_query.filter(
            Labour.date >= start_date,
            Labour.date <= end_date
        )

    expenses_data = expense_query.all()

    labour_data = labour_query.all()

    combined_expenses = []

    for expense in expenses_data:

        combined_expenses.append({

            "id": expense.id,

            "site": expense.site.name
            if expense.site else "",

            "category": expense.category,

            "description": expense.description,

            "amount": expense.amount,

            "date": expense.date
        })

    for worker in labour_data:

        combined_expenses.append({

            "id": worker.id,

            "site": worker.site.name
            if worker.site else "",

            "category": "Labour",

            "description": worker.worker_name,

            "amount": worker.total_amount,

            "date": worker.date
        })

    total_expense = sum(
        item["amount"]
        for item in combined_expenses
    )

    labour_total = sum(
        worker.total_amount
        for worker in labour_data
    )

    sites = Site.query.all()

    return render_template(

        "expenses.html",

        expenses=combined_expenses,

        total_expense=total_expense,

        labour_total=labour_total,

        sites=sites
    )


@expenses.route(
    "/add_expense",
    methods=["GET", "POST"]
)
@login_required
def add_expense():

    sites = Site.query.all()

    if request.method == "POST":

        receipt_file = request.files.get(
            "receipt"
        )

        filename = None

        if receipt_file and receipt_file.filename:

            upload_folder = os.path.join(
                "app",
                "static",
                "receipts"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            filename = (
                str(datetime.now().timestamp())
                + "_"
                + receipt_file.filename
            )

            receipt_path = os.path.join(
                upload_folder,
                filename
            )

            receipt_file.save(
                receipt_path
            )

        expense = Expense(

            site_id=request.form["site_id"],

            category=request.form["category"],

            description=request.form["description"],

            amount=request.form["amount"],

            date=request.form["date"],

            receipt=filename
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

            "Amount (BD)":
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

        worksheet = writer.sheets[
            "Expenses"
        ]

        for cell in worksheet[1]:

            cell.font = cell.font.copy(
                bold=True
            )

            cell.fill = (
                cell.fill.copy(
                    fill_type="solid",
                    start_color="1F2937"
                )
            )

        for column in worksheet.columns:

            max_length = 0

            column_letter = (
                column[0].column_letter
            )

            for cell in column:

                try:

                    if len(
                        str(cell.value)
                    ) > max_length:

                        max_length = len(
                            str(cell.value)
                        )

                except:
                    pass

            adjusted_width = (
                max_length + 5
            )

            worksheet.column_dimensions[
                column_letter
            ].width = adjusted_width

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name="expenses_report.xlsx",

        mimetype=(
            "application/"
            "vnd.openxmlformats-"
            "officedocument."
            "spreadsheetml.sheet"
        )
    )


@expenses.route(
    "/export_expenses_pdf"
)
@login_required
def export_expenses_pdf():

    expenses_data = Expense.query.all()

    output = BytesIO()

    doc = SimpleDocTemplate(

        output,

        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(

        "Tradezone ERP Expense Report",

        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    table_data = [[

        "Site",

        "Category",

        "Description",

        "Amount",

        "Date"
    ]]

    for expense in expenses_data:

        table_data.append([

            expense.site.name
            if expense.site else "",

            expense.category,

            expense.description,

            f"BD {expense.amount}",

            str(expense.date)
        ])

    table = Table(
        table_data
    )

    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.black
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                12
            )
        ])
    )

    elements.append(table)

    doc.build(elements)

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name="expenses_report.pdf",

        mimetype="application/pdf"
    )