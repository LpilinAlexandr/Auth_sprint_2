import abc
from http import HTTPStatus
from typing import Optional

import requests

from auth.app_settings.settings import settings
from requests.models import PreparedRequest


class BaseOauthService(abc.ABC):

    client_id: str
    client_secret: str

    @property
    def site_url(self) -> str:
        raise NotImplementedError

    @property
    def redirect_uri(self) -> str:
        raise NotImplementedError

    @property
    def client_id(self) -> str:
        raise NotImplementedError

    @property
    def scope(self) -> str:
        raise NotImplementedError

    @property
    def response_type(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_register_url(self) -> str:
        ...

    @abc.abstractmethod
    def get_login_url(self) -> str:
        ...

    def __str__(self):
        req = PreparedRequest()
        req.prepare(method='get', url=self.site_url, params={
            'response_type': self.response_type,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
        })
        return req.url

    @abc.abstractmethod
    def get_register_data(self, code: str) -> dict:
        """
        Получает информацию о пользователе.

        Делает 2 запроса:
        1 запрос - это получение access_token'а
        2 запрос - получение данных пользователя.

        У каждого сервиса своё API и по этому данный метод в каждом сервисе будет разный.
        :param code: код авторизации
        """

    @abc.abstractmethod
    def get_login_data(self, code: str) -> dict:
        ...


class YandexOauth(BaseOauthService):

    name = 'yandex'
    client_id = settings.OAUTH_YANDEX_CLIENT_ID
    client_secret = settings.OAUTH_YANDEX_CLIENT_SECRET

    site_url = 'https://oauth.yandex.ru/authorize'
    redirect_uri = None
    scope = 'login:birthday login:email login:info login:avatar'
    response_type = 'code'

    def get_login_url(self):
        self.redirect_uri = settings.SITE_URL + '/api/v1/oauth/callback/login/yandex'
        return str(self)

    def get_register_url(self):
        self.redirect_uri = settings.SITE_URL + '/api/v1/oauth/callback/register/yandex'
        return str(self)

    def get_register_data(self, code: str) -> Optional[dict]:

        boundary = '--------------------------578033841511865424602007'

        # Получаем access_token
        response = requests.post(
            f'https://{self.client_id}:{self.client_secret}@oauth.yandex.ru/token',
            headers={
                'Content-type': f'application/x-www-form-urlencoded; boundary={boundary}'
            },
            data={
                'grant_type': 'authorization_code',
                'code': code,
            }
        )
        if response.status_code != HTTPStatus.OK:
            # todo логирование или какую-тто обработку добавить
            return

        data = response.json()
        access_token = data['access_token']

        # Получаем информацию о пользователе через API Яндекс ID
        response_info = requests.get(
            'https://login.yandex.ru/info',
            headers={
                'Authorization': f'OAuth {access_token}'
            },
            params={
                'format': 'json',
            }
        )

        if response_info.status_code == HTTPStatus.OK:
            user_info = response_info.json()
            return {
                'email': user_info['default_email'],
                'first_name': user_info['first_name'],
                'last_name': user_info['last_name'],
            }
        # todo логирование или какую-тто обработку добавить

    def get_login_data(self, code: str) -> dict:
        return self.get_register_data(code)


class VkOauth(BaseOauthService):

    name = 'vk'
    client_id = settings.OAUTH_VK_CLIENT_ID
    client_secret = settings.OAUTH_VK_CLIENT_SECRET
    site_url = 'https://oauth.vk.com/oauth/authorize'
    redirect_uri = None
    scope = 4194304
    response_type = 'code'
    API_VERSION = '5.131'

    def set_redirect_url(self, url_type: str):
        self.redirect_uri = settings.SITE_URL + f'/api/v1/oauth/callback/{url_type}/vk'

    def get_login_url(self):
        self.set_redirect_url('login')
        return str(self)

    def get_register_url(self):
        self.set_redirect_url('register')
        return str(self)

    def get_data(self, code: str):
        response = requests.get(
            'https://oauth.vk.com/access_token',
            params={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'code': code
            }
        )

        if response.status_code != HTTPStatus.OK:
            # todo логирование или какую-тто обработку добавить
            return

        data = response.json()
        email = data['email']
        response_info = requests.post(
            'https://api.vk.com/method/users.get',
            data={
                'user_ids': str(data['user_id']),
                'access_token': str(data['access_token']),
                'v': self.API_VERSION,
            }
        )

        if response_info.status_code == HTTPStatus.OK:
            user_info = response_info.json()
            user_info['email'] = email
            return {
                'email': email,
                'first_name': user_info['response'][0]['first_name'],
                'last_name': user_info['response'][0]['last_name'],
            }
        # todo логирование или какую-тто обработку добавить

    def get_register_data(self, code: str) -> Optional[dict]:
        self.set_redirect_url('register')
        return self.get_data(code)

    def get_login_data(self, code: str) -> Optional[dict]:
        self.set_redirect_url('login')
        return self.get_data(code)
