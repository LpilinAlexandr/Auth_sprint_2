from flask import Blueprint, jsonify, request
from http import HTTPStatus

from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.datastructures import MultiDict

from auth.authorization.forms.login import LoginForm
from auth.authorization.forms.oauth import OauthUrlForm, OauthServiceForm
from auth.authorization.forms.registration import RegistrationForm
from auth.authorization.jwt.installers import set_jwt_couple

from auth.db.initial import db
from auth.db.models import User, SocialRelation, SocialNetwork
from db.queries import get_social_networks

router = Blueprint('v1/oauth', __name__, url_prefix='/api/v1/oauth')


@router.route('/register/<service>', methods=['GET'])
def get_oauth_register_url(service):
    """Получение url для регистрации через OAuth
    ---
    description: Нужно выбрать один из сервисов, через которых будет проходить регистрация. В ответ придёт url
    tags:
      - OAUTH
    parameters:
      - name: service
        in: path
        type: string
        enum: ['yandex', 'vk']
        required: true
    responses:
      200:
        description: урл для авторизации
        schema:
          type: object
          properties:
            url:
              type: string
              example: http://oauth.yandex.ru/authorize?...
    """
    form = OauthUrlForm(MultiDict({
        'service': service,
    }))
    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    url = form.get_register_url()

    return jsonify({
        'url': url
    })


@router.route('/login/<service>', methods=['GET'])
def get_oauth_login_url(service):
    """Получение url для авторизации через OAuth
    ---
    description: Нужно выбрать один из сервисов, через которых будет проходить регистрация. В ответ придёт url
    tags:
      - OAUTH
    parameters:
      - name: service
        in: path
        type: string
        enum: ['yandex', 'vk']
        required: true
    responses:
      200:
        description: урл для авторизации
        schema:
          type: object
          properties:
            url:
              type: string
              example: http://oauth.yandex.ru/authorize?...
    """
    form = OauthUrlForm(MultiDict({
        'service': service,
    }))
    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    url = form.get_login_url()

    return jsonify({
        'url': url
    })


@router.route('/callback/register/<service>', methods=['GET'])
def oauth_callback_register(service):
    """Коллбек-урл для регистрации через OAuth
    ---
    description: На этот урл приходит код авторизации OAuth.
        Регистрирует пользователя и возвращает в ответе email и password для входа
    tags:
      - OAUTH
    parameters:
      - name: service
        in: path
        type: string
        enum: ['yandex', 'vk']
        required: true
    responses:
      200:
        description: урл для авторизации
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "email": "some@amail.com", "password": "random-password"
          }
    """
    code = request.args.get('code')
    form = OauthServiceForm(MultiDict({
        'service': service,
    }))

    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    service = form.get_service()
    register_data = service.get_register_data(code)

    random_password = RegistrationForm.generate_random_password()

    register_form = RegistrationForm(MultiDict({
        'email': register_data['email'],
        'password': random_password
    }))

    if not register_form.validate():
        return jsonify({'error': register_form.errors}), HTTPStatus.BAD_REQUEST

    new_user = register_form.create_new_user()

    new_user.first_name = register_data['first_name']
    new_user.last_name = register_data['last_name']

    social_network = SocialNetwork.query.filter_by(name=service.name).first()
    new_social_relation = SocialRelation(
        social_id=str(social_network.id),
        user_id=str(new_user.id),
    )
    db.session.add(new_social_relation)
    db.session.commit()

    return jsonify({
        'email': register_data['email'],
        'password': random_password
    })


@router.route('/callback/login/<service>', methods=['GET'])
def oauth_callback_login(service):
    """Коллбек-урл для авторизации через OAuth
    ---
    description: На этот урл приходит код авторизации OAuth.
        Авторизует пользователя и возвращает успешный ответ с JWT-токенами
    tags:
      - OAUTH
    parameters:
      - name: service
        in: path
        type: string
        enum: ['yandex', 'vk']
        required: true
    responses:
      200:
        description: урл для авторизации
        schema:
          type: object
          properties:
            msg:
              type: string
              example: login successful
    """
    code = request.args.get('code')
    form = OauthServiceForm(MultiDict({
        'service': service,
    }))

    if not form.validate():
        return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

    service = form.get_service()
    register_data = service.get_login_data(code)

    login_form = LoginForm()
    user = User.query.filter_by(email=register_data['email'], is_active=True).first()
    if not user:
        return jsonify({'error': 'User does not exist'})

    login_snapshot = login_form.save_login_info(user, request)

    response = jsonify({"msg": "login successful"})
    set_jwt_couple(user, login_snapshot.user_agent, response)

    return response


@router.route('/social-networks', methods=['GET'])
@jwt_required()
def get_networks():
    """Получение всех привязанных соцсетей юзера
    ---
    tags:
      - OAUTH
    responses:
      200:
        description: урл для авторизации
        schema:
          type: object
          properties:
          type: application/json
          example: {
            "networks": [{"name": "yandex", "description": "example", "id": "some-uuid"},]
          }
    """
    jwt = get_jwt()
    user_id = jwt['sub']
    networks = get_social_networks(user_id)

    response_data = [
        {
            'name': network.name,
            'description': network.description,
            'id': str(network.id)
        } for network in networks
    ]

    return jsonify({
        'networks': response_data
    })


@router.route('social-networks/<network_id>', methods=['DELETE'])
@jwt_required()
def delete_network_relation(network_id):
    """Удаления привязанной соцсети пользователя
    ---
    tags:
      - OAUTH
    parameters:
      - name: network_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: успешный ответ
        schema:
          type: object
          properties:
            msg:
              type: string
              example: deleted successful
    """
    jwt = get_jwt()
    user_id = jwt['sub']
    SocialRelation.query.filter_by(user_id=user_id, social_id=network_id).delete()
    db.session.commit()

    return jsonify({"msg": "deleted successful"})
