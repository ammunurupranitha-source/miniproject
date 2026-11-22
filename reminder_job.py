
from notification_sender import send_notification, load_device_token


def main():
    print("Starting Study Planner Reminder Job...")

    device_token = load_device_token()

    if not device_token:
        print("ERROR: Firebase device token is missing.")
        return

    result = send_notification(
        device_token=device_token,
        title="📚 Study Planner Reminder",
        body="It's time to study! Open your Student Study Planner."
    )

    if result:
        print("Study reminder sent successfully!")
    else:
        print("Failed to send study reminder.")


if __name__ == "__main__":
    main()
