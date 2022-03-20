from flask_jwt_extended import (create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies)

from authorization.jwt.storage import save_refresh
from db.models import User
from db.queries import get_active_user_roles


def get_payload(user, user_agent):

    roles = [role.name for role in get_active_user_roles(user.id)]
    return {
        'name': user.get_name(),
        'roles': roles,
        'user_agent': user_agent
    }


def _set_access_token(user, payload, response):
    """Устанавливает новый JWT-access токен."""
    access_token = create_access_token(
        identity=user.id,
        additional_claims=payload,
        fresh=True,
    )
    set_access_cookies(response=response, encoded_access_token=access_token)


def _set_refresh_token(user, payload, response):
    """Устанавливает новый JWT-refresh токен."""
    refresh_token = create_refresh_token(
        identity=user.id,
        additional_claims=payload
    )
    save_refresh(user=user, refresh_token=refresh_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)


def set_jwt_couple(user, user_agent, response):
    """Устанавливает пару новых JWT токенов: access и refresh."""

    payload = get_payload(
        user, user_agent
    )

    _set_access_token(user, payload, response)
    _set_refresh_token(user, payload, response)

    return response


def get_user_from_jwt(token: dict):
    user_id = token['sub']
    user = User.query.filter_by(id=user_id).first()
    return user
