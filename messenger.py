import json
import requests
import yaml


#Get Webex API KEY from YAML File
try:
    with open("./config.yaml", 'r') as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Success: Loaded YAML config file")
except Exception:
    print("Yaml file incomplete or invalid format")
    raise
    


# Webex Teams messages API endpoint
base_url = 'https://api.ciscospark.com/v1/'

class Messenger():
    def __init__(self, base_url=base_url, api_key=config["api_key"]):
        self.base_url = base_url
        self.api_key = config["api_key"]
        self.headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        self.bot_id = requests.get(f'{self.base_url}/people/me', headers=self.headers).json().get('id')
        
    def get_message(self, message_id):
        """ Retrieve a specific message, specified by message_id """
        print(f'MESSAGE ID: {message_id}')
        received_message_url = f'{self.base_url}/messages/{message_id}'
        self.message_text = requests.get(received_message_url, headers=self.headers).json().get('text')


    def post_message(self, room_id, message):
        """ Post message to a Webex Teams space, specified by room_id """
        data = {
            "roomId": room_id,
            "text": message,
            }
        post_message_url = f'{self.base_url}/messages'
        post_message = requests.post(post_message_url,headers=self.headers,data=json.dumps(data))
        print(json.dumps(post_message.json(),indent=4))


