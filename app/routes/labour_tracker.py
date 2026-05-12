from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app.models import WorkEntry, Labour, Site

labour_tracker = Blueprint("labour_tracker", __name__)


@labour_tracker.route("/labour_tracker")
@login_required
def view_labour_tracker():
    labour_id = request.args.get("labour_id")
    site_id = request.args.get("site_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = WorkEntry.query.options(
        joinedload(WorkEntry.labour),
        joinedload(WorkEntry.site)
    )

    if labour_id and labour_id != "all":
        query = query.filter(WorkEntry.labour_id == labour_id)
    if site_id and site_id != "all":
        query = query.filter(WorkEntry.site_id == site_id)
    if start_date:
        query = query.filter(WorkEntry.date >= start_date)
    if end_date:
        query = query.filter(WorkEntry.date <= end_date)

    entries = query.order_by(WorkEntry.id.desc()).all()

    total_hours = sum(float(e.hours or 0) for e in entries)
    total_cost = 0.0
    for e in entries:
        if e.labour:
            total_cost += float(e.hours or 0) * float(e.labour.hourly_rate or 0)

    labours = Labour.query.order_by(Labour.name).all()
    sites = Site.query.order_by(Site.name).all()

    return render_template(
        "labour_tracker.html",
        entries=entries,
        labours=labours,
        sites=sites,
        total_hours=total_hours,
        total_cost=total_cost,
        total_entries=len(entries)
    )
