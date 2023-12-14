from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from config import settings


serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encrypt(plaintext):
    return serializer.dumps(plaintext)


def decrypt(encrypted):
    return serializer.loads(encrypted)

def hash_password(password):
    return pwd_context.hash(password)
