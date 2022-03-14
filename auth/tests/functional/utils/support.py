import json
import os

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_redis_cache(data: str) -> dict:
    """Парсит сырые данные, получаемые из редиса."""
    result_list = json.loads(data)
    obj_str = result_list[0]
    return json.loads(obj_str)


def load_json_file(file_name):
    """Load json file by the filename"""
    file = os.path.join(BASE_DIR, 'testdata', file_name)

    with open(file, 'r') as f:
        json_file = json.load(f)
        return json_file


def parse_access_token(cookies):
    result = {}
    cookies = cookies.split(' ')

    for item in cookies:
        item = item.strip()
        if 'access_token_cookie' in item:
            result['access_token_cookie'] = item.replace('access_token_cookie=', '').replace(';', '')
    return result


def parse_refresh_token(cookies):
    result = {}
    cookies = cookies.split(' ')

    for item in cookies:
        item = item.strip()
        if 'refresh_token_cookie' in item:
            result['refresh_token_cookie'] = item.replace('refresh_token_cookie=', '').replace(';', '')
    return result

