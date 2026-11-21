
import os
import json
import firebase_admin
from firebase_admin import credentials, messaging


def send_reminder():
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    device_token = os.environ.get("FCM_DEVICE_TOKEN")

    if not service_account_json or not device_token:
        raise ValueError("Firebase credentials or device token are missing.")

    service_account = json.loads(service_account_json)

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)

    message = messaging.Message(
        notification=messaging.Notification(
            title="Study Planner Reminder",
            body="It's time to check your study tasks. Keep learning!"
        ),
        token=device_token
    )

    response = messaging.send(message)
    print("Notification sent:", response)


if __name__ == "__main__":
    send_reminder()
