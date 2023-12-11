from aiosmtplib import SMTP
from email.message import EmailMessage
from config import settings

class EmailService:
    def __init__(self, smtp_server: str, username: str, password: str, port: int, from_email: str):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.port = port
        self.from_email = from_email

    async def send_email(self, to_email: str, subject: str, body: str):
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[to_email]
        )

        async with SMTP(hostname=self.smtp_server, port=self.port) as smtp:
            await smtp.login(self.username, self.password)
            await smtp.send_message(message)


def get_email_service():
    return EmailService(settings.MAIL_SERVER, settings.MAIL_USERNAME, settings.MAIL_PASSWORD,
                        settings.MAIL_PORT, settings.MAIL_FROM_EMAIL)
