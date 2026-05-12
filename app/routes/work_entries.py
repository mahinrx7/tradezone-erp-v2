from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)

from flask_login import login_required

from sqlalchemy.orm import joinedload

from app import db

from app.models import (
    WorkEntry,
    Labour,
    Site
)

from datetime import datetime

work_entries = Blueprint(
    "work_entries",
    __name__
)


# VIEW WORK ENTRIES
@work_entries.route("/work_entries")
@login_required
def view_work_entries():

    entries = WorkEntry.query.options(
        joinedload(WorkEntry.labour),
        joinedload(WorkEntry.site)
    ).order_by(
        WorkEntry.id.desc()
    ).all()

    labour = Labour.query.all()

    sites = Site.query.all()

    return render_template(
        "work_entries.html",
        entries=entries,
        labour=labour,
        sites=sites
    )


# ADD WORK ENTRY
@work_entries.route(
    "/add_work_entry",
    methods=["POST"]
)
@login_required
def add_work_entry():

    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    t1 = datetime.strptime(start_time, "%H:%M")
    t2 = datetime.strptime(end_time, "%H:%M")
    diff = (t2 - t1).total_seconds() / 3600.0
    if diff < 0:
        diff += 24
    hours = round(diff, 2)

    entry = WorkEntry(
        labour_id=request.form["labour_id"],
        site_id=request.form["site_id"],
        hours=hours,
        start_time=start_time,
        end_time=end_time,
        date=request.form["date"]
    )

    db.session.add(entry)

    db.session.commit()

    return redirect("/work_entries")


# DELETE WORK ENTRY
@work_entries.route(
    "/delete_work_entry/<int:id>"
)
@login_required
def delete_work_entry(id):

    entry = WorkEntry.query.get_or_404(id)

    db.session.delete(entry)

    db.session.commit()

    return redirect("/work_entries")
