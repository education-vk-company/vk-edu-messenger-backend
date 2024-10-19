import threading
from centrifugo.utils import publish_data


def publish_message(message, members, event):
    data = {
        "event": event,
        "message": message,
    }

    def worker():
        for member in members:
            publish_data(data=data, channel=member.id)

    thread = threading.Thread(target=worker)
    thread.start()
