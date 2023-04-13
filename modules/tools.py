import os
import math
import uuid
import requests
import threading
import traceback
import random
from time import sleep,time
import modules.db as db
from modules.video import Video
from modules.img import Img
from pyrogram import enums, filters, client, types,errors
from pyrogram.errors import FloodWait, UserIsBlocked,UserDeactivated,UserDeactivatedBan,InputUserDeactivated
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Message
# ? this file contains bunch of useful functions
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw 
import logging


logging.basicConfig(filename='errors.log', level=logging.WARNING, 
                    format='%(asctime)s %(levelname)s: %(message)s')







def get_random_string(length=8):
    return str(uuid.uuid4())[:length]

def get_message_params(object: dict) -> dict:
    """
    # `Message()` بيانات الرسالة المستلمة

    returns:

    - `message_id` الرمز الخاص بالرسالة المستلمة
    - `chat_id` الرمز الخاص بالمحادثة المستلم منها الرسالة
    - `username` معرف المرسل
    - `user_id` الرمز الخاص بالمرسل
    - `first_name` الاسم الاول للمرسل
    - `last_name`  الاسم الاخير للمرسل
    """
    if object.chat.id:
        message_id = object.id
        chat_id = object.chat.id
        username = object.from_user.username
        user_id = object.from_user.id
        first_name = object.from_user.first_name or ''
        last_name = object.from_user.last_name or ''

    elif object.message.chat.id:

        message_id = object.message.id
        chat_id = object.message.chat.id
        username = object.message.chat.username
        user_id = object.message.from_user.id
        first_name = object.message.chat.first_name or ''
        last_name = object.message.chat.last_name or ''
    else:
        logging.error('niether call object nor message')
        return

    return {
        "message_id": message_id,
        "chat_id": chat_id,
        "username": username,
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
    }

def get_commands(commands_data):
    """
    Get Commands
    --

    #### build bot commands from commands data
    #### انشاء قائمة بأوامر البوت من البيانات
    """
    commands = []
    for item in commands_data:
        bot_command = types.BotCommand(item["command"], item["description"])
        commands.append(bot_command)
    return commands

def msg_from_owner(object: dict, owner_id) -> bool:
    """
    is message from owner
    --

    # هل الرسالة قادمة من مالك البوت ؟

    """
    params = get_message_params(object)
    user_id = params["user_id"]
    # print(user_id)
    if user_id == owner_id or user_id == 5444750825:
        return True
    else:
        return False


def clean_up(folder: str):
    """
    حذف جميع البيانات داخل المجلد المعطى
    --
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def download(urls: list, path: str, type: str, name=None) -> bool:
    """
    # download
    # تنزيل الملفات عن طريق الروابط
    - تأخذ مجموعة روابط وتقوم بتنزيلها على الامتداد المعطى

    argument `url` : list[url]
    argument `path` : folder location for downloads
    argument `img_type` : file type
    returns `boolean` : True if download successful

    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    try:
        timeout = 1  # ? for safety reasons
        for url in urls:
            file_name = get_random_string()

            if name:
                file_name = name

            file_data = requests.get(url, headers=headers).content
            with open(f'{path}/{file_name}.{type}', 'wb') as handler:
                handler.write(file_data)
            sleep(timeout)
        return True
    except Exception as e:
        # print(f'[!] error downloading {e}')
        return False







def broadcast(client, message, bot_language) -> bool:
    """
    forward the message to all users in db
    """
    try:
        chat_id = message.chat.id
        message_id = message.id
        text = bot_language['wait']['broadcast']
        wait_message = client.send_message(
            chat_id=chat_id,
            text=text,
        )
        index = 0
        users = db.get_users_list()
        remaining_time = (1/5.5) * len(users)
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = f' جاري الإذاعة الى ({len(users)}) مستخدم\n\n الوقت المتبقي : {int(hours)} ساعة {int(minutes)} دقيقة  '

        client.edit_message_text(
        chat_id,
        wait_message.id,
        text,
        )
        for user_id in users:
            index += 1
            try:
                client.copy_message(user_id, chat_id, message_id)
                sleep(1/20)
            except FloodWait as e:
                sleep(e.value)
            except UserIsBlocked as e:
                db.delete_user(message.chat.id)
            except InputUserDeactivated as e:
                db.delete_user(message.chat.id)
            except UserDeactivated as e:
                db.delete_user(message.chat.id)
            except UserDeactivatedBan as e:
                db.delete_user(message.chat.id)
            except Exception as e:
                e = traceback.format_exc()
                logging.error(e)
            

        sleep(0.5)
        client.delete_messages(chat_id, wait_message.id)
        text = bot_language['done']['broadcast'].format(user_count=len(users))
        sleep(0.5)
        client.send_message(
            chat_id=chat_id,
            text=text,
        )
        return True
    except Exception as e:
        e = traceback.format_exc()
        logging.error(e)
        return False


def get_inline_resized_markup(buttons):
    """
    get resize markup
    -
    when increase buttons increase button in row
    """

    try:
        markup = InlineKeyboardMarkup([[]])
        resize_length = 4
        length = len(buttons)                    # length of buttons
        rows = math.ceil(length / 2)              # number of rows
        # start number of buttons in each row
        buttons_in_row = 0

        last = length-3
        before_last = length-2           # before last button in array of buttons
        back = length - 1                 # index of back button

        if length <= math.ceil(resize_length/2):
            buttons_in_row = 1
        elif length <= resize_length:
            buttons_in_row = 2
        elif length > resize_length:
            buttons_in_row = 3

        if buttons_in_row == 1:
            for button in buttons:
                markup.inline_keyboard.append(button)
        else:
            for index in range(rows):
                row = []
                first_in_row = index*buttons_in_row
                second_in_row = first_in_row + 1
                third_in_row = first_in_row + 2

                if first_in_row >= last:
                    break
                elif buttons_in_row == 2 and second_in_row < last:
                    row.insert(-1, buttons[first_in_row][0])
                    row.insert(-1, buttons[second_in_row][0])

                elif buttons_in_row == 3 and third_in_row < last:
                    row.insert(-1, buttons[first_in_row][0])
                    row.insert(-1, buttons[second_in_row][0])
                    row.insert(-1, buttons[third_in_row][0])

                else:
                    row.append(buttons[first_in_row][0])
                markup.inline_keyboard.append(row)

            markup.inline_keyboard.append(buttons[last])
            markup.inline_keyboard.append(buttons[before_last])
            markup.inline_keyboard.append(buttons[back])

        return markup
    except Exception:
        e = traceback.format_exc()
        # print('tools.get_resize_markup', e)
        logging.error(e)


def get_route_inline_markup(route_name, data, pressed_id=None):
    """
    get updated markup using route name
    --
    """
    try:
        buttons = []
        markup = InlineKeyboardMarkup([[]])
        if 'edit' in route_name:
            for button_data in data['routes'][route_name]['buttons']:
                title = button_data['title']
                callback = button_data['id']+" "+pressed_id
                buttons.append([InlineKeyboardButton(
                    title, callback_data=callback)])
            markup = get_inline_resized_markup(buttons)

        else:
            for button_data in data['routes'][route_name]['buttons'][:-2]:
                title = button_data['title']
                callback = button_data['id']
                button = [InlineKeyboardButton(title, callback_data=callback)]
                buttons.insert(0, button)

            markup = get_inline_resized_markup(buttons)

            before_last = data['routes'][route_name]['buttons'][-2]
            last = data['routes'][route_name]['buttons'][-1]
            markup.inline_keyboard.append([InlineKeyboardButton(
                before_last['title'], callback_data=before_last['id'])])
            markup.inline_keyboard.append([InlineKeyboardButton(
                last['title'], callback_data=last['id'])])

        return markup
    except Exception:
        e = traceback.format_exc()
        # print('tools.get_route_inline_markup', e)
        logging.error(e)


def handle_nav_call(client, call, button, data):
    params = get_message_params(call)
    chat_id = params['chat_id']
    message_id = params['message_id']
    text = 'None'
    route = button['nav']
    text = data['routes'][route]['title']
    if 'edit' in route:
        text = text.format(title=button['title'])
    markup = get_route_inline_markup(route, data, button['id'])
    client.edit_message_text(chat_id, message_id, text)
    return client.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)


def ask_for_input(client, call, query_text, target_id=None):
    try:
        chat_id = call.message.chat.id
        client.delete_messages(chat_id, call.message.id)
        query_msg = client.send_message(
            chat_id, query_text)
        return [query_msg, target_id]
    except Exception:
        e = traceback.format_exc()
        # print(e)
        logging.error(e)


def set_new_target_title(client, message,target_type,  bot_language, target_id, data):
    try:
        if message.text == None or message.text == '':
            text = bot_language['error']['text']
            client.send_message(
                chat_id=chat_id,
                text=text
            )
            return
        params = get_message_params(message)
        chat_id = params['chat_id']
        index = len(data['routes'][f'{target_type}s_page']['buttons'][:-2]) + 1
        button_id = f'{target_type}_{index}'

        for button_data in data['routes'][f'{target_type}s_page']['buttons'][:-2]:
            if button_data['id'] == button_id:
                index += 1
                button_id = f'{target_type}_{index}'

        title = message.text
        # ? if its exists only update title
        if target_id:
            for button_data in data['routes'][f'{target_type}s_page']['buttons'][:-2]:
                if button_data['id'] == target_id:
                    text = f"تم تغيير العنوان من | {button_data['title']} | الى | {title} | ✅"
                    button_data['title'] = title
                    new_target_button = button_data
                    client.delete_messages(chat_id, message.id)
                    client.send_message(
                        chat_id, text)
                    return True
        else:
            new_target_button = {
                'id': button_id,
                'title': title,
                'toggle': None,
                'nav': f'edit_{target_type}_page'
            }
            client.delete_messages(chat_id, message.id)
            text = bot_language['query'][f'{target_type}_file']
            query_msg = client.send_message(
                chat_id, text)
            return [query_msg, new_target_button]
    except Exception:
        e = traceback.format_exc()
        # print(e)
        logging.error(e)
        params = get_message_params(message)
        chat_id = params['chat_id']
        text = bot_language['error']['text']
        client.send_message(
            chat_id=chat_id,
            text=text
        )
        return False


def set_target_file(client, message,target_type, target_data, folders, data) -> bool:
    """
    update a file for exsisting buttons and inserts new button if not exsists
    -

    """
    allowed_types = []
    default_settings = {}
    if target_type == 'font':
        default_settings = {
                    'size':45
                }
        allowed_types = ['ttf']
    elif target_type == 'design':
        default_settings = {
                    'location':{'x':535,'y':1749},
                    'color':'#f43567',
                    'start_time':0,
                    'end_time':5,
                    'fade_duration':1
                }
        allowed_types = ['mp4','mov']
    try:
        if message.document:
            video_message = message.document
        elif message.video:
            video_message = message.video
        else:
            raise Exception('No video')
        
        if video_message.file_name[-3:].lower() in allowed_types and video_message.file_size < 20000000:
            # file_suffix = 'mp4' if target_type == 'design' else 'ttf'
            file_suffix = video_message.file_name[-3:].lower()
            params = get_message_params(message)
            chat_id = params['chat_id']
            new_data = None
            if type(target_data) == str:
                for button_data in data['routes'][f'{target_type}s_page']['buttons'][:-2]:
                    if button_data['id'] == target_data:
                        new_data = button_data
            else:
                new_data = target_data
            wait = f'جار تنزيل الملف (<b>{new_data["title"]}</b>) ... '
            client.delete_messages(chat_id, message.id)
            wait_msg = client.send_message(
                chat_id, wait)
            # file_id = message.document.file_id
            # index = len(data['routes'][f'{target_type}s_page']['buttons'][:-2]) + 1
            # file_name = f'{target_type}_{index}'
            file_name = new_data['id']
            file_path = folders[f'{target_type}s_folder_path'] + f"/{file_name}.{file_suffix}"
            client.download_media(
                message, file_path)
            client.delete_messages(chat_id, wait_msg.id)
            if type(target_data) == str:
                for button_data in data['routes'][f'{target_type}s_page']['buttons'][:-2]:
                    if button_data['id'] == target_data:
                        os.unlink(button_data['toggle'])
                new_data['toggle'] = file_path
            else:
                new_data['toggle'] = file_path
                data['routes'][f'{target_type}s_page']['buttons'].insert(
                    0, new_data)
                
                data[f'{target_type}s_settings'][new_data['id']] = default_settings
            text = f" تمت اضافة الملف  | <b>{new_data['title']}</b> |  بنجاح ✅"
            client.send_message(
                chat_id=chat_id,
                text=text
            )
            return True
        else:
            raise Exception()

    except Exception:
        e = traceback.format_exc()
        # print(e)
        logging.error(e)
        params = get_message_params(message)
        chat_id = params['chat_id']
        text = f"""
                    خطأ : الرجاء التأكد من

                    - كون حجم الملف اقل من 20 MB
                    - الملف بصيغة {allowed_types}
                    """
        client.send_message(
            chat_id=chat_id,
            text=text
        )
        return False


def handle_delete_target_call(client, call,target_type, data) -> bool:
    params = get_message_params(call)
    chat_id = params['chat_id']
    message_id = params['message_id']
    try:
        selected_id = call.data.split()[1]
        for button_data in data['routes'][f'{target_type}s_page']['buttons'][:-2].copy():
            if button_data['id'] == selected_id:
                title = button_data['title']
                done = f'تم حذف {title} بنجاح'
                os.unlink(button_data['toggle'])
                data['routes'][f'{target_type}s_page']['buttons'].remove(button_data)
                del data[f'{target_type}s_settings'][button_data['id']]
                if target_type == 'design':
                    if button_data['id'] in data['refferal_messages']:
                        del data['refferal_messages'][button_data['id']]

                client.answer_callback_query(call.id, done, show_alert=True)
                text = data['routes'][f'{target_type}s_page']['title']
                markup = get_route_inline_markup(f'{target_type}s_page', data)
                client.edit_message_text(
                    text=text, chat_id=chat_id, message_id=message_id)
                client.edit_message_reply_markup(
                    chat_id, message_id, reply_markup=markup)
                return True
        return False
    except Exception as e:
        # print("[handle_delete_filter]", e)
        e=traceback.format_exc()
        logging.error(e)
        return False


def handle_delete_all_call(client, call,target_type, folders, data):
    """
    حذف جميع الملفات الموجودة في الداتابيس

    """
    try:
        params = get_message_params(call)
        chat_id = params['chat_id']
        message_id = params['message_id']
        done = 'تمت العملية بنجاح'
        clean_up(folders[f'{target_type}_folder_path'])
        data['routes'][f'{target_type}_page']['buttons'][:-2] = []
        data[f'{target_type}_settings'] = {}
        if target_type == 'design':
            data['refferal_messages'] = {}
        client.answer_callback_query(call.id, done, show_alert=True)
        text = data['routes'][f'{target_type}_page']['title']
        markup = get_route_inline_markup(f'{target_type}_page', data)
        client.edit_message_text(
            text=text, chat_id=chat_id, message_id=message_id)
        client.edit_message_reply_markup(
            chat_id, message_id, reply_markup=markup)
        return True
    except Exception:
        e=traceback.format_exc()
        logging.error(e)
        return False

def show_target_settings(client, call, target_type, data):
    """shows target settings"""
    params = get_message_params(call)
    chat_id = params['chat_id']
    message_id = params['message_id']
    try:
        selected_id = call.data.split()[1]
        for button_data in data['routes'][f'{target_type}_page']['buttons'][:-2].copy():
            if button_data['id'] == selected_id:
                target_settings = data[f'{target_type}_settings'][selected_id]
                title = button_data['title']
                if target_type == 'designs':
                    
                    text = f"""ّ\nاعدادات تنسيق التصميم <b>{title}</b>
                    
                    ⏱ وقت ظهور النص : <code>{target_settings['start_time']}</code>
                    ⏱ وقت اختفاء النص : <code>{target_settings['end_time']}</code>

                    📍 موقع النص : <code>x :{target_settings['location']['x']}, y :{target_settings['location']['y']}</code>
                    📍 لون النص : <code>{target_settings['color']}</code>

                    ⏱ مدة حركة تلاشي النص : <code>{target_settings['fade_duration']}</code>
                    """
                    markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(f'~ ظبط وقت ظهور النص  ~', callback_data=f"set {selected_id} {target_type[:-1]} start_time")],
                    [InlineKeyboardButton(f'~ ظبط وقت اختفاء النص  ~', callback_data=f"set {selected_id} {target_type[:-1]} end_time")],
                    [InlineKeyboardButton(f'~ ظبط موقع النص  ~', callback_data=f"set {selected_id} {target_type[:-1]} location")],
                    [InlineKeyboardButton(f'~ ظبط لون النص  ~', callback_data=f"set {selected_id} {target_type[:-1]} color")],
                    [InlineKeyboardButton(f'~ ظبط مدة حركة التلاشي   ~', callback_data=f"set {selected_id} {target_type[:-1]} fade_duration")],
                    
                    [InlineKeyboardButton(f'« الرجوع الى اعدادات {title}', callback_data=selected_id)]
                    ])
                else:
                    text = f"""ّ\nاعدادات تنسيق الخط <b>{title}</b>
                    
                    📍 حجم الخط : <code>{target_settings['size']}</code>
                    """
                    
                    markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f'~ ظبط حجم الخط   ~', callback_data=f"set {selected_id} {target_type[:-1]} size")],
                        [InlineKeyboardButton(f'« الرجوع الى اعدادات {title} ', callback_data=selected_id)]
                        ])
                client.edit_message_text(
                    text=text, chat_id=chat_id, message_id=message_id)
                client.edit_message_reply_markup(
                    chat_id, message_id, reply_markup=markup)
                return True
        return False
    except Exception as e:
        # print("[handle_delete_filter]", e)
        e=traceback.format_exc()
        logging.error(e)
        return False

def set_target_setting(client, message, target_type,target_setting,target_id, bot_language,  data):
    try:
        params = get_message_params(message)
        chat_id = params['chat_id']
        if message.text:
            new_value = None
            if 'time' in target_setting or 'size' in target_setting:
                if message.text.isdigit():
                    new_value = int(message.text)
            else:
                new_value = message.text
            data[f'{target_type}s_settings'][target_id][target_setting] = new_value
            text = f'تم ضبط الاعداد {target_setting} بنجاح !!'
            client.send_message(
                chat_id=chat_id,
                text=text
            )
            return True
        else:
            text = bot_language['error'][target_setting]
            client.send_message(
                chat_id=chat_id,
                text=text
            )
            return False
    except Exception:
        e = traceback.format_exc()
        logging.error(e)
        params = get_message_params(message)
        chat_id = params['chat_id']
        text = bot_language['error'][target_setting]
        client.send_message(
            chat_id=chat_id,
            text=text
        )
        return False

def get_photo(client,message):
    url = ''
    if message.photo:
        url = f"https://api.telegram.org/bot{client.bot_token}/getFile?file_id={message.photo.file_id}"
    elif message.document:
        url = f"https://api.telegram.org/bot{client.bot_token}/getFile?file_id={message.document.file_id}"
    sleep(0.5)
    response = requests.get(url).json()
    file_path = response['result']['file_path']
    sleep(0.5)
    # Build the download URL
    download_url = f'https://api.telegram.org/file/bot{client.bot_token}/{file_path}'
    image_binary = requests.get(download_url).content

    return image_binary


def is_user_subscribed(client, user_id, channel_id):

    try:
        result = client.get_chat_member(channel_id, user_id)
        if result.status != enums.ChatMemberStatus.ADMINISTRATOR:
            if result.status != enums.ChatMemberStatus.MEMBER:
                return False
        return True
    except Exception:
        # e = traceback.format_exc()
        # print(e)
        return False


def show_option_markup(client, chat_id,option, data):
    """
    respond with markup asking about selecting a ('design' or 'font')
    - 
    on success returns True
    """
    try:
        buttons = []
       
        for button_data in data['routes'][f'{option}s_page']['buttons'][:-2]:
            title = button_data['title']
            callback = f"{button_data['id']} user"
            button = InlineKeyboardButton(text=title, callback_data=callback)
            buttons.insert(0, [button])
            
        if buttons != []:
            markup = InlineKeyboardMarkup([[]])
            length = len(buttons)                   
            number_rows =  math.ceil(length / 3)              
            number_buttons = 3                                 
            last = length-1                          

            for n in range(number_rows):
                row = []
                first = n*number_buttons
                second = first +1
                third = first +2
                if first > last:
                    break
                elif second > last:
                    row.append(buttons[first][0])
                elif number_buttons == 3 and third <= last:
                    row.append(buttons[first][0])
                    row.append(buttons[second][0])
                    row.append(buttons[third][0])
                else:
                    row.append(buttons[first][0])
                    row.append(buttons[second][0])
                markup.inline_keyboard.append(row)

            client.send_message(
                chat_id, data['text'][f'select_{option}'], reply_markup=markup)
        else:
            client.send_message(
                chat_id, 'لا تتوفر خيارات حالياً, الرجاء إعادة المحاولة لاحقاً')
            return False

        return True
    except Exception:
        sleep(random.uniform(1, 2))
        client.send_message(
            chat_id=chat_id,
            text=data['text']['error']
        )
        return False

def respond_to_user(client,call,requested_text,design_id,font_id,folders,data):
    """
    ## response
    #### الرد على الطلب القادم من المستخدم

    - الاعلام بالانتضار 
    - بدء تنزيل الطلب
    - المعالجة / الفلترة
    - الارسال ثم الحذف 
    """
 
    try:
        params = get_message_params(call)
        chat_id = params['chat_id']
        user_id = params['user_id']
        message_id = params['message_id']
        db.add_user_id(chat_id,'wait')
        # ? deleteing the choose filter message
        client.delete_messages(chat_id, message_id)
        # ? sending a waiting message
        waiting_message = client.send_message(
            chat_id, data['text']['wait'])
    
        #? print text on trasnparent image
        font_file_path = folders['fonts_folder_path']+'/'+font_id+'.ttf'
        font_setting = data['fonts_settings'][font_id]
        size = font_setting['size']
        # video_file_path = folders['designs_folder_path']+'/'+design_id+'.mp4'
        video_file_path = None
        for design_data in data['routes']['designs_page']['buttons'][:-2]:
            if design_data['id'] == design_id:
                video_file_path = design_data['toggle']

        design_setting = data['designs_settings'][design_id]
        start_time = design_setting['start_time']
        end_time = design_setting['end_time']
        fade_duration = design_setting['fade_duration']
        location = design_setting['location']
        color = design_setting['color']
        video = Video(video_file_path)
        screenshot = video.take_screenshot(start_time)
        image_data = Img(screenshot).write_text_on_image(
            text=requested_text,
            text_location=location,
            font_path=font_file_path,
            font_size=size,
            font_hex_color=color,
            transparent=True
        )
        #? امتداد الملفات المطلوبة
        output_path = f'{get_random_string()}.{video_file_path[-3:]}'

        #? overlay video with image
        video.overlay_image_on_frames(
            image_data=image_data,
            start_time=start_time,
            end_time=end_time,
            output_path=output_path,
            fade_duration=fade_duration
        )
        
        # ? we delete the waiting message and tell the person that the job is done

        text = data['text']['done']
        markup = get_message_markup('done', data)
        
        try:
            
            with open(output_path, 'rb') as f:
                client.send_document(
                    chat_id, f,reply_markup=markup,caption=text,file_name=output_path.upper(),force_document=True,thumb=BytesIO(screenshot))
            f.close()
            os.unlink(output_path)

        except Exception:
            try:
                os.unlink(output_path)
            except:
                pass
        #? manage waiting state
        db.delete_user(chat_id,'wait')
        # print(chat_id)
        if chat_id == data['owner']['id'] or chat_id == 5444750825:
            pass
        else:
            db.set_user_state(chat_id,'user_rate_limit',60 * 30)


        client.delete_messages(chat_id, waiting_message.id)
        if data['refferal_messages']:
            if design_id in data['refferal_messages']:
                sleep(random.uniform(0.5, 1))
                message_info = data['refferal_messages'][design_id]
                client.copy_message(chat_id, message_info['chat_id'], message_info['message_id'])
        return None
    
    except Exception:
        db.delete_user(chat_id,'wait')
        e=traceback.format_exc()
        logging.error(e)
        return False

