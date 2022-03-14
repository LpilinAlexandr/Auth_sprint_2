from werkzeug.useragents import UserAgent


def string_as_user_agent(row_string: str):
    return UserAgent(row_string)


def user_agent_as_string(user_agent: UserAgent):
    return user_agent.string


def get_ip(request):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip4 = request.environ.get('REMOTE_ADDR', '')
    else:
        ip4 = request.environ.get('HTTP_X_FORWARDED_FOR', '')

    return ip4
