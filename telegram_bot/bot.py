import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import requests
import json 
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the backend API URL and bot token
API_URL = 'http://localhost:5000'
BOT_TOKEN = '7112686723:AAH9pPTv_e_T_NNiCM5RGOS6MzXiZe_QTrw'

# Define conversation states
ORG_DETAILS, VOLUNTEER_DETAILS, RECIPIENT_DETAILS, VOLUNTEER_AVAILABILITY, NEEDS_DETAILS = range(5)

# Define command handlers
async def start(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text('Hello! Welcome to the Volunteer Management Bot.')

async def register_org(update: Update, _: CallbackContext) -> int:
    await update.message.reply_text('Please provide the following details in this format:\n'
                              'Organization Name\n'
                              'Contact Person Name\n'
                              'Email\n'
                              'Phone Number\n'
                              'Description')
    return ORG_DETAILS

async def handle_org_details(update: Update, context: CallbackContext) -> int:
    details = update.message.text.split('\n')
    if len(details) < 5:
        await update.message.reply_text('Please provide all the details in the correct format.')
        return ORG_DETAILS

    org_name, contact_person, email, phone_number, description = details
    data = {
        "admin_telegram_user_id": update.message.from_user.id,
        "name": org_name,
        "contact_person": contact_person,
        "email": email,
        "phone_number": phone_number,
        "description": description,
        "admin_name": update.message.from_user.full_name,
        "admin_email": email
    }

    response = requests.post(f'{API_URL}/register_org', json=data)
    if response.status_code == 200:
        org_code = response.json().get('organization_code')
        await update.message.reply_text(f'Organization created successfully! Your organization code is {org_code}')
    else:
        await update.message.reply_text('Error creating organization. Please try again.')

    return ConversationHandler.END

async def volunteer_signup(update: Update, _: CallbackContext) -> int:
    await update.message.reply_text('Please provide the following details in this format:\n'
                              'Organization Code\n'
                              'Your name\n'
                              'Your Email\n'
                              'Your Phone Number')
    return VOLUNTEER_DETAILS

async def handle_volunteer_details(update: Update, context: CallbackContext) -> int:
    details = update.message.text.split('\n')
    if len(details) < 4:
        await update.message.reply_text('Please provide all the details in the correct format.')
        return VOLUNTEER_DETAILS

    org_code,name, email, phone_number = details
    data = {
        "telegram_user_id": str(update.message.from_user.id),
        "organization_code": org_code,
        "name": name,
        "email": email,
        "phone_number": phone_number
    }

    response = requests.post(f'{API_URL}/volunteer_signup', json=data)
    await update.message.reply_text(response.json()['message'])
    return ConversationHandler.END

async def indicate_availability(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text('Please provide your availability in this format:\n'
                              'Date Time-Slot Time-Slot ...\n\n'
                              'Example:\n'
                              '2024-09-01 10:00-11:00 12:00-13:00\n'
                              '2024-09-02 09:00-10:00\n\n'
                              'Separate multiple slots with spaces.')
    return VOLUNTEER_AVAILABILITY

async def handle_volunteer_availability(update: Update, context: CallbackContext) -> int:
    telegram_user_id = str(update.message.from_user.id)
    try:
        raw_data = update.message.text.split('\n')
        availability = {}
        for line in raw_data:
            parts = line.split()
            date = parts[0]
            time_slots = [time_slot for time_slot in parts[1:]]
            availability[date] = time_slots
    except Exception as e:
        await update.message.reply_text('Invalid format. Please try again.')
        return VOLUNTEER_AVAILABILITY

    payload = {
        'telegram_user_id': telegram_user_id,
        'availability': availability
    }

    response = requests.post(f'{API_URL}/indicate_availability', json=payload)
    await update.message.reply_text(response.json()['message'])
    return ConversationHandler.END

async def recipient_signup(update: Update, _: CallbackContext) -> int:
    await update.message.reply_text('Please provide the following details in this format:\n'
                              'Organization Code\n'
                              'Your Name\n'
                              'Your Email\n'
                              'Your Phone Number\n'
                              'Help Needed')
    return RECIPIENT_DETAILS

async def handle_recipient_details(update: Update, context: CallbackContext) -> int:
    details = update.message.text.split('\n')
    if len(details) < 5:
        await update.message.reply_text('Please provide all the details in the correct format.')
        return RECIPIENT_DETAILS

    org_code, name, email, phone_number, help_needed = details
    data = {
        "telegram_user_id": str(update.message.from_user.id),
        "organization_code": org_code,
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "help_needed": help_needed,
    }

    response = requests.post(f'{API_URL}/recipient_signup', json=data)
    await update.message.reply_text(response.json()['message'])
    return ConversationHandler.END

async def update_needs(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text('Please provide your updated needs in this format:\n'
                              'Date Time-Slot Time-Slot ...\n\n'
                              'Example:\n'
                              '2024-09-01 10:00-11:00 12:00-13:00\n'
                              '2024-09-02 09:00-10:00\n\n'
                              'Separate multiple slots with spaces.')
    return NEEDS_DETAILS

async def handle_needs_details(update: Update, context: CallbackContext) -> int:
    telegram_user_id = str(update.message.from_user.id)
    try:
        raw_data = update.message.text.split('\n')
        availability = {}
        for line in raw_data:
            parts = line.split()
            date = parts[0]
            time_slots = [time_slot for time_slot in parts[1:]]
            availability[date] = time_slots
    except Exception as e:
        await update.message.reply_text('Invalid format. Please try again.')
        return NEEDS_DETAILS

    payload = {
        'telegram_user_id': telegram_user_id,
        'availability': availability
    }

    response = requests.post(f'{API_URL}/update_needs', json=payload)
    await update.message.reply_text(response.json()['message'])
    return ConversationHandler.END

async def get_available_volunteers(update: Update, context: CallbackContext) -> None:
    org_id = context.args[0]
    date = context.args[1]
    time = context.args[2]

    data = {
        'org_id': org_id,
        'date': date,
        'time': time
    }

    response = requests.post(f'{API_URL}/get_available_volunteers', json=data)
    result = response.json()
    available_volunteers = result.get('available_volunteers', [])
    if available_volunteers:
        await update.message.reply_text('\n'.join(available_volunteers))
    else:
        await update.message.reply_text(result.get('message', 'No available volunteers found.'))

async def assign(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 5:
        await update.message.reply_text('Please provide the following details in the format:\n'
                                  'Recipient Name Volunteer Name Date Time-Range\n\n'
                                  'Example:\n'
                                  'Alice Brown John Smith 2024-09-01 10:00-11:00')
        return

    recipient_name = context.args[0]
    volunteer_name = context.args[1]
    date_str = context.args[2]
    time_range = context.args[3]

    data = {
        'recipient_name': recipient_name,
        'volunteer_name': volunteer_name,
        'date': date_str,
        'time': time_range
    }

    response = requests.post(f'{API_URL}/assign', json=data)
    result = response.json()
    await update.message.reply_text(result['message'])

    if 'Volunteer assigned successfully!' in result['message']:
        # Notify volunteer and recipient
        notify_assignment(result['volunteer_telegram_user_id'], result['recipient_telegram_user_id'], recipient_name, volunteer_name, date_str, time_range, context)

async def notify_assignment(volunteer_telegram_user_id, recipient_telegram_user_id, recipient_name, volunteer_name, date, time_range, context):
    volunteer_message = f"You have been assigned to help {recipient_name} on {date} during {time_range}."
    recipient_message = f"{volunteer_name} has been assigned to assist you on {date} during {time_range}."
    await context.bot.send_message(chat_id=int(volunteer_telegram_user_id), text=volunteer_message)
    await context.bot.send_message(chat_id=int(recipient_telegram_user_id), text=recipient_message)

async def show_unattended(update: Update, _: CallbackContext) -> None:
    response = requests.get(f'{API_URL}/show_unattended')
    result = response.json()
    unattended = result.get('unattended_recipients', [])
    if unattended:
        reply = "Unattended recipients:\n"
        for rec in unattended:
            reply += f"- {rec['name']}:\n"
            for date, time_slots in rec['unattended_availability'].items():
                reply += f"  {date}: {', '.join(time_slots)}\n"
    else:
        reply = result.get('message', 'All recipients are attended to.')
    await update.message.reply_text(reply)


async def clear_db(update: Update, context: CallbackContext) -> None:
    admin_telegram_user_id = str(update.message.from_user.id)

    data = {
        'admin_telegram_user_id': admin_telegram_user_id
    }

    response = requests.post(f'{API_URL}/clear_db', json=data)
    await update.message.reply_text(response.json()['message'])

async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("register_org", register_org))
    # application.add_handler(CommandHandler("volunteer_signup", volunteer_signup))
    # application.add_handler(CommandHandler("indicate_availability", indicate_availability))
    # application.add_handler(CommandHandler("recipient_signup", recipient_signup))
    # application.add_handler(CommandHandler("update_needs", update_needs))
    application.add_handler(CommandHandler("get_available_volunteers", get_available_volunteers))
    application.add_handler(CommandHandler("assign", assign))
    application.add_handler(CommandHandler("show_unattended", show_unattended))
    application.add_handler(CommandHandler("clear_db", clear_db))

    # Add conversation handlers
    conv_handler_org = ConversationHandler(
        entry_points=[CommandHandler('register_org', register_org)],
        states={
            ORG_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_org_details)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_org)

    conv_handler_volunteer = ConversationHandler(
        entry_points=[CommandHandler('volunteer_signup', volunteer_signup)],
        states={
            VOLUNTEER_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_volunteer_details)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_volunteer)

    conv_handler_recipient = ConversationHandler(
        entry_points=[CommandHandler('beneficiary_signup', recipient_signup)],
        states={
            RECIPIENT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recipient_details)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_recipient)

    conv_handler_availability = ConversationHandler(
        entry_points=[CommandHandler('indicate_availability', indicate_availability)],
        states={
            VOLUNTEER_AVAILABILITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_volunteer_availability)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_availability)

    conv_handler_needs = ConversationHandler(
        entry_points=[CommandHandler('update_needs', update_needs)],
        states={
            NEEDS_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_needs_details)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_needs)

    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
