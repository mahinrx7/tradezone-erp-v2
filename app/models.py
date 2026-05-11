from app import db

from flask_login import UserMixin

from datetime import datetime


# USER MODEL
class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="supervisor"
    )

    assigned_site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id")
    )

    assigned_site = db.relationship(
        "Site"
    )


# SITE MODEL
class Site(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    client_name = db.Column(
        db.String(200),
        nullable=False
    )

    contract_amount = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# LABOUR MODEL
class Labour(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    specialization = db.Column(
        db.String(100)
    )

    hourly_rate = db.Column(
        db.Float,
        default=0
    )


# WORK ENTRY MODEL
class WorkEntry(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    labour_id = db.Column(
        db.Integer,
        db.ForeignKey("labour.id")
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id")
    )

    hours = db.Column(
        db.Float,
        default=0
    )

    date = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    labour = db.relationship(
        "Labour"
    )

    site = db.relationship(
        "Site"
    )


# EXPENSE MODEL
class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id")
    )

    category = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.String(500)
    )

    amount = db.Column(
        db.Float,
        default=0
    )

    date = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    receipt_image = db.Column(
        db.String(300)
    )

    site = db.relationship(
        "Site"
    )


# CLIENT PAYMENT MODEL
class ClientPayment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.id")
    )

    amount = db.Column(
        db.Float,
        default=0
    )

    notes = db.Column(
        db.String(500)
    )

    date = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    site = db.relationship(
        "Site"
    )