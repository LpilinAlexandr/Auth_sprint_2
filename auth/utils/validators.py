from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import Email, Length, ValidationError

from db.models import Role, User


class RegistrationEmail(Email):
    """Поле для емеила со встроенной валидацией на уникальность."""
    def __call__(self, form, field):
        super().__call__(form, field)

        exists_user = User.query.filter_by(email=field.data).count()
        if exists_user:
            raise ValidationError('User with this email address already exists')


class StringLength(Length):
    """Преобразует дату в строку перед валидацией."""
    def __call__(self, form, field):
        field.data = str(field.data)
        return super().__call__(form, field)


class RoleNameValidator:
    """Поле для уникаального имени роли."""

    def __init__(self, message):
        self.message = message

    def __call__(self, form, field):
        exists_name = Role.query.filter_by(name=field.data).count()
        if exists_name:
            raise ValidationError(self.message)


class RoleIdExistsValidator:
    """Валидатор существования роли по id."""

    def __init__(self, message):
        self.message = message

    def __call__(self, form, field):
        try:
            exists_role = Role.query.filter_by(id=field.data).count()
        except SQLAlchemyError:
            raise ValidationError(self.message)
        if not exists_role:
            raise ValidationError(self.message)


class UserIdExistsValidator:
    """Валидатор существования пользователя по id."""

    def __init__(self, message):
        self.message = message

    def __call__(self, form, field):
        try:
            exists_user = User.query.filter_by(id=field.data).count()
        except SQLAlchemyError:
            raise ValidationError(self.message)
        if not exists_user:
            raise ValidationError(self.message)

