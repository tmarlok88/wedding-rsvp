import boto3
from botocore.exceptions import ClientError


class EmailSender:
    def __init__(self, region: str, sender: str):
        self.client = boto3.client('ses', region_name=region)
        self.sender = sender

    def send_email(self, recipients: list, subject: str, body: str) -> bool:
        try:
            # Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': recipients,
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
            print(e.response['Error']['Message'])
            return False
        else:
            print(f"Email sent! Message ID: {response['MessageId']}")
            return True
