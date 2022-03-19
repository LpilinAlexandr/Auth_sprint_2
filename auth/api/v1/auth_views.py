from functools import wraps

import requests
from flask import Blueprint, jsonify, request
from http import HTTPStatus

from flask_jwt_extended import get_jwt, jwt_required, unset_jwt_cookies
from werkzeug.datastructures import MultiDict

from auth.authorization.forms.login import LoginForm
from auth.authorization.forms.login_history import LoginHistoryForm
from auth.authorization.forms.registration import RegistrationForm
from auth.authorization.forms.user_data import ChangeUserDataForm
from auth.authorization.jwt.installers import get_user_from_jwt, set_jwt_couple
from auth.authorization.jwt.storage import (delete_all_tokens, delete_token, check_exists_refresh)

router = Blueprint('v1/auth', __name__, url_prefix='/api/v1/auth')


def allowed_refresh(func):
    """
    Декоратор, который проверяет: есть ли полученный JWT-токен в базе.

    Тем самым мы решаем 2 задачи:
    1) refresh-токен может использоваться только 1 раз
    2) Можно разлогинить все устройства пользователя, удалив его refresh-токен.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        jwt = get_jwt()
        token_is_stored = check_exists_refresh(jwt)
        if not token_is_stored:
            return jsonify({'error': 'Refresh token expired or not valid'}), HTTPStatus.UNAUTHORIZED

        result = func(*args, **kwargs)
        return result

    return wrapper


@router.route("/registration", methods=["POST"])
def registration():
    """Регистрация пользователя
    ---
    description:  (обмен логина и пароля на пару токенов - JWT-access токен и refresh токен)
    tags:
      - AUTH
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password1
            - password2
          properties:
            email:
              type: string
              example: hello@world.com
            password:
              type: string
              example: Qwerty123
    responses:
      200:
        description: test login description
        schema:
          type: object
          properties:
            msg:
              type: string
              example: success registration!
      400:
        description: Невалидные параметры
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Please enter valid email address."
          }
    """
    form = RegistrationForm()
    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    new_user = form.create_new_user()

    success_msg = f'Вы успешно зарегистрировались. ' \
                  f'На почту {new_user.email} отправлено письмо для подтверждения и активации аккаунта.'

    return jsonify({'msg': success_msg})


@router.route("/login", methods=["POST"])
def login():
    """Вход пользователя в аккаунт
    ---
    description:  (обмен логина и пароля на пару токенов - JWT-access токен и refresh токен)
    tags:
      - AUTH
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: admin
            password:
              type: string
              example: qwerty
    responses:
      200:
        description: test login description
        schema:
          type: object
          properties:
            msg:
              type: string
              example: login successful
      400:
        description: Невалидные параметры
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Incorrect login or password"
          }
    """

    form = LoginForm()
    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    user = form.get_user()
    if not user:
        fail_msg = f'Incorrect login or password'
        return jsonify({'error': fail_msg}), HTTPStatus.BAD_REQUEST

    login_snapshot = form.save_login_info(user, request)

    response = jsonify({"msg": "login successful"})
    set_jwt_couple(user, login_snapshot.user_agent, response)

    return response


@router.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
@allowed_refresh
def logout():
    """Выход пользователя из аккаунта
    ---
    description: Разлогинивает путём удаления refresh-токена из базы и из cookies
    tags:
      - AUTH
    parameters:
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            devices:
              type: string
              example: all
    responses:
      200:
        description: test login description
        schema:
          type: object
          properties:
            msg:
              type: string
              example: logout successful
      401:
        description: Юзер не авторизован
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Missing cookie refresh_token_cookie"
          }
    """
    jwt = get_jwt()
    user = get_user_from_jwt(jwt)

    devices_logout = request.json and request.json.get('all_devices', False) is True or False
    if devices_logout:
        delete_all_tokens(user)
    else:
        delete_token(user, jwt)

    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)

    return response


@router.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@allowed_refresh
def update_tokens():
    """обновление access-токена
        ---
    description: Возвращает новую пару access и refresh токенов.
    tags:
      - AUTH
    responses:
      200:
        description: test login description
        schema:
          type: object
          properties:
            msg:
              type: string
              example: update was successful
      400:
        description: Невалидные параметры
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Incorrect login or password"
          }
      401:
        description: Юзер не авторизован
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Missing cookie refresh_token_cookie"
          }
    """
    refresh_token = jwt = get_jwt()
    user = get_user_from_jwt(jwt)
    user_agent = refresh_token['user_agent']
    delete_token(user, refresh_token)

    response = jsonify({"msg": "update was successful"})
    set_jwt_couple(user, user_agent, response)
    return response


@router.route("/user-data", methods=["PATCH"])
@jwt_required()
def change_authentication():
    """изменение логина или пароля
    ---
    description: Ендпоинт позволяет изменить юзеру у себя пароль и логин, он же email.
    tags:
      - AUTH
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: hello@world.com
            old_password:
              type: string
              example: Qwerty123
            new_password:
              type: string
              example: Qwerty123
    responses:
      200:
        description: test login description
        schema:
          type: object
          properties:
            msg:
              type: string
              example: Data changed successfully!
      400:
        description: Невалидные параметры
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Please enter valid email address."
          }
      401:
        description: Юзер не авторизован
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "msg": "Missing cookie access_token_cookie"
          }
    """
    access_token = get_jwt()
    user = get_user_from_jwt(access_token)

    form = ChangeUserDataForm(user)
    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    form.set_new_data(user)

    return jsonify({'msg': 'Data changed successfully!'})


@router.route("/login-history", methods=["GET"])
@jwt_required()
def get_login_history():
    """получение пользователем своей истории входов в аккаунт
        ---
        description: Позволяет получить историю входов за период, либо за всё время.
        tags:
          - AUTH
        parameters:
          - name: date_from
            in: query
            schema:
              type: string
              properties:
                date_from:
                  type: string
                  example: 01-02-2022
          - name: date_to
            in: query
            schema:
              type: string
              properties:
                date_to:
                  type: string
                  example: 01-03-2022
          - name: page
            in: query
            schema:
              type: integegr
              properties:
                date_to:
                  type: integer
                  example: 1
          - name: per_page
            in: query
            schema:
              type: integer
              properties:
                date_to:
                  type: integer
                  example: 10
        responses:
          200:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "items": [
                {
                    "browser": "chrome",
                    "created_at": "Sat, 26 Feb 2022 11:11:04 GMT",
                    "ip4": "127.0.0.1",
                    "platform": "linux",
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
                },
              ],
                    "has_next": true,
                    "has_prev": false,
                    "page": 1,
                    "pages": 3,
                    "total": 100,
              }
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Please enter valid email address."
              }
          401:
            description: Юзер не авторизован
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Missing cookie access_token_cookie"
              }
        """
    access_token = get_jwt()
    user = get_user_from_jwt(access_token)
    form = LoginHistoryForm(MultiDict({
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', ''),
        'page': request.args.get('page', 1),
        'per_page': request.args.get('per_page', 25),
    }))

    login_history_list = form.get_login_history(user)
    response = jsonify(login_history_list)
    return response
