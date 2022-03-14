import json
import requests
from http import HTTPStatus
from ..utils.support import parse_access_token


REGISTRATION_URL = 'http://api:5050/api/v1/auth/registration'

TEST_EMAIL_1 = "s22s22s--world2.com"
TEST_PASSWORD_1 = "Qweasrty123"


def test_registration_wrong_email():
    '''Тест регистрации с некорректным email'''
    r = requests.post(
        REGISTRATION_URL,
        json={
            "email": TEST_EMAIL_1,
            "password": TEST_PASSWORD_1
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error']['email'][0] == "Please enter valid email address."


TEST_EMAIL_2 = "s22s22s@world2.com"
TEST_PASSWORD_2 = ""


def test_registration_wrong_password():
    '''Тест регистрации с пустым паролем'''
    r = requests.post(
        REGISTRATION_URL,
        json={
            "email": TEST_EMAIL_2,
            "password": TEST_PASSWORD_2
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error']['password'][0] == "Please enter your password."


TEST_EMAIL_3 = "s22s22s@world2.com"
TEST_PASSWORD_3 = "Qweasrty123"


def test_registration_success():
    '''Тест успешной регистрации'''
    r = requests.post(
        REGISTRATION_URL,
        json={
            "email": TEST_EMAIL_3,
            "password": TEST_PASSWORD_3
        }
    )
    assert r.status_code == HTTPStatus.OK
    assert json.loads(r.content.decode('utf-8')) == {'msg': f'Вы успешно зарегистрировались. На почту {TEST_EMAIL_3} отправлено письмо для подтверждения и активации аккаунта.'}


TEST_EMAIL_4 = "s22s22s@world2.com"
TEST_PASSWORD_4 = "Qweasrty123"


def test_registration_duplicate():
    '''Тест повторной регистрации существующего пользователя'''
    r = requests.post(
        REGISTRATION_URL,
        json={
            "email": TEST_EMAIL_4,
            "password": TEST_PASSWORD_4
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error']['email'][0] == "User with this email address already exists"


TEST_EMAIL_5 = "s22s22s@world2.com"
TEST_PASSWORD_5 = "12345"


def test_registration_short_password():
    '''Тест на короткий пароль при регистрации'''
    r = requests.post(
        REGISTRATION_URL,
        json={
            "email": TEST_EMAIL_5,
            "password": TEST_PASSWORD_5
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error']['password'][0] == "Password length must be at least 6 and no more than 100 characters."



LOGIN_URL = 'http://api:5050/api/v1/auth/login'

TEST_EMAIL_6 = "s22s22s@world2.com"
TEST_PASSWORD_6 = "Qweasrty123"


def test_login_success():
    '''Тест успешного входа'''
    r = requests.post(
        LOGIN_URL,
        json={
            "email": TEST_EMAIL_6,
            "password": TEST_PASSWORD_6
        }
    )
    assert r.status_code == HTTPStatus.OK
    assert json.loads(r.content.decode('utf-8')) == {'msg': 'login successful'}


TEST_EMAIL_7 = "s22s22s@world2_com"
TEST_PASSWORD_7 = "Qweasrty123"


def test_login_email_wrong():
    '''Тест входа с неверным логином'''
    r = requests.post(
        LOGIN_URL,
        json={
            "email": TEST_EMAIL_7,
            "password": TEST_PASSWORD_7
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error'] == "Incorrect login or password"



TEST_EMAIL_8 = "s22s22s@world2.com"
TEST_PASSWORD_8 = "Qweasrty12777"


def test_login_password_wrong():
    '''Тест входа с неверным паролем'''
    r = requests.post(
        LOGIN_URL,
        json={
            "email": TEST_EMAIL_8,
            "password": TEST_PASSWORD_8
        }
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert json.loads(r.content.decode('utf-8'))['error'] == "Incorrect login or password"


TEST_EMAIL_9 = "s22s22s@world2.com"
TEST_PASSWORD_9 = "Qweasrty123"
LOGIN_HISTORY_URL = 'http://api:5050/api/v1/auth/login-history'


def test_login_history_success():
    '''Тест просмотра истории входов пользователя'''
    r = requests.post(
        LOGIN_URL,
        json={
            "email": TEST_EMAIL_9,
            "password": TEST_PASSWORD_9
        }
    )

    assert r.status_code == HTTPStatus.OK
    assert json.loads(r.content.decode('utf-8')) == {'msg': 'login successful'}
    headers = r.headers['Set-Cookie']
    access_token = parse_access_token(headers)

    rh = requests.get(
        LOGIN_HISTORY_URL,
        json={
            "email": TEST_EMAIL_9,
            "password": TEST_PASSWORD_9,
            'date_from': '2022-01-01',
            'date_to': '2023-01-01'
        },
        headers={'access_token_cookie': access_token['access_token_cookie']}
    )

    assert rh.status_code == HTTPStatus.OK
    assert json.loads(r.content.decode('utf-8')) == {'msg': 'login successful'}
