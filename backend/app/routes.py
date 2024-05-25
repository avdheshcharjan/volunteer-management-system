from flask import request, jsonify, current_app
from . import db
from .models import Organization, Admin, Volunteer, Recipient, Assignment

@current_app.route('/signup_volunteer', methods=['POST'])
def signup_volunteer():
    data = request.get_json()
    organization_code = data['organization_code']
    org = Organization.query.filter_by(organization_code=organization_code).first()
    if not org:
        return jsonify({'message': 'Organization not found!'}), 404

    new_volunteer = Volunteer(
        telegram_user_id=data['telegram_user_id'],
        org_id=org.org_id,
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number']
    )
    db.session.add(new_volunteer)
    db.session.commit()
    return jsonify({'message': 'Volunteer signed up successfully!'})

@current_app.route('/update_availability', methods=['POST'])
def update_availability():
    data = request.get_json()
    volunteer = Volunteer.query.filter_by(telegram_user_id=data['telegram_user_id']).first()
    if not volunteer:
        return jsonify({'message': 'Volunteer not found!'}), 404

    volunteer.availability = data['availability']
    db.session.commit()
    return jsonify({'message': 'Availability updated successfully!'})

@current_app.route('/signup_recipient', methods=['POST'])
def signup_recipient():
    data = request.get_json()
    organization_code = data['organization_code']
    org = Organization.query.filter_by(organization_code=organization_code).first()
    if not org:
        return jsonify({'message': 'Organization not found!'}), 404

    new_recipient = Recipient(
        telegram_user_id=data['telegram_user_id'],
        org_id=org.org_id,
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number'],
        help_needed=data['help_needed'],
        date=data['date'],
        time=data['time']
    )
    db.session.add(new_recipient)
    db.session.commit()
    notify_admin_of_signup(new_recipient)
    return jsonify({'message': 'Recipient signed up successfully!'})

def notify_admin_of_signup(recipient):
    admin = Admin.query.filter_by(org_id=recipient.org_id).first()
    if admin:
        message = f"New recipient signup: {recipient.name} needs help on {recipient.date} at {recipient.time}. Help needed: {recipient.help_needed}"
        send_message_to_admin(admin, message)

def send_message_to_admin(admin, message):
    # Logic to send message to admin's Telegram chat
    pass

@current_app.route('/get_available_volunteers', methods=['POST'])
def get_available_volunteers():
    data = request.get_json()
    org_id = data['org_id']
    date = data['date']
    time = data['time']

    available_volunteers = find_available_volunteers(date, time, org_id)
    if available_volunteers:
        return jsonify({'available_volunteers': [volunteer.name for volunteer in available_volunteers]})
    return jsonify({'message': 'No available volunteers found!'})

@current_app.route('/assign_volunteer', methods=['POST'])
def assign_volunteer():
    data = request.get_json()
    recipient = Recipient.query.filter_by(recipient_id=data['recipient_id']).first()
    if not recipient:
        return jsonify({'message': 'Recipient not found!'}), 404

    volunteer = Volunteer.query.filter_by(volunteer_id=data['volunteer_id']).first()
    if not volunteer:
        return jsonify({'message': 'Volunteer not found!'}), 404

    new_assignment = Assignment(
        recipient_id=recipient.recipient_id,
        volunteer_id=volunteer.volunteer_id,
        status='Pending'
    )
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({'message': 'Volunteer assigned successfully!', 'volunteer': volunteer.name})

@current_app.route('/unattended_recipients', methods=['GET'])
def unattended_recipients():
    unattended = db.session.query(Recipient).outerjoin(Assignment, Recipient.recipient_id == Assignment.recipient_id).filter(Assignment.recipient_id == None).all()
    if unattended:
        return jsonify({'unattended_recipients': [{'name': recipient.name, 'date': recipient.date, 'time': recipient.time} for recipient in unattended]})
    return jsonify({'message': 'All recipients are attended to.'})

def find_available_volunteers(date, time, org_id):
    volunteers = Volunteer.query.filter_by(org_id=org_id).all()
    available_volunteers = []
    for volunteer in volunteers:
        if is_available(volunteer, date, time):
            available_volunteers.append(volunteer)
    return available_volunteers

def is_available(volunteer, date, time):
    availability = volunteer.availability
    day_of_week = date.strftime('%A').lower()
    if day_of_week in availability:
        available_times = availability[day_of_week]
        for period in available_times:
            start_time, end_time = period.split('-')
            if start_time <= time <= end_time:
                return True
    return False

