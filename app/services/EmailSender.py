import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, smtp_server: str, sender: str, password: str,
                 footer_template: str = None):
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(smtp_server, 465, context=context)
        self.server.login(sender, password)
        self.sender = sender
        self.footer_template = footer_template

    def send_emails(self, recipients: list, subject, body) -> (list, list):
        success = []
        fail = []
        for guest in recipients:
            assembled_body = self.generate_text(body, **guest.attribute_values)
            if self.footer_template:
                assembled_body += "\n---\n" + self.generate_text(self.footer_template, **guest.attribute_values)
            if self.send_email(guest.email, subject, assembled_body):
                success.append(guest.email)
            else:
                fail.append(guest.email)
        return success, fail

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg.attach(MIMEText(body, 'plain', _charset="UTF-8"))

            self.server.sendmail(self.sender, recipient, msg.as_string())
            return True
        except Exception as exception:
            print(exception)
            return False

    @staticmethod
    def generate_text(template: str, **kwargs):
        return template.format(**kwargs)
