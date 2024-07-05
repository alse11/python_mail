import imaplib
import email
from email.header import decode_header
import functions
import os
import base64

mail_pass = ""
username = ""
imap_server = "imap.mail.ru"
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(username, mail_pass)

imap.select("INBOX")

ENCODING = "utf-8"


def main():
    res, unseen_msg = imap.uid("search", "UNSEEN", "ALL")
    unseen_msg = unseen_msg[0].decode(ENCODING).split(" ")

    if unseen_msg[0]:
       for letter in unseen_msg:
           res, msg = imap.uid("fetch", letter, "(RFC822)")
           #res, msg = imap.fetch(b'letter', "(RFC822)")
           if res == "OK":
               msg = email.message_from_bytes(msg[0][1])
               msg_from = functions.from_subj_decode(msg["From"])
               msg_subj = functions.from_subj_decode(msg["Subject"])
               if msg["Message-ID"]:
                   msg_id = msg["Message-ID"].lstrip("<").rstrip(">")
               else:
                   msg_id = msg["Received"]
               if msg["Return-path"]:
                   msg_email = msg["Return-path"].lstrip("<").rstrip(">")
               else:
                   msg_email = msg_from

               if not msg_email:
                   encoding = decode_header(msg["From"])[0][1]  # не проверено
                   msg_email = (
                       decode_header(msg["From"])[1][0]
                           .decode(encoding)
                           .replace("<", "")
                           .replace(">", "")
                           .replace(" ", "")
                   )
               letter_text = functions.get_letter_text(msg)
               print(letter_text)




if __name__ == "__main__":
    main()
