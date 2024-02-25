import logging
from telegram import Update, ChatMember
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import openai

# Set your Telegram bot token and OpenAI API key
TELEGRAM_BOT_TOKEN = 'ADD YOUR TELEGRAM BOT TOKEN'
OPENAI_API_KEY = 'ADD YOUR OPEN AI API KEY'

# Set the chat ID of the specified group for verification
TARGET_GROUP_ID = -1001907508879  # Replace with your actual group chat ID

# Set up the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to determine if the bot should respond
chat_enabled = False

# Define the chat start command
def chat_start(update: Update, context: CallbackContext) -> None:
    global chat_enabled

    # Check if the user is a member of the specified group
    user_id = update.message.from_user.id
    try:
        chat_member = context.bot.get_chat_member(TARGET_GROUP_ID, user_id)
        if chat_member.status not in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR, ChatMember.MEMBER]:
            update.message.reply_text('Sorry, you must be a member of the Japura DIT Onsite group to use this bot.')
            return
    except Exception as e:
        logger.error(f"Error checking user membership: {e}")
        update.message.reply_text('Sorry, an error occurred while checking your membership. Please try again later.')
        return

    # If the user is a member, enable the chat
    chat_enabled = True
    update.message.reply_text('Welcome🙏 I am your personal AI companion 🤖. How may I assist you today?')

# Define the chat stop command
def chat_stop(update: Update, context: CallbackContext) -> None:
    global chat_enabled
    chat_enabled = False
    update.message.reply_text('Goodbye!👋 Is there anything specific you need assistance with? I am always ready.😉')

# Define the chat message handler
def chat(update: Update, context: CallbackContext) -> None:
    global chat_enabled
    # Check if the bot should respond
    if not chat_enabled:
        return

    user_message = update.message.text

    # Send a loading emoji while generating the response
    loading_message = update.message.reply_text('🤗')

    try:
        # Determine the model based on context or user preference
        selected_model = "gpt-3.5-turbo"  # Default to GPT-3.5 Turbo
        if context.user_data.get('use_gpt4', False):
            selected_model = "gpt-4"  # Use GPT-4 if specified

        # Generate the response
        response = openai.ChatCompletion.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ]
        )
        ai_reply = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"Error generating response from OpenAI: {e}")
        ai_reply = "Sorry, I encountered an error while processing your request."

    # Delete the loading message
    loading_message.delete()

    # Send the AI-generated response back to the user
    update.message.reply_text(ai_reply)

# Set up the main function
def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler(["start", "chat"], chat_start))
    dp.add_handler(CommandHandler("stopchat", chat_stop))

    # Register message handler for chat
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
