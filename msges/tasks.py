import threading
from centrifugo.utils import publish_data


def publish_message(message, members, event):
    data = {
        "event": event,
        "message": message,
    }

    def worker():
        publish_data(data=data, channels=[member.id for member in members])

    thread = threading.Thread(target=worker)
    thread.start()
