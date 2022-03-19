from datetime import datetime
from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import UUID

from auth.db.initial import db
from auth.db.models import Role, RoleRelation, User
from auth.permission.forms.delete_role import RoleIdExistsValidator
from auth.utils.validators import UserIdExistsValidator


class RoleSetForm(FlaskForm):
    """
    Форма создания роли
    """
    class Meta:
        csrf = False

    role_id = StringField(
        'role_id',
        validators=[
            UUID(), RoleIdExistsValidator('No role with this id')
        ]
    )

    user_id = StringField(
        'role_id',
        validators=[
            UUID(), UserIdExistsValidator('No User with this id')
        ]
    )

    def update_relation(self) -> Optional[Role]:
        """Устанавливает роль юзеру."""
        if not self.validate():
            return

        role = Role.query.filter_by(id=self.data['role_id']).first()
        user = User.query.filter_by(id=self.data['user_id']).first()

        new_relatio = RoleRelation(
            user_id=user.id,
            role_id=role.id
        )
        db.session.add(new_relatio)
        db.session.commit()
        return new_relatio


class RoleResetForm(RoleSetForm):

    def update_relation(self) -> Optional[Role]:
        """Устанавливает роль юзеру."""
        if not self.validate():
            return

        role = Role.query.filter_by(id=self.data['role_id']).first()
        user = User.query.filter_by(id=self.data['user_id']).first()

        new_relatio = RoleRelation.query.filter_by(
            user_id=user.id,
            role_id=role.id
        ).update({
            'finish_at': datetime.utcnow()
        })
        db.session.commit()
        return new_relatio
