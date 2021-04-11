import boto3
from botocore.exceptions import ClientError


class EmailSender:
    def __init__(self, region: str, sender: str, html_template: str = None, footer_template: str = None):
        self.client = boto3.client('ses', region_name=region)
        self.sender = sender

        self.html_template = html_template
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

    def send_email(self, recipient: str, subject: str, body: str, html_body: str = None) -> bool:
        try:
            self.client.send_email(
                Destination={
                    'ToAddresses': [recipient],
                },
                Message={
                    'Body': {
                        # 'Html': {
                        #     'Charset': "UTF-8",
                        #     'Data': BODY_HTML,
                        # },
                        'Text': {
                            'Charset': "UTF-8",
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': "UTF-8",
                        'Data': subject,
                    },
                },
                Source=self.sender,
            )
        except ClientError as e:
            print(str(e))
            return False
        else:
            return True

    @staticmethod
    def generate_text(template: str, **kwargs):
        return template.format(**kwargs)
