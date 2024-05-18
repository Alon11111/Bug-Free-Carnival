from typing import Final
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import requests


TOKEN: Final = '6399303462:AAG5ZuSbRYo1P6A88NLBilsL7Oj3MZKZZck'
BOT_USERNAME: Final = '@CriticalFail_Bot'

# USER_LATI = None
# USER_LONG = None

RESTAURANT = {
 "Fat Cow": "fat-cow",
"Greco": "deli-by-greco",
"Silly Kid": "silly-kid",
"Souplier": "souplier",
}

start_flag = False
chosen_restaurant = None
chosen_lati = None
chosen_long = None

# Functions
def extract_lat_long(message):
    LOCATION_REGEX = r'(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)'
    match = re.search(LOCATION_REGEX, message.strip())
    if match:
        # Extracting latitude and longitude
        latitude = float(match.group(1))
        longitude = float(match.group(3))
        return latitude, longitude
    else:
        return False

def check_open_status(restaurant, latitude, longitude):
    url = f"https://consumer-api.wolt.com/order-xp/web/v1/venue/slug/{restaurant}/dynamic/?lat={latitude}&lon={longitude}"
    
    global chosen_restaurant
    chosen_restaurant= None
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            is_open = data["venue"]["delivery_open_status"]["is_open"]
            return is_open
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global start_flag
    start_flag = True
    keyboard = [[restaurant_name] for restaurant_name in RESTAURANT.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(f"Hey {update.message.from_user.first_name}! Which restaurant should we check for you?", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Currently im a WoltBot! It might change from time to time but for now, please type "/start" and choose restaurant so I can check and tell you if its open or closed!')


# async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text('This is a custom command!')

# async def following_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Great! What is your current location?")


# Responses
    
def handle_response(text: str) -> str:
    global start_flag, chosen_restaurant, chosen_lati, chosen_long        

    if (start_flag == True) and (text in RESTAURANT):
        chosen_restaurant = RESTAURANT[text]
        start_flag = False
        return "Great! What is your current location?"
        # start_flag = False
        # return check_open_status(RESTAURANT[text])
    
    if (chosen_restaurant != None) and (start_flag == False):
        coordinates = extract_lat_long(text)
        if coordinates == False:
            return "Please provide valid location"
        chosen_lati, chosen_long = coordinates
        return check_open_status(chosen_restaurant, chosen_lati, chosen_long)
    

    # coordinates = extract_lat_long(text)
    # if coordinates:
    #     global USER_LATI, USER_LONG
    #     USER_LATI, USER_LONG = coordinates
    #     return f'Your are here: {USER_LATI}/{USER_LONG}! I saved it.'

    # # if 'hello' in processed:
    # #     return 'Hey there!'
    
    # # if 'how are you' in processed:
    # #     return 'I am good!'
    
    # # if 'i love python' in processed:
    # #     return 'Me too!'
    
    # return 'I dont understand what you wrote...'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # Delete if you want the bot to respond in group without mentioning the bot
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        # Save this line tho if you did delete
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    # app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)