from db.models import Role, RoleRelation


def get_active_user_roles(user_id):
    """Возвращает активные роли пользователя."""
    active_roles_relation = RoleRelation.query \
        .with_entities(RoleRelation.role_id) \
        .filter(RoleRelation.user_id == user_id) \
        .filter(RoleRelation.finish_at == None)

    roles_query = Role.query.filter(
        Role.id.in_(active_roles_relation)
    ).all()

    return roles_query
