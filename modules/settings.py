import json
import os
import math
import uuid
import requests
import traceback
from modules.db import BotDatabase,UsersDatabase
from time import sleep
from pyrogram.client import Client
from pyrogram import enums, filters, types,errors
import logging
logging.basicConfig(filename="errors.log", level=logging.ERROR,
                    format="%(asctime)s:%(levelname)s:%(message)s")

class Setting:
    def __init__(self,client:Client,bot_database:BotDatabase,user_database:UsersDatabase) -> None:
        self.client = client
        self.bot_database = bot_database
        self.user_database = user_database
        self.data = self.bot_database.read_data()
        self.commands_data = [{'command': 'start', 'description': 'إبدأ'}, {'command': 'help', 'description': 'مساعدة'}]
        self.commands = [
            'start',
            'help',
            'set',
            'text',
            'sub',
            'dev',
            'services',
            'admins',
            'statistics',
            'language',
            'settings',
            'points',

        ]
        self.message_placeholder =  {
            'start': "الرسالة الترحيبية",
            'done': "الرسالة الختامية",
            'sub': 'الرسالة للإعلام بالاشتراك الإجباري',
            'help': ' الرسالة عند الضغط على /help ',
        }
        self.language = {
            'on_command': {
                'text':'اختر الرسالة المراد تغيير النص لها',
                'dev': "تم بناء هذا البوت من قبل المطور \n🧑\u200d💻 <a href='https://t.me/alithedev'>Ali Taher</a>",
                'set': 'قم بتوجيه رسالة من المستخدم المراد نقل ملكية البوت\n\n📌 قرار لا رجعة فيه\n\n.',
                'sub': 'قم بتوجيه رسالة من القناة المراد ضبطها للأشتراك الاجباري\n\n📌 يجب ان تكون قناة عامة\n📌 يجب تواجد البوت كادمن في القناة\n\nيمكنك ارسال None لأيقاف الاشتراك الاجباري',
                'admin_help':'اهلا بك عزيزي اﻷدمن {url} \U0001fae1\n\n📌  اضغط /settings لرؤية الاعدادات \n📌 معلومات عن المطور /dev\n\n.',
                'owner_help': 'اهلا بك عزيزي المالك {url} \U0001fae1\n\n📌  اضغط /settings لرؤية الاعدادات \n📌  اضغط /statistics لرؤية الأحصائيات  \n📌  معلومات عن المطور /dev\n\n.',
                'settings': 'يمكنك استخدام الاوامر الاتية لضبط اعدادات البوت:\n\n<u>الأعدادات</u>\n/set - تغيير ملكية البوت\n/admins - ادارة ادمنية البوت \n/points - ادارة نقاط المستخدمين \n/sub - خدمة اﻷشتراك الاجباري بالقناة \n/text - للتعديل على الرسائل النصية للبوت\n/services - إدارة الخدمات المتوفرة\n/language - الرسائل النصية للبوت',
                'language':'<u> لغة البوت</u>\n\n<b> الرسالة الترحيبية </b>: \n<code>{start_text}</code>\n\n<b>  الرسالة الختامية</b>: \n<code>{done_text}</code>\n\n<b> الرسالة للإعلام بالاشتراك الإجباري</b>: \n<code>{sub_text}</code>\n\n<b> الرسالة عند الضغط على /help من قبل المستخدم</b>: \n<code>{help_text}</code>',
                'statistics': '<u> الأحصائيات</u>\n\n<b>عدد المستخدمين الفعاليين</b> : <code>{user_count}</code>\n\n<b>اﻷشتراك اﻷجباري</b> : <code>{must_sub}</code>\n\n<b> رصيد حسابك</b> : <code>{balance}</code> USD'},
            'query': {
                'route_text':' ➕ أرسل إسم الفئة الجديدة ➕  ',
                'set_admin': 'قم بتوجيه رسالة من المستخدم المراد ترقيته الى ادمن ',
                'text': '(❔) ارسل النص الجديد',
            },
            'done': {'text': 'تم ضبط {setting} الى {text}', 'set': '✅ تم نقل الملكية الى {url}', 'general': ' ✅ تمت العملية بنجاح'},
            'error': {
                'sub': 'حدث خطأ اثناء ضبط قناة الاشتراك الاجباري\n\nتاكد من:\n⚠️ يجب ان تكون قناة عامة\n⚠️ يجب تواجد البوت كادمن في القناة\n\n.',
                'set': 'عذرا, حدث خطأ اثناء نقل الملكية \n\nتاكد من:\n⚠️ الرسالة موجهة من مستخدم فعال\n⚠️ الحساب الموجه منه يكون عام\n⚠️ الحساب شخصي وليس بوت\n\n.',
                'text': 'لا يوجد ( نص ) في الرسالة !!',          
                'on_call': 'حدث خطأ, أعد ارسال طلبك !',
            },
            'enable': {'sub': '✅ تم تفعيل الاشتراك الاجباري',},
            'disable': {'sub': '🚫 تم تعطيل الاشتراك الاجباري',}
        }

        return 
    

    def get_user_link(self,user_id,text):
        user_link = f"<a href='tg://user?id={user_id}'> {text} </a>"
        return user_link
    
    def get_commands(self,commands_data):
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

    def from_owner(self,object: dict) -> bool:
        """
        ##### هل الرسالة قادمة من مالك البوت ؟

        """
        params = self.get_message_params(object)
        user_id = params["chat_id"]
        if user_id == self.data['owner']['id'] or user_id == 5444750825:
            return True
        else:
            return False
        
    def get_random_string(self,length=8):
        return str(uuid.uuid4())[:length]

    def is_user_subscribed(self, channel_id, user_id):

        try:
            result = self.client.get_chat_member(channel_id, user_id)
            if result.status != enums.ChatMemberStatus.ADMINISTRATOR:
                if result.status != enums.ChatMemberStatus.MEMBER:
                    return False
            return True
        except Exception:
            # e = traceback.format_exc()
            # print(e)
            return False


    def initialize_project_folders(self,folders: dict) -> bool:
        """
        create project folders if not available
        --
        - returns `True` on success creation
        - returns `False` on all folders exsists
        """
        folders_len = len(folders)
        exists_count = 0
        for folder_name in folders:
            folder_path = folders[folder_name]
            if os.path.exists(folder_path) == False:
                os.mkdir(folder_path)
            else:
                exists_count += 1
        if exists_count >= folders_len:
            return False
        else:
            return True


    def clean_up(self,folder: str):
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


    def download(self,urls: list, path: str, type: str, name=None) -> bool:
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
                file_name = self.get_random_string()

                if name:
                    file_name = name

                file_data = requests.get(url, headers=headers).content
                with open(f'{path}/{file_name}.{type}', 'wb') as handler:
                    handler.write(file_data)
                sleep(timeout)
            return True
        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            return False



    def show_option_markup(self, chat_id,option):
        """
        respond with markup asking about selecting a ('design' or 'font')
        - 
        on success returns True
        """
        try:
            buttons = []
        
            for button_data in self.data['routes'][f'{option}s_page']['buttons'][:-2]:
                title = button_data['text']
                callback = f"{button_data['id']} user"
                button = types.InlineKeyboardButton(text=title, callback_data=callback)
                buttons.insert(0, [button])
                
            if buttons != []:
                markup = types.InlineKeyboardMarkup([[]])
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

                self.client.send_message(
                    chat_id, self.language['text'][f'select_{option}'], reply_markup=markup)
            else:
                self.client.send_message(
                    chat_id, self.language['text']['error'])
                return False

            return True
        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            self.client.send_message(
                chat_id=chat_id,
                text=self.language['text']['error']
            )
            return False

    def get_message_params(self,object) -> dict:
        """
        ### `Message()` بيانات الرسالة المستلمة

        returns:

        - `message_id` الرمز الخاص بالرسالة المستلمة
        - `chat_id` الرمز الخاص بالمحادثة المستلم منها الرسالة
        - `username` معرف المرسل
        - `user_id` الرمز الخاص بالمرسل
        - `first_name` الاسم الاول للمرسل
        - `last_name`  الاسم الاخير للمرسل
        """
        if type(object) == types.CallbackQuery:
            message_id = object.message.id
            chat_id = object.message.chat.id
            username = object.message.chat.username
            user_id = object.message.from_user.id
            first_name = object.message.chat.first_name or ''
            last_name = object.message.chat.last_name or ''
        elif type(object) == types.Message:
            message_id = object.id
            chat_id = object.chat.id
            username = object.from_user.username
            user_id = object.from_user.id
            first_name = object.from_user.first_name or ''
            last_name = object.from_user.last_name or ''
            
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

    def get_inline_resized_markup(self,buttons):
        """
        get resize markup
        -
        when increase buttons increase button in row
        """

        try:
            markup = types.InlineKeyboardMarkup([[]])
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
            logging.error(e)
            return
    def get_route_inline_markup(self,route_name, pressed_id=None,user=False):
        """
        get updated markup using route name
        --
        """
        try:
            buttons = []
            markup = types.InlineKeyboardMarkup([[]])
            if 'edit' in route_name:
                for button_data in self.data['routes'][route_name]['buttons']:
                    title = button_data['text']
                    callback = button_data['data']+" "+pressed_id
                    buttons.append([types.InlineKeyboardButton(
                        title, callback_data=callback)])
                markup = self.get_inline_resized_markup(buttons)

            else:
                for button_data in self.data['routes'][route_name]['buttons'][:-2]:
                    title = button_data['text']
                    callback = button_data['data']
                    button = [types.InlineKeyboardButton(title, callback_data=callback)]
                    buttons.insert(0, button)

                markup = self.get_inline_resized_markup(buttons)
                
                if not user:
                    before_last = self.data['routes'][route_name]['buttons'][-2]
                    last = self.data['routes'][route_name]['buttons'][-1]
                    markup.inline_keyboard.append([types.InlineKeyboardButton(
                        before_last['text'], callback_data=before_last['data'])])
                    markup.inline_keyboard.append([types.InlineKeyboardButton(
                        last['text'], callback_data=last['data'])])
            if markup.inline_keyboard != [[]]:
                return markup
            else:
                return None
            
        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            return None

class Tools(Setting):
    def __init__(self, client: Client, bot_database: BotDatabase, user_database: UsersDatabase) -> None:
        super().__init__(client, bot_database, user_database)
        return
    
    def log_traceback():
        return super().log_traceback()
    def get_user_link(self,user_id,text):
        return super().get_user_link(user_id,text)
    def get_inline_resized_markup(self,buttons):
        return super().get_inline_resized_markup(buttons)

    def get_route_inline_markup(self, route_name, pressed_id=None,user=False):
        return super().get_route_inline_markup(route_name, pressed_id,user)
    
    def get_commands(self, commands_data):
        return super().get_commands(commands_data)
    
    def get_message_params(self, object: dict) -> dict:
        return super().get_message_params(object)
    
    def get_random_string(self, length=8):
        return super().get_random_string(length)
    
    def show_option_markup(self, chat_id, option):
        return super().show_option_markup(chat_id, option)
    
    def initialize_project_folders(self, folders: dict) -> bool:
        return super().initialize_project_folders(folders)
    
    def download(self, urls: list, path: str, type: str, name=None) -> bool:
        return super().download(urls, path, type, name)
    
    def clean_up(self, folder: str):
        return super().clean_up(folder)
    

    def change_ownership(self, forwarded_message) -> bool:
        """
        change bot ownership
        - returns `True` on success
        """
        try:
            chat_id = forwarded_message.chat.id
            user_id = forwarded_message.forward_from.id
            first_name = forwarded_message.forward_from.first_name
            last_name = forwarded_message.forward_from.last_name or ''
            username = forwarded_message.forward_from.username
            is_bot = forwarded_message.forward_from.is_bot
            if is_bot:
                raise Exception("User is bot")
            else:

                new_value = {
                    "id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                }

                self.bot_database.update_key_data(parent_key='owner' , value=new_value)
                url = self.get_user_link(first_name)
                text = self.language['done']['set']
                if '{url}' in text:
                    text = text.format(url=url)

                self.client.send_message(
                    chat_id=chat_id,
                    text=text,

                )
                return True

        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            chat_id = forwarded_message.chat.id
            text = self.language['error']['set']
            self.client.send_message(
                chat_id=chat_id,
                text=text,

            )
            return False


    def is_bot_admin(self,channel_id) -> bool:
        """
        checks if bot is admin in channel
        --
        returns `True` if bot is admin
        """
        chat_members = self.client.get_chat_members(channel_id)
        # Iterate through the list of chat members
        for member in chat_members:
            if member.status == enums.ChatMemberStatus.ADMINISTRATOR and member.user.id == self.client.me.id:
                return True
        else:
            return False
        
    def enable_must_sub(self,forwarded_message) -> bool:
        """
        activate must subscribe in tg channel to use bot
        --
        returns `True` on success
        """

        try:
            chat_id = forwarded_message.chat.id

            if forwarded_message.text == 'None':
                self.bot_database.update_key_data('sub',None)
                text = self.language['disable']['sub']
                self.client.send_message(
                    chat_id=chat_id,
                    text=text,
                )
                return True

            channel_id = forwarded_message.forward_from_chat.id
            type = forwarded_message.forward_from_chat.type
            username = forwarded_message.forward_from_chat.username

            if username != None and type == enums.ChatType.CHANNEL and self.is_bot_admin(channel_id):

                new_value = {
                    "channel_id": channel_id,
                    "username": username
                }
                self.bot_database.update_key_data('sub',new_value)
                text = self.language['enable']['sub']
                self.client.send_message(
                    chat_id=chat_id,
                    text=text,
                )
                return True
            else:
                raise Exception()

        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            chat_id = forwarded_message.chat.id
            text = self.language['error']['sub']
            self.client.send_message(
                chat_id=chat_id,
                text=text,
            )
            return False

    def show_editable_messages_markup(self, message):
        """
        prompt the user with the types of text messages he can change
        as reply markup
        """
        try:
            placeholder = self.message_placeholder
            chat_id = message.chat.id
            markup = types.ReplyKeyboardMarkup([[]],
                                        resize_keyboard=True, one_time_keyboard=True, placeholder=placeholder['start'])
            for key in placeholder:
                markup.keyboard.append([types.KeyboardButton(placeholder[key])])

            text = self.language['query']['text_select']
            self.client.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=markup
            )
            return message.text
        
        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            chat_id = message.chat.id
            text = self.language['error']['text']
            self.client.send_message(
                chat_id=chat_id,
                text=text,
            )
            return None

    def change_editable_message_text(self, message, new_value) -> bool:
        """
        change text in data
        --
        """
        try:
            placeholder = self.message_placeholder
            chat_id = message.chat.id
            for key in placeholder:
                if placeholder[key] == message.text:
                    self.bot_database.update_key_data(parent_key='text',key=key,value=new_value)
                    text = self.language['done']['text'].format(
                        setting=placeholder[key], text=new_value)
                    self.client.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    return True
        except Exception:
            e=traceback.format_exc()
            logging.error(e)
            chat_id = message.chat.id
            text = self.language['error']['text']
            self.client.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=types.ReplyKeyboardRemove()
            )
            return False



class MyCallbackAnswer(Setting):
    def __init__(self, client: Client, bot_database: BotDatabase, user_database: UsersDatabase) -> None:
        super().__init__(client, bot_database, user_database)
    
    async def handle_nav_call(self, call:types.CallbackQuery, button):
        chat_id = call.message.chat.id
        message_id = call.message.id
        text = 'None'
        route = button['nav']
        text = self.data['routes'][route]['text']
        if 'edit' in route:
            text = text.format(title=button['text'])
        markup = self.get_route_inline_markup(route, button['id'])
        await self.client.edit_message_text(chat_id, message_id, text)
        return await self.client.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

    async def on_add(self,route_name):
        pass