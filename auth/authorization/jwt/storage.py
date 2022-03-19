from flask_jwt_extended import decode_token

from auth.app_settings.settings import settings
from auth.db.no_sql import redis_client


def save_refresh(user, refresh_token):
    """
    Сохраняет refresh-токен и устройство.

    При логине пользователю на его устройство, в браузер, выдаётся refresh-token.
    Нам нужно сохранить токен, чтобы им могли воспользоваться только один раз.
    То есть если токен есть в базе, значит он валидный и им можно воспользоваться.
    Если его в базе нет, то и воспользоваться им нельзя.

    Также мы запоминаем устройство пользователя, которому выдали этот токен.
    Если нужно будет везде разлогинить, то мы просто удалим все refresh-токены устрйоств, которые запоминали.

    :param user:
    :param user_agent:
    :param refresh_token:
    :return:
    """

    token = decode_token(refresh_token)
    token_id = token['jti']
    user_agent = token['user_agent']
    value = 'stored'

    refresh_key = f'{settings.REFRESH_KEY}{token_id}'
    device_key = f'{settings.DEVICE_KEY}{user.id}'

    redis_client.setex(refresh_key, settings.REFRESH_TOKEN_EXP, value)
    redis_client.hset(device_key, user_agent, token_id)


def check_exists_refresh(refresh_token: dict):
    """Проверяет, хранится ли у нас этот refresh-токен."""
    token_id = refresh_token['jti']
    refresh_key = f'{settings.REFRESH_KEY}{token_id}'
    exists = redis_client.exists(refresh_key)

    return bool(exists)


def delete_token(user, refresh_token: dict):
    token_id = refresh_token['jti']
    user_agent = refresh_token['user_agent']

    refresh_key = f'{settings.REFRESH_KEY}{token_id}'
    device_key = f'{settings.DEVICE_KEY}{user.id}'

    redis_client.delete(refresh_key)
    redis_client.hdel(device_key, user_agent)


def delete_all_tokens(user):
    device_key = f'{settings.DEVICE_KEY}{user.id}'

    for device, refresh in redis_client.hgetall(device_key).items():
        token_id = refresh.decode('utf-8')
        refresh_key = f'{settings.REFRESH_KEY}{token_id}'
        redis_client.delete(refresh_key)

    redis_client.delete(device_key)
