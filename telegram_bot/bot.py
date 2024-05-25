import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the backend API URL
API_URL = 'http://localhost:5000'
BOT_TOKEN = '7112686723:AAH9pPTv_e_T_NNiCM5RGOS6MzXiZe_QTrw'

def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! Welcome to the Volunteer Management Bot.')

def register_org(update: Update, context: CallbackContext) -> None:
    admin_telegram_user_id = update.message.from_user.id
    org_name = context.args[0]
    contact_person = context.args[1]
    email = context.args[2]
    phone_number = context.args[3]
    description = ' '.join(context.args[4:])

    payload = {
        'admin_telegram_user_id': admin_telegram_user_id,
        'name': org_name,
        'contact_person': contact_person,
        'email': email,
        'phone_number': phone_number,
        'description': description,
        'admin_name': update.message.from_user.full_name,
        'admin_email': email,
        'admin_password': 'default_password'  # In a real app, handle password securely
    }

    response = requests.post(f'{API_URL}/register_org', json=payload)
    data = response.json()
    update.message.reply_text(f"Organization registered successfully! Your organization code is: {data['organization_code']}")

def volunteer_signup(update: Update, context: CallbackContext) -> None:
    telegram_user_id = update.message.from_user.id
    org_code = context.args[0]
    name = update.message.from_user.full_name
    email = context.args[1]
    phone_number = context.args[2]

    payload = {
        'telegram_user_id': telegram_user_id,
        'organization_code': org_code,
        'name': name,
        'email': email,
        'phone_number': phone_number
    }

    response = requests.post(f'{API_URL}/volunteer_signup', json=payload)
    update.message.reply_text(response.json()['message'])

def indicate_availability(update: Update, context: CallbackContext) -> None:
    telegram_user_id = update.message.from_user.id
    availability = ' '.join(context.args)

    payload = {
        'telegram_user_id': telegram_user_id,
        'availability': availability
    }

    response = requests.post(f'{API_URL}/indicate_availability', json=payload)
    update.message.reply_text(response.json()['message'])

def recipient_signup(update: Update, context: CallbackContext) -> None:
    telegram_user_id = update.message.from_user.id
    org_code = context.args[0]
    name = update.message.from_user.full_name
    email = context.args[1]
    phone_number = context.args[2]
    help_needed = ' '.join(context.args[3:])
    date = context.args[-2]
    time = context.args[-1]

    payload = {
        'telegram_user_id': telegram_user_id,
        'organization_code': org_code,
        'name': name,
        'email': email,
        'phone_number': phone_number,
        'help_needed': help_needed,
        'date': date,
        'time': time
    }

    response = requests.post(f'{API_URL}/recipient_signup', json=payload)
    data = response.json()
    update.message.reply_text(data['message'])

    # Notify admin
    notify_admin_of_signup(data['admin_telegram_user_id'], data['recipient_name'], data['date'], data['time'], data['help_needed'], context)

def notify_admin_of_signup(admin_telegram_user_id, recipient_name, date, time, help_needed, context):
    message = f"New recipient signup: {recipient_name} needs help on {date} at {time}. Help needed: {help_needed}"
    context.bot.send_message(chat_id=admin_telegram_user_id, text=message)

def update_needs(update: Update, context: CallbackContext) -> None:
    telegram_user_id = update.message.from_user.id
    date = context.args[0]
    time = context.args[1]

    payload = {
        'telegram_user_id': telegram_user_id,
        'date': date,
        'time': time
    }

    response = requests.post(f'{API_URL}/update_needs', json=payload)
    update.message.reply_text(response.json()['message'])

def get_available_volunteers(update: Update, context: CallbackContext) -> None:
    org_id = context.args[0]
    date = context.args[1]
    time = context.args[2]

    payload = {
        'org_id': org_id,
        'date': date,
        'time': time
    }

    response = requests.post(f'{API_URL}/get_available_volunteers', json=payload)
    update.message.reply_text(response.json().get('available_volunteers', response.json().get('message', 'No available volunteers found')))

def assign(update: Update, context: CallbackContext) -> None:
    recipient_name = context.args[0]
    volunteer_name = context.args[1]

    payload = {
        'recipient_name': recipient_name,
        'volunteer_name': volunteer_name
    }

    response = requests.post(f'{API_URL}/assign', json=payload)
    data = response.json()
    update.message.reply_text(data['message'])

    if 'Volunteer assigned successfully!' in data['message']:
        # Notify volunteer and recipient
        notify_assignment(data['volunteer_telegram_user_id'], data['recipient_telegram_user_id'], recipient_name, volunteer_name, data['date'], data['time'], context)

def notify_assignment(volunteer_telegram_user_id, recipient_telegram_user_id, recipient_name, volunteer_name, date, time, context):
    volunteer_message = f"You have been assigned to help {recipient_name} on {date} at {time}."
    recipient_message = f"{volunteer_name} has been assigned to assist you on {date} at {time}."
    context.bot.send_message(chat_id=volunteer_telegram_user_id, text=volunteer_message)
    context.bot.send_message(chat_id=recipient_telegram_user_id, text=recipient_message)

def show_unattended(update: Update, _: CallbackContext) -> None:
    response = requests.get(f'{API_URL}/unattended_recipients')
    data = response.json()
    unattended = data.get('unattended_recipients', [])
    if unattended:
        reply = "Unattended recipients:\n"
        for rec in unattended:
            reply += f"- {rec['name']}: {rec['date']} at {rec['time']}\n"
    else:
        reply = data.get('message', 'All recipients are attended to.')
    update.message.reply_text(reply)

def clear_db(update: Update, context: CallbackContext) -> None:
    admin_telegram_user_id = update.message.from_user.id

    payload = {
        'admin_telegram_user_id': admin_telegram_user_id
    }

    response = requests.post(f'{API_URL}/clear_db', json=payload)
    update.message.reply_text(response.json()['message'])

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register_org", register_org))
    dispatcher.add_handler(CommandHandler("volunteer_signup", volunteer_signup))
    dispatcher.add_handler(CommandHandler("indicate_availability", indicate_availability))
    dispatcher.add_handler(CommandHandler("beneficiary_signup", recipient_signup))
    dispatcher.add_handler(CommandHandler("update_needs", update_needs))
    dispatcher.add_handler(CommandHandler("get_available_volunteers", get_available_volunteers))
    dispatcher.add_handler(CommandHandler("assign", assign))
    dispatcher.add_handler(CommandHandler("show_unattended", show_unattended))
    dispatcher.add_handler(CommandHandler("clear_db", clear_db))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
