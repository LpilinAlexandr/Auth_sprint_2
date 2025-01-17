import random
import string
from typing import Optional

from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms import EmailField, StringField
from wtforms.validators import InputRequired

from authorization.password.main import encrypt_password
from db.initial import db
from db.models import User, Role, RoleRelation, SocialNetwork, SocialRelation
from permission.forms.create_role import RoleCreateForm

from utils.validators import RegistrationEmail, StringLength


class RegistrationForm(FlaskForm):
    """
    Форма регистрации по двум полям: email и password.
    """
    class Meta:
        csrf = False

    email = EmailField(
        'email',
        validators=[
            InputRequired('Please enter your email address.'),
            RegistrationEmail('Please enter valid email address.'),
        ]
    )
    password = StringField(
        'password',
        validators=[
            InputRequired('Please enter your password.'),
            StringLength(min=6, max=100, message='Password length must be at least 6 and no more than 100 characters.')
        ]
    )

    def create_new_user(self) -> Optional[User]:
        """ Создание пользователя с базовой ролью без отправки подтверждения на email"""
        if not self.validate():
            return

        new_user = User(
            email=self.data['email'],
            password=encrypt_password(password=self.data['password'])
        )
        db.session.add(new_user)

        default_role = Role.query.filter_by(name='SimpleUser').first()
        if not default_role:
            form = RoleCreateForm(MultiDict({
                'name': 'SimpleUser',
                'description': 'This is a role of custom User'
            }))
            default_role = form.create_new_role()
        db.session.commit()

        new_relatiol = RoleRelation(
            user_id=new_user.id,
            role_id=default_role.id
        )
        db.session.add(new_relatiol)
        db.session.commit()
        return new_user

    @staticmethod
    def generate_random_password(symbol_amount: int = 20):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(symbol_amount))

    def oauth_user_update(self, network_name: str, user: User, first_name: str, last_name: str):
        """
        Обновляет данные пользователя и привязывает к нему аккаунт социальной сети.
        :param network_name: название социальной сети
        :param user: пользователь
        :param first_name: имя
        :param last_name: фамилия
        """
        user.first_name = first_name
        user.last_name = last_name

        social_network = SocialNetwork.query.filter_by(name=network_name).first()
        new_social_relation = SocialRelation(
            social_id=str(social_network.id),
            user_id=str(user.id),
        )
        db.session.add(new_social_relation)
        db.session.commit()
