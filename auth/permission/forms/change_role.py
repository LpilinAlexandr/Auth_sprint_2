from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import UUID

from db.initial import db
from db.models import Role
from utils.validators import RoleIdExistsValidator, RoleNameValidator


class RoleChangeForm(FlaskForm):
    """
    Форма создания роли
    """
    class Meta:
        csrf = False

    role_id = StringField(
        'role_id',
        validators=[
            UUID(), RoleIdExistsValidator('Role ID is required')
        ]
    )

    name = StringField(
        'name',
        validators=[
            RoleNameValidator('Please enter name'),
        ]
    )

    description = StringField()

    def validate(self, *args, **kwargs):
        result = super().validate(*args, **kwargs)

        name, description = self._fields['name'], self._fields['description']
        if not name.data and not description.data:
            name.errors = description.errors = ['Fill in at least one field']
            result = False

        return result

    def change_role(self) -> Optional[Role]:
        """Изменение роли на основе полученных данных."""
        if not self.validate():
            return

        changed_role = Role.query.filter_by(id=self.data['role_id']).first()

        if self.data.get('name'):
            changed_role.name = self.data['name']

        if self.data.get('description'):
            changed_role.description = self.data['description']

        db.session.commit()
        return changed_role
