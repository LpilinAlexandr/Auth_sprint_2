from typing import Any, Dict, List, Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import UUID

from db.queries import get_active_user_roles
from permission.forms.set_role import UserIdExistsValidator


class GetUserRolesForm(FlaskForm):
    """
    Форма создания роли
    """
    class Meta:
        csrf = False

    user_id = StringField(
        'user_id',
        validators=[
            UUID(), UserIdExistsValidator('No User with this id')
        ]
    )

    def get_user_roles(self) -> Optional[List[Dict[str, Any]]]:
        """Возвращает все активные роли юзера."""
        if not self.validate():
            return

        roles_query = get_active_user_roles(self.data['user_id'])

        return [{
            'id': role.id,
            'name': role.name,
            'description': role.description,
        } for role in roles_query]
