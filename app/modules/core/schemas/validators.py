from pydantic_core import PydanticCustomError

from app.helpers.uploads import validate_file_size


def validate_photo(cls, v):
    if v and v.content_type not in ["image/jpeg", "image/png"]:
        raise PydanticCustomError(
            'invalid_photo_format',
            'Invalid photo format. Only JPEG or PNG images are allowed.',
        )
    return v

def validate_photo_size(cls, v):
    max_size = 1024 * 1024 * 20  # 20MB
    if v and not validate_file_size(v.file, max_size):
        raise PydanticCustomError(
            'photo_too_large',
            'Photo must be less than {max_size} bytes.',
        )
    return v

def check_passwords_match(cls, v, values, **kwargs):
    if 'password' in values.data and v != values.data['password']:
        raise PydanticCustomError(
            'password_mismatch',
            'Password and password_confirmation do not match.'
        )
    return v
