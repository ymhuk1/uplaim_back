from models import Notification


async def notify(client, type_notify, title, description=None, read=False):

    new_notify = Notification(client=client, type=type_notify, title=title, description=description, read=read)
    client.notify.append(new_notify)
