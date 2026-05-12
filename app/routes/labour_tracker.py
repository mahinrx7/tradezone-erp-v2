from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app.models import WorkEntry, Labour, Site
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile


labour_tracker = Blueprint("labour_tracker", __name__)


def get_filtered_entries():
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
    return entries


@labour_tracker.route("/labour_tracker")
@login_required
def view_labour_tracker():
    entries = get_filtered_entries()

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


@labour_tracker.route("/export_labour_tracker_pdf")
@login_required
def export_labour_tracker_pdf():
    entries = get_filtered_entries()

    total_hours = sum(float(e.hours or 0) for e in entries)
    total_cost = 0.0
    for e in entries:
        if e.labour:
            total_cost += float(e.hours or 0) * float(e.labour.hourly_rate or 0)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    pdf = SimpleDocTemplate(tmp.name, pagesize=landscape(letter))

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_text = "Labour Tracker Report"
    elements.append(Paragraph(title_text, styles["Title"]))
    elements.append(Spacer(1, 6))

    # Filter info
    filters = []
    labour_id = request.args.get("labour_id")
    site_id = request.args.get("site_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if labour_id and labour_id != "all":
        lab = Labour.query.get(labour_id)
        if lab:
            filters.append("Labour: " + lab.name)
    if site_id and site_id != "all":
        s = Site.query.get(site_id)
        if s:
            filters.append("Site: " + s.name)
    if start_date:
        filters.append("From: " + start_date)
    if end_date:
        filters.append("To: " + end_date)
    if filters:
        elements.append(Paragraph("Filters: " + " | ".join(filters), styles["Normal"]))
    else:
        elements.append(Paragraph("Showing all entries", styles["Normal"]))
    elements.append(Spacer(1, 4))

    # Summary
    summary = "Total Entries: %d | Total Hours: %.1f | Total Cost: BD %.2f" % (
        len(entries), total_hours, total_cost
    )
    elements.append(Paragraph(summary, styles["Normal"]))
    elements.append(Spacer(1, 14))

    # Table
    data = [["#", "Labour", "Specialization", "Site", "Time", "Hours", "Date", "Rate", "Cost"]]
    for i, e in enumerate(entries, 1):
        labour_name = e.labour.name if e.labour else "-"
        spec = e.labour.specialization if e.labour else "-"
        site_name = e.site.name if e.site else "-"
        time_range = ""
        if e.start_time and e.end_time:
            time_range = e.start_time + " - " + e.end_time
        else:
            time_range = "-"
        hrs = "%.1f" % float(e.hours or 0)
        date_str = str(e.date) if e.date else "-"
        rate = "BD %.2f/hr" % float(e.labour.hourly_rate or 0) if e.labour else "-"
        cost = "BD %.2f" % (float(e.hours or 0) * float(e.labour.hourly_rate or 0)) if e.labour else "-"
        data.append([str(i), labour_name, spec or "-", site_name, time_range, hrs, date_str, rate, cost])

    table = Table(data, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("ALIGN", (5, 0), (5, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ])
    table.setStyle(style)
    elements.append(table)

    pdf.build(elements)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name="labour_tracker_report.pdf"
    )
