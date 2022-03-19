from typing import Optional

from flask_wtf import FlaskForm
from wtforms import EmailField, StringField

from auth.authorization.forms.registration import RegistrationEmail, StringLength
from auth.authorization.password.main import encrypt_password, verify_password
from auth.db.initial import db
from auth.db.models import User


class ChangeUserDataForm(FlaskForm):
    """
    Форма регистрации по двум полям: email и password.
    """
    class Meta:
        csrf = False

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    email = EmailField(
        'email',
        validators=[
            RegistrationEmail('Please enter valid email address.'),
        ]
    )

    old_password = StringField(
        'password1',
        validators=[
            StringLength(min=6, max=100, message='Password length must be at least 6 and no more than 100 characters.')
        ]
    )

    new_password = StringField(
        'password2',
        validators=[
            StringLength(min=6, max=100, message='Password length must be at least 6 and no more than 100 characters.')
        ]
    )

    def validate(self, *args, **kwargs):
        old_password, new_password = self._fields['old_password'], self._fields['new_password']
        email = self._fields['email']

        if old_password.data is None and new_password.data is None:
            old_password.validators = new_password.validators = []

        if email.data is None:
            email.validators = []

        result = super().validate(*args, **kwargs)

        is_valid_password = verify_password(
            password=old_password.data,
            hashed_password=self.user.password,
        )
        if not is_valid_password:
            old_password.errors = ['Invalid old password']
            result = False

        return result

    def set_new_data(self, user: User) -> Optional[User]:

        if not self.validate():
            return

        if self.data.get('email'):
            # todo Здесь если будет подтверждение емеила нужно:
            #  сделать отправку письма и ставить ему "емеил не подтверждён"
            user.email = self.data.get('email')

        if self.data.get('new_password'):
            user.password = encrypt_password(self.data.get('new_password'))

        db.session.add(user)
        db.session.commit()
        return user
