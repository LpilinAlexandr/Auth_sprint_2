from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt


def jwt_required_with_roles(roles=None, optional=False, fresh=False, refresh=False, locations=None):
    """Декоратор, проверяющий наличие роли у пользователя у представления, гдя обязательно jwt"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(optional, fresh, refresh, locations)
            claims = get_jwt()

            if not roles or set(claims['roles']) & set(roles):
                return fn(*args, **kwargs)

            return {'msg': 'No access rights'}

        return decorator
    return wrapper
