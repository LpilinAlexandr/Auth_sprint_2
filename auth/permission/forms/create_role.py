from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from auth.db.initial import db
from auth.db.models import Role
from auth.utils.validators import RoleNameValidator


class RoleCreateForm(FlaskForm):
    """
    Форма создания роли
    """
    class Meta:
        csrf = False

    name = StringField(
        'name',
        validators=[
            RoleNameValidator('Role with this name already exists'), InputRequired('Please enter name.')
        ]
    )
    description = StringField(
        'description',
        validators=[
            InputRequired('Please enter description.'),
        ]
    )

    def create_new_role(self) -> Optional[Role]:
        """Создание новой роли на основе полученных данных."""
        if not self.validate():
            return

        new_role = Role(
            name=self.data['name'],
            description=self.data['description']
        )
        db.session.add(new_role)
        db.session.commit()
        return new_role
