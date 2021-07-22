from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
import smtplib
from typing import List

from fastapi.datastructures import UploadFile

from cache import get_settings


class Mail(object):
    def __init__(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        files: List[UploadFile] = None
    ):
        self.user = sender
        self.recipients = recipients
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = subject
        self.msg['From'] = sender
        self.msg['To'] = ", ".join(recipients)
        self.msg['Date'] = formatdate(localtime=True)
        self.files = files

    async def send_email(self, password: str, plaintext=None, html=None):
        # Plaintext part
        if(plaintext is not None):
            plaintext = str(plaintext)
            textPart = MIMEText(plaintext, 'plain', "utf-8")
            self.msg.attach(textPart)

        # HTML part
        if(html is not None):
            htmlPart = MIMEText(html, 'html', "utf-8")
            self.msg.attach(htmlPart)

        # Attached Files
        if self.files is not None:
            for file in self.files or []:
                part = MIMEApplication(
                    file.file.read(),
                    Name=basename(file.filename)
                )
                part['Content-Disposition'] = f'attachment;\
                    filename="{file.filename}"'
                self.msg.attach(part)

        # Connect to the server
        if get_settings().PRODUCTION:
            s = smtplib.SMTP('localhost')
        else:
            s = smtplib.SMTP_SSL('mail.liviere.pl')
            s.login(self.user, password)

        s.sendmail(self.msg['From'], self.recipients, self.msg.as_string())
        s.quit()
