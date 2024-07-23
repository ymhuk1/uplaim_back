import requests
from models import Push


async def send_notification(client, title, body):
        url = "https://exp.host/--/api/v2/push/send"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Host": "exp.host"
        }
        payload = {
            "to": client.push_token,
            "title": str(title),
            "body": str(body),
        }
        response = requests.post(url, json=payload, headers=headers)

        new_push = Push(to=client.push_token, title=title, body=body, data=response.json(), client=client)
        client.push.append(new_push)

