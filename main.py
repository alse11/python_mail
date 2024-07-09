import imaplib
import email_functions
from os import getenv
from dotenv import load_dotenv
import email_functions
import email_class


def main():
    load_dotenv()
    mail_pass = getenv("MAILPASS")
    mail_username = getenv("MAILUSERNAME")

    mail_class = email_class.Mail(mail_username, mail_pass)

    msgs = mail_class.return_all_unread_messages()
    for msg in msgs:
        print(msg["Text"])


if __name__ == "__main__":
    main()
