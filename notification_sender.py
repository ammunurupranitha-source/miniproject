
import os
import json
import firebase_admin
from firebase_admin import credentials, messaging


def initialize_firebase():
    """Initialize Firebase Admin only once."""

    if not firebase_admin._apps:
        try:
            service_account_json = os.environ.get(
                "FIREBASE_SERVICE_ACCOUNT"
            )

            if service_account_json:
                firebase_config = json.loads(service_account_json)
                cred = credentials.Certificate(firebase_config)

            elif os.path.exists("firebase-service-account.json"):
                cred = credentials.Certificate(
                    "firebase-service-account.json"
                )

            else:
                print("Firebase service account is missing.")
                return False

            firebase_admin.initialize_app(cred)

        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            return False

    return True


def load_device_token():
    """Read the saved Firebase device token."""

    token = os.environ.get("FCM_DEVICE_TOKEN")

    if token:
        return token.strip()

    try:
        with open("device_token.txt", "r", encoding="utf-8") as file:
            return file.read().strip()

    except FileNotFoundError:
        print("Firebase device token is missing.")
        return None


def send_notification(device_token, title, body):
    """Send a push notification to one registered device."""

    if not device_token:
        print("Device token is missing.")
        return False

    if not initialize_firebase():
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=device_token
        )

        response = messaging.send(message)
        print("Notification sent successfully:", response)
        return True

    except Exception as e:
        print(f"Notification sending failed: {e}")
        return False
