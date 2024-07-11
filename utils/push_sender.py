import requests


async def send_notification(to, title, body):
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
    }
    payload = {
        "to": to,
        "title": title,
        "body": body,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
