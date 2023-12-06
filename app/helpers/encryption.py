from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from os import urandom

class Encryption:
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.backend = default_backend()

    def encrypt(self, plaintext):
        salt = urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(self.key)
        iv = urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        return urlsafe_b64encode(salt + iv + encrypted).decode('utf-8')

    def decrypt(self, encrypted):
        encrypted = urlsafe_b64decode(encrypted)
        salt, iv, encrypted = encrypted[:16], encrypted[16:32], encrypted[32:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(self.key)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.decode('utf-8')
