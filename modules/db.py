import json
import os
import uuid

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
                'routes':{}
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
    

if __name__ == "__main__":
    botdatabase = BotDatabase('data.json')
    botdatabase.add_route('services','الخدمات المتوفرة')

