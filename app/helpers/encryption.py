from itsdangerous import URLSafeTimedSerializer
from config import settings


serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def encrypt(plaintext):
    return serializer.dumps(plaintext)


def decrypt(encrypted):
    return serializer.loads(encrypted)
