from . import db
from sqlalchemy.dialects.postgresql import JSON

class Organization(db.Model):
    __tablename__ = 'organizations'
    org_id = db.Column(db.Integer, primary_key=True)
    admin_telegram_user_id = db.Column(db.String(100), nullable=False, unique=True)
    organization_code = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    volunteer_id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.String(100), nullable=False, unique=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    availability = db.Column(JSON, nullable=True)
    capabilities = db.Column(JSON, nullable=True)

class Recipient(db.Model):
    __tablename__ = 'recipients'
    recipient_id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.String(100), nullable=False, unique=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    help_needed = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipients.recipient_id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.volunteer_id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
