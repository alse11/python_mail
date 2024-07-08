import imaplib
import functions
from os import getenv
from dotenv import load_dotenv


def main():
    load_dotenv()
    mail_pass = getenv("MAILPASS")
    mail_username = getenv("MAILUSERNAME")

    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(mail_username, mail_pass)
    imap.select("INBOX")

    msgs = functions.return_all_unread_messages(imap)
    for msg in msgs:
        print(msg[1])


if __name__ == "__main__":
    main()
