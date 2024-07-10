import imaplib
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import quopri
import email
import os
import email_constance


class Mail:

    def __init__(self, username, password):
        self.mail_username = username
        self.mail_pass = password

        imap_server = "imap.mail.ru"
        self.imap = imaplib.IMAP4_SSL(imap_server)
        self.imap.login(self.mail_username, self.mail_pass)
        self.imap.select("INBOX")

    def from_subj_decode(self, msg_from_subj):
        if not msg_from_subj:
            return None
        encoding = decode_header(msg_from_subj)[0][1]
        msg_from_subj = decode_header(msg_from_subj)[0][0]
        if isinstance(msg_from_subj, bytes):
            msg_from_subj = msg_from_subj.decode(encoding)
        if isinstance(msg_from_subj, str):
            pass
        msg_from_subj = str(msg_from_subj).strip("<>").replace("<", "")
        return msg_from_subj

    def get_letter_text_from_html(self, body):
        body = body.replace(
            "<div><div>", "<div>"
        ).replace("</div></div>", "</div>")
        try:
            soup = BeautifulSoup(body, "html.parser")
            paragraphs = soup.find_all("div")
            text = ""
            for paragraph in paragraphs:
                text += paragraph.text + "\n"
            return text.replace("\xa0", " ")
        except (Exception) as exp:
            print("function \"get_letter_text_from_html\" made error ", exp)
            return False

    def letter_type(self, part):
        if part["Content-Transfer-Encoding"] in (None, "7bit", "8bit", "binary"):
            return part.get_payload()
        elif part["Content-Transfer-Encoding"] == "base64":
            encoding = part.get_content_charset()
            return base64.b64decode(part.get_payload()).decode(encoding)
        elif part["Content-Transfer-Encoding"] == "quoted-printable":
            encoding = part.get_content_charset()
            return quopri.decodestring(part.get_payload()).decode(encoding)
        else:
            return part.get_payload()

    def clean_text(self, text):
        return text.replace("<", "").replace(">", "").replace("\xa0", " ").strip()

    def extract_text_from_part(self, part):
        extract_part = self.letter_type(part)
        if part.get_content_subtype() == "html":
            return self.get_letter_text_from_html(extract_part)
        return extract_part

    def get_letter_text(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == "text":
                    return self.clean_text(self.extract_text_from_part(part))
        else:
            if msg.get_content_maintype() == "text":
                return self.clean_text(self.extract_text_from_part(msg))
        return ""

    def get_letter_files(self, msg):
        mail = email.message_from_bytes(msg[0][1])

        if mail.is_multipart():
            if not os.path.exists("files"):
                os.mkdir("files")
            for part in mail.walk():
                content_type = part.get_content_type()
                filename = part.get_filename()

                if not filename:
                    continue
                filename = str(filename).split('?')[3].encode(
                    filename.split('?')[1]
                )
                filetype = content_type.split("/")[1]
                if filetype == email_constance.DOCX_FILETYPE:
                    filetype = "docx"
                new_file = os.path.join(
                    "files",
                    str(filename).split('\'')[1] + '.' + filetype
                )

                with open(new_file, 'wb') as new_file:
                    new_file.write(part.get_payload(decode=True))
                    new_file.close()

    def return_all_unread_messages(self, sender=None):
        """
        Returns unread messages
        :param sender: target email
        :return:
        """
        letters_massive = []

        res, unseen_msg = self.imap.uid("search", "UNSEEN", "ALL")
        unseen_msg = unseen_msg[0].decode(email_constance.ENCODING).split(" ")

        if not unseen_msg[0]:
            return letters_massive

        for letter in unseen_msg:
            res, msg = self.imap.uid("fetch", letter, "(RFC822)")
            if res != "OK":
                continue
            msg = email.message_from_bytes(msg[0][1])
            msg_from = self.from_subj_decode(msg["From"])
            msg_subj = self.from_subj_decode(msg["Subject"])
            msg_date = msg["Date"]

            if msg["Message-ID"]:
                msg_id = msg["Message-ID"].lstrip("<").rstrip(">")
            else:
                msg_id = msg["Received"]

            if msg["Return-path"]:
                msg_from = msg["Return-path"].lstrip("<").rstrip(">")
            if not msg_from:
                encoding = decode_header(msg["From"])[0][1]  # не проверено
                msg_from = (
                    decode_header(msg["From"])[1][0].decode(
                        encoding
                    ).replace("<", "").replace(">", "").replace(" ", "")
                )
            letter_text = self.get_letter_text(msg)
            if msg_from != sender and sender != None:
                continue

            letters_massive.append(
                {
                    "Subject": msg_subj,
                    "Text": letter_text,
                    "Sender": msg_from,
                    "Date": msg_date,
                    "Id": msg_id
                }
            )

        return letters_massive
