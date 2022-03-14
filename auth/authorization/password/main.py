from passlib.hash import ldap_pbkdf2_sha512


def encrypt_password(password: str):
    """
    Хеширует пароль.

    Выбрана ldap_pbkdf2_sha512 с функцией формирования ключа. Выглядит серьёзно. :)
    """
    return ldap_pbkdf2_sha512.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Определяет соответствие пароля."""
    return ldap_pbkdf2_sha512.verify(password, hashed_password)
