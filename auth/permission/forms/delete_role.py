from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import UUID

from db.initial import db
from db.models import Role
from utils.validators import RoleIdExistsValidator


class RoleDeleteForm(FlaskForm):
    """
    Форма удаления роли
    """
    class Meta:
        csrf = False

    role_id = StringField(
        'role_id',
        validators=[
            UUID(), RoleIdExistsValidator('No role with this id')
        ]
    )

    def delete_role(self) -> Optional[Role]:
        """Удаление роли на основе полученных данных."""
        if not self.validate():
            return

        deleted_role = Role.query.filter_by(id=self.data['role_id']).delete()
        db.session.commit()
        return deleted_role
