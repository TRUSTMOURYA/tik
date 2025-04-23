
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import time
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = 'YOUR_API_TOKEN'
admin_user_ids = ['YOUR_ADMIN_USER_IDS']

user_access = {}
abusive_users = {}
panga_users = {}
admin_offline = True
offline_message = "Mai abhi offline hoon, please wait! Mai jaldi online ho jaunga."

def is_admin(user_id):
    return str(user_id) in admin_user_ids

def handle_admin_offline(update, context):
    user_id = update.message.from_user.id
    if update.message.chat.type == 'private' and admin_offline:
        update.message.reply_text(f"Admin is currently offline. {offline_message}")

def start(update, context):
    user_id = update.message.from_user.id
    if user_id not in user_access or user_access[user_id] < time.time():
        update.message.reply_text("Aapko access ke liye pehle admin se approval lena hoga. Please contact admin to get access.")
    else:
        update.message.reply_text("Welcome! Aapko access mil gaya hai. Bot ko use karne ke liye aap commands ka istemal kar sakte hain.")

def add(update, context):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text("Aap admin nahi hain, isliye yeh command nahi chala sakte.")
        return

    if len(context.args) != 3:
        update.message.reply_text("Usage: /add <user_id> <days> <hours>")
        return

    try:
        target_user_id = int(context.args[0])
        days = int(context.args[1])
        hours = int(context.args[2])
        expiration_time = time.time() + (days * 86400) + (hours * 3600)
        user_access[target_user_id] = expiration_time
        update.message.reply_text(f"User {target_user_id} ko access de diya gaya hai. Access expires in {days} days and {hours} hours.")
    except ValueError:
        update.message.reply_text("Invalid input! Please ensure <user_id>, <days>, and <hours> are valid integers.")

def remove(update, context):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text("Aap admin nahi hain, isliye yeh command nahi chala sakte.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /remove <user_id>")
        return

    try:
        target_user_id = int(context.args[0])
        if target_user_id in user_access:
            del user_access[target_user_id]
            update.message.reply_text(f"User {target_user_id} ka access hata diya gaya hai.")
        else:
            update.message.reply_text(f"User {target_user_id} ka access nahi tha.")
    except ValueError:
        update.message.reply_text("Invalid input! Please ensure <user_id> is a valid integer.")

def check_access(update, context):
    user_id = update.message.from_user.id
    if user_id not in user_access or user_access[user_id] < time.time():
        update.message.reply_text("Aapko access ke liye pehle admin se approval lena hoga. Please contact admin to get access.")
    else:
        update.message.reply_text("Aapka access valid hai. Ab aap bot use kar sakte hain.")

def offline(update, context):
    update.message.reply_text(offline_message)

def handle_abuse(update, context):
    user_id = update.message.from_user.id
    message_text = update.message.text.lower()
    abusive_words = ['gali', 'behen', 'bhenchod', 'gand', 'kutte']
    if any(word in message_text for word in abusive_words):
        if user_id not in abusive_users:
            abusive_users[user_id] = []
        abusive_users[user_id].append(message_text)
        update.message.reply_text("Aapne abusive language ka use kiya hai. Ab aapko sabhi logon ke saamne galiyan milengi.")
        for _ in range(3):
            update.message.reply_text("Aapne galiya di hai. Aapko reply milega... " + "Behenchod!" * 5)
    else:
        update.message.reply_text("Aapke message mein koi gali nahi thi.")

def add_admin(update, context):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text("Aap admin nahi hain, isliye yeh command nahi chala sakte.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /add_admin <new_admin_user_id>")
        return

    try:
        new_admin_id = int(context.args[0])
        if len(admin_user_ids) < 10:
            admin_user_ids.append(str(new_admin_id))
            update.message.reply_text(f"New admin {new_admin_id} ko add kar diya gaya hai.")
        else:
            update.message.reply_text("Max limit of 10 admins reached.")
    except ValueError:
        update.message.reply_text("Invalid input! Please ensure <new_admin_user_id> is a valid integer.")

def panga(update, context):
    user_id = update.message.from_user.id
    if len(context.args) != 1:
        update.message.reply_text("Usage: /panga <username>")
        return

    target_username = context.args[0]
    if target_username not in panga_users:
        panga_users[target_username] = 0
    panga_users[target_username] += 1
    update.message.reply_text(f"@{target_username} ko panga diya gaya hai. Total panga: {panga_users[target_username]}")
    for _ in range(panga_users[target_username] * 2):
        update.message.reply_text(f"@{target_username} Abusive reply!")

def handle_reactions(update, context):
    if update.message.chat.type == 'channel' and update.message.chat.id in admin_user_ids:
        reactions = ['☠️', '🔥', '💊️']
        for reaction in reactions:
            update.message.reply_text(f"Reaction: {reaction}")

def handle_error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("check_access", check_access))
    application.add_handler(CommandHandler("offline", offline))
    application.add_handler(CommandHandler("add_admin", add_admin))
    application.add_handler(CommandHandler("panga", panga))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_abuse))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_offline))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, handle_reactions))
    
    application.run_polling()

if __name__ == '__main__':
    main()
