from flask import request, jsonify, current_app
from . import db
from .models import Organization, Admin, Volunteer, Recipient, Assignment, clear_all_tables
import string
import random
from datetime import datetime

def generate_org_code(length=8):
    """Generate a unique organization code."""
    letters_and_digits = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(letters_and_digits) for _ in range(length))
        if not Organization.query.filter_by(organization_code=code).first():
            return code

@current_app.route('/register_org', methods=['POST'])
def register_org():
    data = request.get_json()
    new_org_code = generate_org_code()

    new_org = Organization(
        admin_telegram_user_id=data['admin_telegram_user_id'],
        organization_code=new_org_code,
        name=data['name'],
        contact_person=data['contact_person'],
        email=data['email'],
        phone_number=data['phone_number'],
        description=data['description']
    )
    db.session.add(new_org)
    db.session.commit()

    new_admin = Admin(
        org_id=new_org.org_id,
        name=data['admin_name'],
        email=data['admin_email'],
        telegram_user_id=data['admin_telegram_user_id']
    )
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Organization created successfully!', 'organization_code': new_org_code})

@current_app.route('/volunteer_signup', methods=['POST'])
def volunteer_signup():
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
    return jsonify({'message': 'Signup successful! You are now registered as a volunteer. You can indicate your availability using the command: /indicate_availability. Format: {"monday": ["10:00-14:00"], "tuesday": ["09:00-17:00"]}'})

@current_app.route('/indicate_availability', methods=['POST'])
def indicate_availability():
    data = request.get_json()
    volunteer = Volunteer.query.filter_by(telegram_user_id=data['telegram_user_id']).first()
    if not volunteer:
        return jsonify({'message': 'Volunteer not found!'}), 404

    availability = data['availability']
    # Ask for confirmation logic could be handled on the client-side before sending the final request
    volunteer.availability = availability
    db.session.commit()
    return jsonify({'message': 'Your availability has been updated successfully!'})

@current_app.route('/recipient_signup', methods=['POST'])
def recipient_signup():
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
        availability=data['availability']
    )
    db.session.add(new_recipient)
    db.session.commit()
    return jsonify({'message': 'Signup successful! You have been registered as a recipient.'})

@current_app.route('/update_needs', methods=['POST'])
def update_needs():
    data = request.get_json()
    recipient = Recipient.query.filter_by(telegram_user_id=data['telegram_user_id']).first()
    if not recipient:
        return jsonify({'message': 'Recipient not found!'}), 404

    recipient.availability = data['availability']
    db.session.commit()
    return jsonify({'message': 'Your needs date has been updated successfully!'})

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

def find_available_volunteers(date, time, org_id):
    volunteers = Volunteer.query.filter_by(org_id=org_id).all()
    available_volunteers = []
    for volunteer in volunteers:
        if is_available(volunteer, date, time):
            available_volunteers.append(volunteer)
    return available_volunteers

def is_available(volunteer, date_str, time_str):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    time = datetime.strptime(time_str, '%H:%M').time()
    availability = volunteer.availability

    # Check if the volunteer is available on the given date and time
    day_of_week = date.strftime('%A').lower()
    if day_of_week in availability:
        available_times = availability[day_of_week]
        for period in available_times:
            start_time, end_time = period.split('-')
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
            if start_time <= time <= end_time:
                # Check if the volunteer is already assigned during this time
                if not is_assigned(volunteer, date, time):
                    return True
    return False

def is_assigned(volunteer, date, time):
    assignments = Assignment.query.filter_by(volunteer_id=volunteer.volunteer_id, date=date).all()
    for assignment in assignments:
        if assignment.time == time:
            return True
    return False

@current_app.route('/assign', methods=['POST'])
def assign():
    data = request.get_json()
    recipient_name = data['recipient_name']
    volunteer_name = data['volunteer_name']
    date_str = data['date']
    time_str = data['time']

    recipient = Recipient.query.filter_by(name=recipient_name).first()
    volunteer = Volunteer.query.filter_by(name=volunteer_name).first()
    
    if not recipient:
        return jsonify({'message': 'Recipient not found!'}), 404
    
    if not volunteer:
        return jsonify({'message': 'Volunteer not found!'}), 404

    # Convert date and time strings to datetime objects
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    time = datetime.strptime(time_str, '%H:%M').time()

    new_assignment = Assignment(
        recipient_id=recipient.recipient_id,
        volunteer_id=volunteer.volunteer_id,
        date=date,
        time=time,
        status='Pending'
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'message': 'Volunteer assigned successfully!', 'date': date_str, 'time': time_str})

@current_app.route('/show_unattended', methods=['GET'])
def show_unattended():
    all_recipients = Recipient.query.all()
    unattended_recipients = []

    for recipient in all_recipients:
        recipient_unattended = False
        for date_str, time_slots in recipient.availability.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            for time_slot in time_slots:
                start_time_str, end_time_str = list(time_slot.items())[0]
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
                # Check if there is any assignment for this recipient at the given date and time
                assignments = Assignment.query.filter_by(
                    recipient_id=recipient.recipient_id,
                    date=date,
                    time=start_time  # Assuming assignments are stored with start_time
                ).all()
                
                if not assignments:
                    recipient_unattended = True
                    break

            if recipient_unattended:
                unattended_recipients.append({
                    'name': recipient.name,
                    'date': date_str,
                    'time_slot': time_slot
                })
                break

    if unattended_recipients:
        return jsonify({'unattended_recipients': unattended_recipients})
    else:
        return jsonify({'message': 'All recipients are attended to.'})

@current_app.route('/clear_db', methods=['POST'])
def clear_db():
    data = request.get_json()
    admin_telegram_user_id = data.get('admin_telegram_user_id')

    # Verify if the requester is an admin
    admin = Admin.query.filter_by(telegram_user_id=admin_telegram_user_id).first()
    if not admin:
        return jsonify({'message': 'Unauthorized access!'}), 403

    try:
        clear_all_tables()
        return jsonify({'message': 'All tables cleared successfully!'})
    except Exception as e:
        return jsonify({'message': f'Error clearing tables: {str(e)}'}), 500
