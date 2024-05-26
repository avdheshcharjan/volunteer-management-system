from flask import request, jsonify, current_app
from . import db
from .models import Organization, Admin, Volunteer, Recipient, Assignment, clear_all_tables
import string
import random
from datetime import datetime, timedelta
import logging 

logger = logging.getLogger(__name__)

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
        phone_number=data['phone_number'],
        capabilities=data['capabilities']
    )
    db.session.add(new_volunteer)
    db.session.commit()
    return jsonify({'message': 'Signup successful! You are now registered as a volunteer. You can indicate your availability using the command: /indicate_availability.'})

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
    )
    db.session.add(new_recipient)
    db.session.commit()
    return jsonify({'message': 'Signup successful! You have been registered as a recipient. You can indicate your needs date using the command: /update_needs'})

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
        for volunteer in available_volunteers:
            logger.debug(f"Capababilities: {volunteer.capabilities}")
        return jsonify({
            'available_volunteers': [
                {
                    'name': volunteer.name,
                    'capabilities': volunteer.capabilities
                } 
                for volunteer in available_volunteers
            ]
        })
    return jsonify({'message': 'No available volunteers found!'})

def find_available_volunteers(date, time, org_id):
    volunteers = Volunteer.query.filter_by(org_id=org_id).all()
    available_volunteers = []
    for volunteer in volunteers:
        logger.debug(f'Volunteer: {volunteer}')
        if is_available(volunteer, date, time):
            available_volunteers.append(volunteer)
    return available_volunteers

def is_available(volunteer, date_str, time_str):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    time = datetime.strptime(time_str, '%H:%M').time()
    availability = volunteer.availability
    logger.debug(f'Availability: {availability}')
    if date_str in availability:
        available_times = availability[date_str]
        for period in available_times:
            start_time_str, end_time_str = period.split('-')
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
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
    time_range = data['time']  # Expected format: "10:00-11:00"

    recipient = Recipient.query.filter_by(name=recipient_name).first()
    volunteer = Volunteer.query.filter_by(name=volunteer_name).first()
    
    if not recipient:
        return jsonify({'message': 'Recipient not found!'}), 404
    
    if not volunteer:
        return jsonify({'message': 'Volunteer not found!'}), 404

    # Convert date string to date object and time range to time objects
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    start_time_str, end_time_str = time_range.split('-')
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()

    new_assignment = Assignment(
        recipient_id=recipient.recipient_id,
        volunteer_id=volunteer.volunteer_id,
        date=date,
        time=start_time,
        status='Pending'
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({
        'message': 'Volunteer assigned successfully!',
        'date': date_str,
        'time': time_range,
        'volunteer_telegram_user_id': volunteer.telegram_user_id,
        'recipient_telegram_user_id': recipient.telegram_user_id
    })


@current_app.route('/show_unattended', methods=['GET'])
def show_unattended():
    all_recipients = Recipient.query.all()
    unattended_recipients = []

    for recipient in all_recipients:
        logger.debug(f"Processing recipient: {recipient.name}")
        logger.debug(f"Availability: {recipient.availability}")
        unattended_availability = {}

        for date_str, time_slots in recipient.availability.items():
            logger.debug(f"Processing date: {date_str}, time_slots: {time_slots}")
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            for time_slot in time_slots:
                try:
                    logger.debug(f"Processing time_slot: {time_slot}")
                    start_time_str, end_time_str = time_slot.split('-')
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()

                    # Find all assignments for the recipient on the given date
                    assignments = Assignment.query.filter_by(
                        recipient_id=recipient.recipient_id,
                        date=date
                    ).all()
                    logger.debug(f"Assignments on {date_str}: {assignments}")

                    # Calculate unattended slots
                    current_start = start_time
                    while current_start < end_time:
                        slot_start = current_start
                        slot_end = (datetime.combine(datetime.today(), current_start) + timedelta(hours=1)).time()
                        if slot_end > end_time:
                            slot_end = end_time

                        # Check if this slot is assigned
                        is_assigned = any(
                            assignment.time == slot_start and assignment.time < slot_end
                            for assignment in assignments
                        )
                        logger.debug(f"Checking slot {slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}: Assigned={is_assigned}")

                        if not is_assigned:
                            unattended_slot = f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                            if date_str not in unattended_availability:
                                unattended_availability[date_str] = []
                            unattended_availability[date_str].append(unattended_slot)

                        current_start = slot_end

                except Exception as e:
                    logger.error(f"Error processing time_slot '{time_slot}' for recipient '{recipient.name}' on date '{date_str}': {e}")

        if unattended_availability:
            unattended_recipients.append({
                'name': recipient.name,
                'unattended_availability': unattended_availability,
                'needs': recipient.help_needed
            })

    logger.debug(f"Unattended_recipients: {unattended_recipients}")

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
