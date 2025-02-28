from include.tasks.email_track import get_service, fetch_email, parse_email
from include.tasks.post_event import process_event

# USER_EMAIL = 'indranil@softechnation.com'

def main():
    print("Hello from airflow!")

def _test():
    """ Shows basic usage of the Gmail API.
        Lists the user's mails.
    """
    service = get_service(file_path="/Data/Indranil/STN/tmp/test/240504085800.36324.mail")

    try:
        if service:
            fetch_email(service)
            id = parse_email()
            print(f"event id: {id}")
            process_event(id)

    except Exception as error:
        # TODO(developer) - Handle errors from gmail API.
        print("An error occurred")
        print(error)

if __name__ == "__main__":
    _test()
