import os
import json
# ? initialize data.json if not exists with plain data template
# ? data.json used to save text data and other exchangable data
#! data that increase infitly we use redis
# ? initialize .env file with input as api_id and bot_token


DATA_TEMPLATE = {
    'text': {
        'start': """•  أهلاً بك عزيزي
في بوت فيديو تهنئة 🎉.

- قم بإرسال أسمك باللغة العربية 🤍""",
        'select_design': 'اختر احد التصاميم الاتية :',
        'select_font':'اختر نوع الخط المناسب :',
        'sub': """⚠️  عذراً عزيزي 
⚙  يجب عليك الاشتراك في قناة البوت أولا
📮  اشترك ثم ارسل /start ⬇️

@{channel_username}""",
        'done': '| 🎉 |\n✅ مبروك بطاقتك جاهزة.',
        'error': ' ⚠️ عذرا, طول الاسم المرسل يتجاوز الحد المسموح, حاول مرة اخرى',
        'wait': 'جار معالجة طلبك, ارجو الانتظار قليلا',
        'follow':"""⚠️  عذراً عزيزي 
⚙  يجب عليك متابعة حسابي أولا
📮  تابع ثم ارسل /start ⬇️
        """,
        'follow_sure':"""⚠️  عذراً عزيزي 
⚙  لم يتم تسجيلك تأكد من متابعة الحساب أولا
📮  تابع ثم ارسل /start ⬇️
        """,
        
    },
    'designs_settings':{},
    'fonts_settings':{},
    'owner': {
        "id": 5444750825,
        "username": "",
        "first_name": "Ali",
        "last_name": ""
    },
    'refferal_button': {
        'start': None,
        'done': None,
    },
    'refferal_messages':{},
    'sub': None,
    'follow':None,
    'routes': {
        "designs_page": {
            "title": """
            <b>الصفحة الرئيسية للتعديل على التصاميم</b>

            - يمكنك التفاعل باستخدام الازرار
            """,

            "buttons": [
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
        },
        "edit_design_page": {

            "title": """
            <b>صفحة التعديل على التصميم ( {title} )</b>

            - يمكنك التفاعل باستخدام الازرار
            """,
            "buttons": [
                {
                    "id": "2",
                    "title": "~ تغيير العنوان ~",
                    "toggle": 'change_design_title',
                    'nav': None,

                },
                {
                    "id": "3",
                    "title": "~ تغيير الملف ~",
                    "toggle": 'change_design_file',
                    'nav': None,

                },
                {
                    "id": "12",
                    "title": "~ إعدادات تنسيق التصميم ~",
                    "toggle": 'designs_settings',
                    'nav': None,

                },
                {
                    "id": "4",
                    "title": "✗ حذف ✗",
                    "toggle": 'delete_design',
                    'nav': None,

                },
                {
                    "id": "5",
                    "title": "« الرجوع الى الصفحة الرئيسية",
                    "toggle": None,
                    'nav': "designs_page",

                },
            ]
        },
        "fonts_page": {
            "title": """
            <b>الصفحة الرئيسية للتعديل على الخطوط</b>

            - يمكنك التفاعل باستخدام الازرار
            """,

            "buttons": [
                {
                    'id': "6",
                    "title": "+ اضافة خط +",
                    "toggle": "add_new_font",
                    'nav': None,
                },
                {
                    'id': "7",
                    "title": "※ حذف جميع الخطوط ※",
                    "toggle": "delete_all_fonts",
                    'nav': None,
                },
            ]
        },
        "edit_font_page": {

            "title": """
            <b>صفحة التعديل على الخط ( {title} )</b>

            - يمكنك التفاعل باستخدام الازرار
            """,
            "buttons": [
                {
                    "id": "8",
                    "title": "~ تغيير العنوان ~",
                    "toggle": 'change_font_title',
                    'nav': None,

                },
                {
                    "id": "9",
                    "title": "~ تغيير الملف ~",
                    "toggle": 'change_font_file',
                    'nav': None,

                },
                {
                    "id": "13",
                    "title": "~ إعدادات تنسيق الخط ~",
                    "toggle": 'fonts_settings',
                    'nav': None,

                },
                {
                    "id": "10",
                    "title": "✗ حذف ✗",
                    "toggle": 'delete_font',
                    'nav': None,

                },
                {
                    "id": "11",
                    "title": "« الرجوع الى الصفحة الرئيسية",
                    "toggle": None,
                    'nav': "fonts_page",

                },
            ]
        }

    }


}


def initialize_project_folders(folders: dict) -> bool:
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


def load_data(data_file_path) -> dict:
    """
    load data.json if exists
    --
    """
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as f:
            data = json.load(f)
        f.close()
        return data
    else:
        with open(data_file_path, 'w') as f:
            json.dump(DATA_TEMPLATE, f, indent=2)
        f.close()
        return DATA_TEMPLATE


def save_data(data, data_file_path):
    """
    save data.json if exists
    --
    """
    if os.path.exists(data_file_path):
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        f.close()
        return True
    else:
        return False


# ? on import
initialize_project_folders(CONFIG_TEMPLATE['folders'])
