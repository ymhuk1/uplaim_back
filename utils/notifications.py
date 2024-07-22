from models import Notification
from utils.push_sender import send_notification


async def notify(client, type_notify, title, description=None, read=False, session=None):

    new_notify = Notification(client=client, type=type_notify, title=title, description=description, read=read)
    client.notify.append(new_notify)

    await send_notification(client, title, description, session=session)
