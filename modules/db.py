import json
import os
import uuid
import logging


class JSONDB:
    def __init__(self,filepath:str) -> None:
        self.path = filepath
        self.initial_data = {}
        if not os.path.exists(filepath):
            self.write_data(self.initial_data)
        return

    def read_data(self):
        with open(self.path, 'r') as file:
            data = json.load(file)
            return data

    def write_data(self, data:dict):
        with open(self.path, 'w') as file:
            json.dump(data, file,indent=2)

#! JSON DB 
class UsersDatabase(JSONDB):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self.initial_user_data = {
                'points':0,  #? initial user points
                'orders':[]
            }
        return 
    
    def read_data(self):
        return super().read_data()
    
    def write_data(self, data: dict):
        return super().write_data(data)

    def add_user(self,chat_id:int or str) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id not in data:
            data[user_id] = self.initial_user_data
            self.write_data(data)
            return True
        return False
    
    def delete_user(self,chat_id:int or str) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            del data[user_id]
            self.write_data(data)
            return True
        return False
    
    def update_user_data(self,chat_id:int or str,key:str,value) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            user_data = data[user_id]
            user_data[key] = value
            self.write_data(data)
            return True
        return False
    
    def get_user_data(self,chat_id:int or str) :
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            user_data = data[user_id]
        else:
            self.add_user(user_id)
            user_data = self.initial_user_data
        return user_data





class BotDatabase(JSONDB):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self.initial_data = {
                'text': {
                    'start': "أهلا بك {url} في بوت {bot_name}",
                    'sub': """⚠️  عذراً عزيزي \n⚙  يجب عليك الاشتراك في قناة البوت أولا\n📮  اشترك ثم ارسل /start ⬇️\n\n@{channel_username}""",
                    'done': '| 🎉 |\n✅ تم استلام طلبك',
                    'error':'لا تتوفر خيارات حالياً, الرجاء إعادة المحاولة لاحقاً',
                    'help': ' عزيزي {url} يمكنك استخدام اﻷمر /start للتفاعل مع البوت',
                    },
                'owner': {
                    "id": 5444750825,
                    "username": "",
                    "first_name": "Ali",
                    "last_name": ""
                },
                'sub': None, #? username of a channel
                'routes':{
                    'services':{
                        'text':"""
                        <b>الصفحة الرئيسية للتعديل على الفئات</b>

                            - يمكنك التفاعل باستخدام الازرار
                        """,
                        'buttons':[
                            {
                                'id': "0",
                                "text": "+ اضافة فئة +",
                                "data": "add_category",
                            },
                            {
                                'id': "1",  
                                "text": "※ حذف الكل ※",
                                "data": "delete_all_services",
                            },
                        ]
                    },
                    'admins':{
                        'text':"""
                        <b>الصفحة الرئيسية للتعديل على الادمن</b>

                            - يمكنك التفاعل باستخدام الازرار
                        """,
                        'buttons':[
                            {
                                'id': "0",
                                "text": "+ اضافة ادمن +",
                                "data": "add_admin",
                            },
                            {
                                'id': "1",  
                                "text": "※ حذف الكل ※",
                                "data": "delete_all_admins",
                            },
                        ]
                    },
                    'points':{
                        'text':"""
                        <b>الصفحة الرئيسية للتعديل على النقاط</b>

                            - يمكنك التفاعل باستخدام الازرار
                        """,
                        'buttons':[
                            {
                                'id': "0",
                                "text": "+ اضافة نقاط للكل +",
                                "data": "add_all_points",
                            },
                            {
                                'id': "1",  
                                "text": "※ خصم نقاط الكل ※",
                                "data": "delete_all_points",
                            },
                        ]
                    },
                }
        }
        self.write_data(self.initial_data)
        return
    
    def read_data(self):
        return super().read_data()
    
    def write_data(self, data: dict):
        return super().write_data(data)
    

    def add_route(self,route_name:str,text:str,buttons:list = []) -> bool:
        data = self.read_data()
        if route_name in data['routes']:
            return False #! route already exists
        else:
            new_route = {
                'text' : text,
                'buttons' : buttons,
                
            }
            data['routes'][route_name] = new_route
            self.write_data(data)
            return True
        
    def delete_route(self,route_name:str) -> bool:
        data = self.read_data()
        if route_name in data['routes']:
            del data['routes'][route_name]
            self.write_data(data)
            return True
        return False
    
    def update_route_data(self,route_name:str,key:str,value) -> bool:
        data = self.read_data()
        if route_name in data['routes']:
            data['routes'][route_name][key] = value
            self.write_data(data)
            return True
        return False
    
    def get_route_data(self,route_name:str) :
        data = self.read_data()
        if route_name in data['routes']:
            route_data = data['routes'][route_name]
            return route_data
        return False

    def add_key(self,parent_key:str,key:str=None,value=None) -> bool:
        data = self.read_data()
        if key:
            if parent_key in data:
                data[parent_key][key] = value
                self.write_data(data)
                return True
            else:
                return False
        else:
            if parent_key in data:
                return False
            else:
                data[parent_key] = None
                self.write_data(data)
                return True
    
    def delete_key(self,parent_key:str,key:str = None) -> bool:
        data = self.read_data()
        if parent_key in data:
            if key:
                if key in data[parent_key]:
                    del data[parent_key][key]
                    self.write_data(data)
            else:
                del data[parent_key]
                self.write_data(data)
            return True
        return False


    def update_key_data(self,parent_key:str,value,key:str=None) -> bool:
        data = self.read_data()
        if parent_key in data:
            if key:
                if key in data[parent_key]:
                    data[parent_key][key] = value
                    self.write_data(data)
                    
            else:
                data[parent_key] = value
                self.write_data(data)
            return True
        return False



class StatesDatabase(JSONDB):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
    
    def read_data(self):
        return super().read_data()
    def write_data(self, data: dict):
        return super().write_data(data)
    
    def get_user_state(self,chat_id:int or str):
        data = self.read_data()
        user_id = str(chat_id)
        user_state = None
        if user_id in data:
            user_state = data[user_id]
        return user_state
    
    def set_user_state(self,chat_id:int or str,user_state:str):
        data = self.read_data()
        user_id = str(chat_id)
        data[user_id] = user_state
        self.write_data(data)
        return True

    
    def delete_user_state(self,chat_id:int or str):
        data = self.read_data()
        user_id = str(chat_id)
        if user_id in data:
            del data[user_id]
            self.write_data(data)
            return True
        return False
    
    
