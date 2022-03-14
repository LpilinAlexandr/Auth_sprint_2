import os
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    api_url: str = Field('http://api:5050', env='API_URL')

    redis_host: str = Field('redis', env='REDIS_HOST')
    redis_port: str = Field(6379, env='REDIS_PORT')

    postgres_host: str = Field('localhost', env='POSTGRES_HOST')
    postgres_port: str = Field(5432, env='POSTGRES_PORT')
    postgres_db: str = Field('auth_database', env='POSTGRES_DB')
    postgres_user: str = Field('user', env='POSTGRES_USER')
    postgres_password: str = Field('password', env='POSTGRES_PASSWORD')

    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/auth_database')

    test_data_path: str = Field(end='TEST_DATA_PATH')







