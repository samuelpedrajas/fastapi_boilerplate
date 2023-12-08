from aiosmtplib import SMTP, EmailMessage


class EmailService:
    def __init__(self, smtp_server: str, username: str, password: str, port: int = 587):
        self.smtp_server = smtp_server
        self.username = username
        self.password = password
        self.port = port

    async def send_email(self, to_email: str, subject: str, body: str):
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=self.username,
            to=[to_email]
        )

        async with SMTP(hostname=self.smtp_server, port=self.port) as smtp:
            await smtp.login(self.username, self.password)
            await smtp.send_message(message)

def get_email_service():
    return EmailService(smtp_server="your.smtp.server", username="username", password="password")
