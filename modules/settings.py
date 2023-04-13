import json
import os
import uuid

class Settings:
    def __init__(self, filepath:str):
        self.path = filepath

        self.initial_data = {
                'text': {
                        'start': "أهلا بك {first_name} في بوت {bot_name}",
                        'sub': """⚠️  عذراً عزيزي \n⚙  يجب عليك الاشتراك في قناة البوت أولا\n📮  اشترك ثم ارسل /start ⬇️\n\n@{channel_username}""",
                        'done': '| 🎉 |\n✅ تم استلام طلبك',
                    },
                'owner': {
                    "id": 5444750825,
                    "username": "",
                    "first_name": "Ali",
                    "last_name": ""
                },
                'admins':[], #? user_ids of people in charge
                'sub': None, #? username of a channel
                'routes':{
                    'services':{
                        'text':"""
                        <b> الصفحة الرئيسية إختر أحد الأقسام </b>

                        - يمكنك التفاعل باستخدام الازرار
                        """,
                        'buttons'
                        'admin_buttons':[
                            {
                                'id': "0",
                                "title": "+ اضافة تصميم +",
                                "toggle": "add_new_design",
                                'nav': None,
                            },
                            {
                                'id': "1",
                                "title": "※ حذف جميع التصاميم ※",
                                "toggle": "delete_all_designs",
                                'nav': None,
                            },
                        ]
                    }
                }
        }

        if not os.path.exists(filepath):
            self.write_data(self.initial_data)
        return

    def read_data(self):
        with open(self.path, 'r') as file:
            data = json.load(file)
            return data

    def write_data(self, data:dict):
        with open(self.path, 'w') as file:
            json.dump(data, file)


    def get_random_string():
        return str(uuid.uuid4())[:8]

    def add_new_route(self,route_name:str,text:str,buttons:list = []):
        routes_data = self.read_data()['routes']
        if route_name in routes_data:
            return False #! route already exists
        else:
            new_route = {
                'text' : text,
                'buttons' : buttons,
                
            }