

import re
import os
from pyrogram import Client, filters, enums, types,errors
from dotenv import load_dotenv
from modules.api import Api
from modules.db import BotDatabase,UsersDatabase,StatesDatabase
from modules.settings import Tools
import logging
import traceback

logging.basicConfig(filename="errors.log", level=logging.ERROR,
                    format="%(asctime)s:%(levelname)s:%(message)s")

load_dotenv()

SEC_API_KEY = os.environ.get('SEC_API_KEY')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
BOT_DB_PATH = os.getenv('BOT_DB_PATH')
USER_DB_PATH = os.getenv('USER_DB_PATH')
STATES_DB_PATH = os.getenv('STATES_DB_PATH')

api = Api(SEC_API_KEY)
bot_db = BotDatabase(BOT_DB_PATH)
user_db = UsersDatabase(USER_DB_PATH)
states_db = StatesDatabase(STATES_DB_PATH)

app = Client(BOT_NAME, api_id=API_ID,api_hash=API_HASH, bot_token=BOT_TOKEN)

tools = Tools(client=app,bot_database=bot_db,user_database=user_db)

#? state logic only here and not other files

@app.on_message(filters.private & filters.command(tools.commands)) 
async def on_command(client:Client,message:types.Message):
    await client.set_bot_commands(tools.get_commands(tools.commands_data))
    command = message.text[1:]
    params = tools.get_message_params(message)
    from_owner = tools.from_owner(message)
    text = 'None'
    markup = None
    bot_name = app.me.first_name
    first_name = params['first_name']
    url = tools.get_user_link(params['chat_id'],params['first_name'])

    if command == 'start':
        markup = tools.get_route_inline_markup('services',user=True)
        
    if command in tools.data['text']:
        text = tools.data['text'][command]
        
    if from_owner:
        #? command in tools.commands --> set text to on_command text
        if command in tools.commands and command in tools.language['on_command']:
            text = tools.language['on_command'][command]

        #? command in routes --> text to text of route 
        if command in tools.data['routes']:
            text = tools.data['routes'][command]['text']
            markup = tools.get_route_inline_markup(command)


        #? specific command functionality 
        if command == 'help':
            text = tools.language['on_command']['owner_help']
        elif command == 'text':
            markup = types.InlineKeyboardMarkup([])
            for item in tools.message_placeholder:
                button_text = tools.message_placeholder[item]
                callback = f'{item}::set_text'
                button = types.InlineKeyboardButton(button_text,callback)
                markup.inline_keyboard.append([button])
        elif command == 'points':
            available_users = tools.user_database.read_data()
            if available_users:
                markup = types.InlineKeyboardMarkup([])
                for user in available_users:
                    user_info = await client.get_users(user)
                    button_text = user_info.first_name
                    callback = f'{user_info.id}::points'
                    button = types.InlineKeyboardButton(button_text,callback)
                    markup.inline_keyboard.append([button])
        elif command == 'statistics':
            balance = api.balance()['balance']
            user_count = len(tools.user_database.read_data())
            must_sub =  '✅' if tools.data['sub'] else '❌'
        elif command == 'language':             
            start_text = tools.data['text']['start']
            done_text = tools.data['text']['done']
            sub_text = tools.data['text']['sub']
            help_text = tools.data['text']['help']
    
    else:
        user_db.add_user(params['chat_id'])

    #? fill in brackets with variables
    if re.search(r'{.*}', text):
        # Find all occurrences of {} in text
        matches = re.findall(r'{(.*?)}', text)
        #? Loop through matches and format text with corresponding variable
        for match in matches:
            variable_name = match.strip()
            if variable_name:
                if variable_name in locals():
                    variable_value = locals()[variable_name]
                    text = text.replace(f"{{{variable_name}}}", str(variable_value))
                else:
                    text = text.replace(f"{{{variable_name}}}", ' ')

    #? sending result to user
    return await client.send_message(chat_id=params['chat_id'],text=text,reply_markup=markup)

@app.on_callback_query()
async def answer_callback(client:Client,call:types.CallbackQuery):
    try:
        params = tools.get_message_params(call)
        from_owner = tools.from_owner(call)
        answers = {
            'not_allowed':'🚫',
            'query':'❔',
            'done':'✅',
            'faild':'❌❌❌'
        }
        if from_owner:
            if call.data == 'add_category':
                await client.delete_messages(params['chat_id'],params['message_id'])
                await client.send_message(params['chat_id'],tools.language['query']['route_text'])
                user_state = 'text::category'
                states_db.set_user_state(params['chat_id'],user_state)
                return await call.answer(answers['query'])
        else:
            await call.answer(answers['not_allowed'])
    except Exception:
        e = traceback.format_exc()
        logging.error(e)
        return  

@app.on_message(filters.private)
def reply(client:Client,message:types.Message):
    pass


app.run()