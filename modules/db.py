import json
import os



#! JSON DB 
class JSONDB:
    def __init__(self, filepath:str):
        self.path = filepath
        self.initial_data = {}
        self.initial_user_data = {
                'points':0,  #? initial user points
                'orders':[]
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

    def add_user(self,chat_id:int | str) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id not in data:
            data[user_id] = self.initial_user_data
            self.write_data(data)
            return True
        return False
    
    def delete_user(self,chat_id:int | str) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            del data[user_id]
            self.write_data(data)
            return True
        return False
    
    def get_user_data(self,chat_id:int | str) -> int:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            user_data = data[user_id]
        else:
            self.add_user(user_id)
            user_data = self.initial_user_data
        return user_data

    def update_user_data(self,chat_id:int | str,key:str,value) -> bool:
        user_id = str(chat_id)
        data = self.read_data()
        if user_id in data:
            user_data = data[user_id]
            user_data[key] = value
            self.write_data(data)
            return True
        return False




if __name__ == "__main__":
    pass

