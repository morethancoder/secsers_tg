import json
import os
import math
import uuid
import requests
import traceback
from db import BotDatabase,UsersDatabase
from time import sleep,time
from pyrogram.client import Client
from pyrogram import enums, filters, types,errors
import logging

logging.basicConfig(filename='errors.log', level=logging.WARNING, 
                    format='%(asctime)s %(levelname)s: %(message)s')




class Arms:
    def __init__(self,client:Client,bot_database:BotDatabase,user_database:UsersDatabase) -> None:
        self.client = client
        self.bot_database = bot_database
        self.user_database = user_database
        self.commands_data = [{'command': 'start', 'description': 'إبدأ'}, {'command': 'help', 'description': 'مساعدة'}]
        self.message_placeholder =  {
            'start': "الرسالة الترحيبية",
            'done': "الرسالة الختامية",
            'sub': 'الرسالة للإعلام بالاشتراك الإجباري',
        }
        self.language = {
            'on_command': {
                'dev': "تم بناء هذا البوت من قبل المطور \n🧑\u200d💻 <a href='https://t.me/alithedev'>Ali Taher</a>",
                'user_help': ' عزيزي {url} يمكنك استخدام اﻷمر /start للتفاعل مع البوت',
                'admin_help':'اهلا بك عزيزي اﻷدمن {url} \U0001fae1\n\n📌  اضغط /settings لرؤية الاعدادات \n📌 معلومات عن المطور /dev\n\n.',
                'owner_help': 'اهلا بك عزيزي المالك {url} \U0001fae1\n\n📌  اضغط /settings لرؤية الاعدادات \n📌  اضغط /statistics لرؤية الأحصائيات  \n📌  معلومات عن المطور /dev\n\n.',
                'settings': 'يمكنك استخدام الاوامر الاتية لضبط اعدادات البوت:\n\n<u>الأعدادات</u>\n/set - تغيير ملكية البوت\n/admin - ادارة ادمنية البوت \n/sub - خدمة اﻷشتراك الاجباري بالقناة \n/text - للتعديل على الرسائل النصية للبوت\n/services - إدارة الخدمات المتوفرة',
                'statistics': '<u> الأحصائيات</u>\n\n<b>عدد المستخدمين الفعاليين</b> : <code>{user_count}</code>\n\n<b>اﻷشتراك اﻷجباري</b> : <code>{must_sub}</code>\n\n<b> الرسالة الترحيبية </b>: \n<code>{start_text}</code>\n\n<b>  الرسالة الختامية</b>: \n<code>{done_text}</code>\n\n<b> الرسالة للإعلام بالاشتراك الإجباري</b>: \n<code>{sub_text}</code>',
            },
            'query': {
                'set': 'قم بتوجيه رسالة من المستخدم المراد نقل ملكية البوت\n\n📌 قرار لا رجعة فيه\n\n.',
                'set': 'قم بتوجيه رسالة من المستخدم المراد ترقيته الى ادمن ',
                'sub': 'قم بتوجيه رسالة من القناة المراد ضبطها للأشتراك الاجباري\n\n📌 يجب ان تكون قناة عامة\n📌 يجب تواجد البوت كادمن في القناة\n\nيمكنك ارسال None لأيقاف الاشتراك الاجباري',
                'text_select': 'اختر الرسالة المراد تغيير النص لها',
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
    
    def log_traceback():
        e=traceback.format_exc()
        logging.error(e)
    
    def create_user_link(user_id,text):
        user_link = f"<a href='tg://user?id={user_id}'> {text} </a>"
        return user_link
    
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
                url = self.create_user_link(first_name)
                text = self.language['done']['set']
                if '{url}' in text:
                    text = text.format(url=url)

                self.client.send_message(
                    chat_id=chat_id,
                    text=text,

                )
                return True

        except Exception:
            self.log_traceback()
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
            self.log_traceback()
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
            self.log_traceback()
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
            self.log_traceback()
            chat_id = message.chat.id
            text = self.language['error']['text']
            self.client.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=types.ReplyKeyboardRemove()
            )
            return False


