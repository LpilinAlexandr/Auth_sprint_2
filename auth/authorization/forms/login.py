from typing import Optional

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from auth.authorization.password.main import verify_password
from auth.db.initial import db
from auth.db.models import LoginHistory, User
from auth.utils.client import get_ip


class LoginForm(FlaskForm):
    """
    Форма регистрации по двум полям: email и password.
    """
    class Meta:
        csrf = False

    email = StringField(
        'email',
        validators=[
            InputRequired('Email is required'),
        ]
    )
    password = StringField(
        'password',
        validators=[
            InputRequired('Password is required'),
        ]
    )

    def get_user(self) -> Optional[User]:
        if not self.validate():
            return

        email = self.data['email']
        user = User.query.filter_by(email=email, is_active=True).first()

        if not user:
            return None

        is_valid_password = verify_password(
            password=self.data['password'],
            hashed_password=user.password,
        )

        if is_valid_password:
            return user

    @staticmethod
    def save_login_info(user: User, request: request) -> LoginHistory:

        ip4 = get_ip(request)

        login_data = {
            'user_agent': request.user_agent.string,
            'platform': request.user_agent.platform,
            'browser': request.user_agent.browser,
            'ip4': ip4,
            'user_id': user.id,
        }

        login_snapshot = LoginHistory(**login_data)
        db.session.add(login_snapshot)
        db.session.commit()

        return login_snapshot
