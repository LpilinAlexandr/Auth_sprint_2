from flask import jsonify, request
from werkzeug.datastructures import MultiDict
from flask_restful import Api, Resource
from http import HTTPStatus

from auth.authorization.jwt.extra import jwt_required_with_roles
from auth.db.models import Role
from auth.permission.forms.change_role import RoleChangeForm
from auth.permission.forms.create_role import RoleCreateForm
from auth.permission.forms.delete_role import RoleDeleteForm
from auth.permission.forms.get_roles import GetUserRolesForm
from auth.permission.forms.set_role import RoleResetForm, RoleSetForm

ADMIN = 'admin'
api = Api()


class RoleWithoutIdView(Resource):

    @jwt_required_with_roles(roles={ADMIN})
    def get(self):
        """Просмотр всех ролей
        ---
        description: Возвращает список всех существующих в базе ролей.
        tags:
          - ROLE
        responses:
          200:
            description: Успешный ответ
            schema:
              type: object
              properties:
              type: application/json
              example: [{
                "name": "admin",
                "description": "Something doing",
                "id": "af165836-de8a-40c5-b40f-73bc2c987ddf",
              },]
          401:
            description: Юзер не авторизован
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Missing cookie access_token_cookie"
              }
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """

        result = [{
            'name': role.name,
            'description': role.description,
            'id': str(role.id)
        } for role in Role.query.all()]

        return jsonify(result)

    @jwt_required_with_roles(roles={ADMIN})
    def post(self):
        """Создание роли
        ---
        description: Создание новой роли в базе.
        tags:
          - ROLE
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - name
                - description
              properties:
                name:
                  type: string
                  example: admin
                description:
                  type: string
                  example: Superuser who can create role
        responses:
          200:
            description: Успешный ответ
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role was created successfully!",
                "id": "af165836-de8a-40c5-b40f-73bc2c987ddf"
              }
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        form = RoleCreateForm()
        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        new_role = form.create_new_role()

        success_msg = 'Role was created successfully!'

        return jsonify({
            'msg': success_msg,
            'id': new_role.id
        })


class RoleWIthIdView(Resource):

    @jwt_required_with_roles(roles={ADMIN})
    def delete(self, role_id):
        """Удаление роли
        ---
        description: Удаление роли из базы
        tags:
          - ROLE
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
        responses:
          204:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role was created successfully!",
                "id": "af165836-de8a-40c5-b40f-73bc2c987ddf"
              }
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        form = RoleDeleteForm(MultiDict({
            'role_id': role_id,
        }))
        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        form.delete_role()

        return jsonify({
            'msg': 'deleted',
        }), HTTPStatus.NO_CONTENT

    @jwt_required_with_roles(roles={ADMIN})
    def patch(self, role_id):
        """Изменение роли
        ---
        description: Изменение роли
        tags:
          - ROLE
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: admin
                description:
                  type: string
                  example: Superuser who can create role
        responses:
          200:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "changed"
              }
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        form = RoleChangeForm(MultiDict({
            'role_id': role_id,
            'name': request.json.get('name', ''),
            'description': request.json.get('description', '')
        }))

        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        form.change_role()

        return jsonify({
            'msg': 'changed',
        })


class RoleUserView(Resource):

    @jwt_required_with_roles(roles={ADMIN})
    def put(self, user_id, role_id):
        """Установка юзеру роли
        ---
        description: Установка юзеру новой роли
        tags:
          - ROLE
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
          - name: user_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: {"msg": "success"}
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        data = MultiDict({
            'role_id': role_id,
            'user_id': user_id,
        })

        form = RoleSetForm(data)
        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        form.update_relation()

        return jsonify({
            'msg': 'success',
        })

    @jwt_required_with_roles(roles={ADMIN})
    def delete(self, user_id, role_id):
        """Удаление роли у юзера
        ---
        description: Роль удаляется у юзера
        tags:
          - ROLE
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
          - name: user_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: {"msg": "success"}
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        data = MultiDict({
            'role_id': role_id,
            'user_id': user_id,
        })

        form = RoleResetForm(data)
        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        form.update_relation()

        return jsonify({
            'msg': 'success',
        })


class RoleUserCheckView(Resource):

    @jwt_required_with_roles()
    def get(self, user_id):
        """Проверка наличя прав у пользователя
        ---
        description: Возвращает все текущие активные роли юзера
        tags:
          - ROLE
        parameters:
          - name: user_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: test login description
            schema:
              type: object
              properties:
              type: application/json
              example: [
                  {
                    "description": "Superuser who can create role",
                    "id": "67900d47-4dd0-4af8-a64d-56749c3818d7",
                    "name": "admin"
                  }
                ]
          400:
            description: Невалидные параметры
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "Role with this name already exists"
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
          403:
            description: Нет прав доступа
            schema:
              type: object
              properties:
              type: application/json
              example: {
                "msg": "No access rights"
              }
        """
        form = GetUserRolesForm(MultiDict({
            'user_id': user_id,
        }))
        if not form.validate():
            return jsonify({'error': form.errors}), HTTPStatus.BAD_REQUEST

        roles = form.get_user_roles()

        return jsonify(roles)


api.add_resource(RoleWithoutIdView, '/api/v1/roles')
api.add_resource(RoleWIthIdView, '/api/v1/roles/<role_id>')
api.add_resource(RoleUserView, '/api/v1/user/<user_id>/role/<role_id>')
api.add_resource(RoleUserCheckView, '/api/v1/user-roles/<user_id>')
