from flask import (
    Blueprint,
    render_template,
    send_file,
    redirect
)

from flask_login import (
    login_required,
    current_user
)

from app.models import (
    db,
    Site,
    Expense,
    Labour,
    WorkEntry,
    ClientPayment,
    User
)

import json
import tempfile
from datetime import datetime


backup = Blueprint(
    "backup",
    __name__
)


@backup.route("/backup")
@login_required
def backup_page():

    if current_user.role != "admin":
        return redirect("/")

    # Gather stats
    stats = {
        "sites": Site.query.count(),
        "expenses": Expense.query.count(),
        "labour": Labour.query.count(),
        "work_entries": WorkEntry.query.count(),
        "payments": ClientPayment.query.count(),
        "users": User.query.count(),
    }

    return render_template(
        "backup.html",
        stats=stats
    )


@backup.route("/download_backup")
@login_required
def download_backup():

    if current_user.role != "admin":
        return redirect("/")

    data = {
        "backup_date": datetime.now().isoformat(),
        "version": "tradezone_erp_v2",
    }

    # SITES
    data["sites"] = []
    for s in Site.query.all():
        data["sites"].append({
            "id": s.id,
            "name": s.name,
            "client_name": s.client_name,
            "contract_amount": s.contract_amount,
            "created_at": str(s.created_at) if s.created_at else None,
        })

    # EXPENSES
    data["expenses"] = []
    for e in Expense.query.all():
        data["expenses"].append({
            "id": e.id,
            "site_id": e.site_id,
            "category": e.category,
            "description": e.description,
            "amount": e.amount,
            "date": str(e.date) if e.date else None,
            "receipt_image": e.receipt_image,
            "created_at": str(e.created_at) if e.created_at else None,
        })

    # LABOUR
    data["labour"] = []
    for l in Labour.query.all():
        data["labour"].append({
            "id": l.id,
            "name": l.name,
            "specialization": l.specialization,
            "hourly_rate": l.hourly_rate,
        })

    # WORK ENTRIES
    data["work_entries"] = []
    for w in WorkEntry.query.all():
        data["work_entries"].append({
            "id": w.id,
            "labour_id": w.labour_id,
            "site_id": w.site_id,
            "hours": w.hours,
            "date": str(w.date) if w.date else None,
            "created_at": str(w.created_at) if w.created_at else None,
        })

    # PAYMENTS
    data["payments"] = []
    for p in ClientPayment.query.all():
        data["payments"].append({
            "id": p.id,
            "site_id": p.site_id,
            "amount": p.amount,
            "notes": p.notes,
            "date": str(p.date) if p.date else None,
            "created_at": str(p.created_at) if p.created_at else None,
        })

    # USERS (without passwords for security)
    data["users"] = []
    for u in User.query.all():
        data["users"].append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "assigned_site_id": u.assigned_site_id,
        })

    # Write to temp file
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".json",
        mode="w"
    )

    json.dump(data, tmp, indent=2, ensure_ascii=False)
    tmp.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name=f"tradezone_backup_{timestamp}.json"
    )
