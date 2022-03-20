import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    DEBUG: bool = True
    SECRET_KEY: str = 'ascsa;kmckamcsa'

    JWT_SECRET_KEY: str = 'super-secret'
    JWT_TOKEN_LOCATION: list = ['cookies']
    JWT_COOKIE_SECURE: bool = False
    JWT_COOKIE_DOMAIN: str = os.getenv('SITE_DOMAINs', default='cinema.local')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Для разработки False, чтобы пользоваться свагером. Хотя можно и постманом
    JWT_COOKIE_CSRF_PROTECT = False

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))

    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/auth_database')

    REFRESH_KEY: str = 'refresh::'
    DEVICE_KEY: str = 'devices::user_id::'
    REFRESH_TOKEN_EXP: str = 60 * 60 * 24 * 15

    SITE_URL = 'http://auth.cinema.local'

    OAUTH_YANDEX_CLIENT_ID: str = os.getenv('OAUTH_YANDEX_CLIENT_ID')
    OAUTH_YANDEX_CLIENT_SECRET: str = os.getenv('OAUTH_YANDEX_CLIENT_SECRET')

    OAUTH_VK_CLIENT_ID: str = os.getenv('OAUTH_VK_CLIENT_ID')
    OAUTH_VK_CLIENT_SECRET: str = os.getenv('OAUTH_VK_CLIENT_SECRET')

    class Config:
        env_file = '.env'


settings = Settings()
