
import requests

class Api:
    """API client for Secsers.com"""

    def __init__(self, api_key):
        """Initializes the API client with the given API key"""
        self.api_url = 'https://secsers.com/api/v2'
        self.api_key = api_key

    def order(self, data):
        """Adds an order"""
        post = {'key': self.api_key, 'action': 'add'}
        post.update(data)
        return self._connect(post)

    def status(self, order_id):
        """Gets the status of an order"""
        post = {'key': self.api_key, 'action': 'status', 'order': order_id}
        return self._connect(post)

    def multi_status(self, order_ids):
        """Gets the status of multiple orders"""
        post = {'key': self.api_key, 'action': 'status', 'orders': ','.join(order_ids)}
        return self._connect(post)

    def services(self):
        """Gets available services"""
        post = {'key': self.api_key, 'action': 'services'}
        return self._connect(post)

    def balance(self):
        """Gets account balance"""
        post = {'key': self.api_key, 'action': 'balance'}
        return self._connect(post)

    def _connect(self, post):
        """Connects to the API and returns the response"""
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)'}
        response = requests.post(self.api_url, headers=headers, data=post, verify=False)
        return response.json()
    

if __name__ == '__main__':
    # print(Api('9684c97badcf32e9410dcb1c228eae89').balance())
    #     preffered_categories = [
    #     'Snapchat',
    #     'Spotify',
    #     'Tiktok',
    #     'Facebook',
    #     'Telegram',
    #     'Instagram',
    #     'Youtube',
    #     'Twitter',
    #     'Discord',
    #     'Website',
    # ]


    # api = Api(SEC_API_KEY)
    # services = api.services()

    # # categories = []
    # # for service in services:
    # #     if service['category'] not in categories:
    # #         categories.append(service['category'])


    # for category in preffered_categories:
    #     specific_services = []
    #     for service in services:
    #         if category in service['category'] :
    #             specific_services.append(service)

    #     with open(f'./services/{category}.json','w') as f:
    #         json.dump(specific_services,f,indent=2)

    pass