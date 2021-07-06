from flask import Flask, request, json
import requests
from messenger import Messenger
from dadjokes import Dad_Jokes

app = Flask(__name__)
port = 5000

msg = Messenger()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Receive a notification from Webex Teams and handle it"""
    if request.method == 'GET':
        return f'Request received on local port {port}, this actually works'
    elif request.method == 'POST':
        if 'application/json' in request.headers.get('Content-Type'):
            # Notification payload, received from Webex Teams webhook
            data = request.get_json()

            # Loop prevention, ignore messages which were posted by bot itself.
            # The bot_id attribute is collected from the Webex Teams API
            # at object instatiation.
            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'
            else:
                # Print the notification payload, received from the webhook
                print(json.dumps(data,indent=4))

                # Collect the roomId from the notification,
                # so you know where to post the response
                # Set the msg object attribute.
                msg.room_id = data.get('data').get('roomId')
                
                # Collect the message id from the notification, 
                # so you can fetch the message content
                message_id = data.get('data').get('id')

                # Get the contents of the received message. 
                msg.get_message(message_id)

                # If message starts with '/server', relay it to the web server.
                # If not, just post a confirmation that a message was received.
                if msg.message_text.startswith('/joke'):
	                # Default action is to list send the 'status' command. 
                    try:
                        number_jokes = int(msg.message_text.split()[1])
                        if number_jokes > 10:
                            number_jokes = 10
                            msg.reply = "Let's stick to 10 Jokes for now. I don't want to use up all my good ones!"
                            msg.post_message(msg.room_id, msg.reply)
                        while number_jokes > 0:
                            msg.reply = Dad_Jokes().get_joke() 
                            msg.post_message(msg.room_id, msg.reply)
                            number_jokes = number_jokes - 1
                    except:
                        msg.reply = "To recieve mulitple jokes use /joke #"
                        msg.post_message(msg.room_id, msg.reply)
                else: 
	                msg.reply = Dad_Jokes().get_joke() 
	                msg.post_message(msg.room_id, msg.reply)

                return data
        else: 
            return ('Wrong data format', 400)

if __name__ == '__main__':

    def get_ngrok_urls():
        urls = []
        ngrok_console = 'http://127.0.0.1:4040/api/tunnels'
        try:
            tunnels = requests.get(ngrok_console).json()['tunnels']
        except:
            print('NGROK NOT RUNNING')
            quit()
        
        for tunnel in tunnels:
            urls.append(tunnel['public_url'])
        return urls

    def get_webhook_urls():
        webhook_urls = []
        webhooks_api = f'{msg.base_url}/webhooks'
        webhooks = requests.get(webhooks_api, headers=msg.headers)
        if webhooks.status_code != 200:
            webhooks.raise_for_status()
        else:
            for webhook in webhooks.json()['items']:
                webhook_urls.append(webhook['targetUrl'])
        return webhook_urls

    def create_webhook(url):
        webhooks_api = f'{msg.base_url}/webhooks'
        data = { 
            "name": "Webhook to ChatBot",
            "resource": "all",
            "event": "all",
            "targetUrl": f"{url}"
        }
        webhook = requests.post(webhooks_api, headers=msg.headers, data=json.dumps(data))
        if webhook.status_code != 200:
            webhook.raise_for_status()
        else:
            print(f'Webhook to {url} created')

    def delete_webhooks():
        webhooks_api = f'{msg.base_url}/webhooks'
        webhooks = requests.get(webhooks_api,headers=msg.headers).json()
        for webhook in webhooks["items"]:
            print(f"Deleting {webhook.get('id')}")
            webhooks_api = f'{msg.base_url}/webhooks/{webhook.get("id")}'
            requests.delete(webhooks_api,headers=msg.headers)
    
    ngrok_urls = get_ngrok_urls()
    webhook_urls = get_webhook_urls()
    delete_webhooks()
    create_webhook(ngrok_urls[0])

    #intersect = list(set(ngrok_urls) & set(webhook_urls))
    #if intersect:
    #    print(f'Registered webhook: {intersect[0]}')
    #else: 
    #    create_webhook(ngrok_urls[0])
    

    app.run(host="0.0.0.0", port=port, debug=True)