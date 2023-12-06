import aiosmtplib
from app.dependencies.config import settings

async def send_email(to_address, subject, body, from_address=None):
    # sends an email to 'to_adress' usig the aiosmtplib library
    # 'subject' is the subject of the email
    # 'body' is the body of the email
    # 'from_address' is the email address of the sender
    aiosmtplib.send(
        message=aiosmtplib.Message(
            from_addr=from_address or settings.MAIL_DEFAULT_SENDER,
            to_addr=to_address,
            subject=subject,
            body=body
        ),
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        use_tls=settings.MAIL_USE_TLS
    )