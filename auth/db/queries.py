from auth.db.models import Role, RoleRelation, SocialRelation, SocialNetwork


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


def get_social_networks(user_id):
    """Возвращает все социальные сети пользователя."""
    relations = SocialRelation.query \
        .with_entities(SocialRelation.social_id) \
        .filter(SocialRelation.user_id == user_id)

    roles_query = SocialNetwork.query.filter(
        SocialNetwork.id.in_(relations)
    ).all()

    return roles_query
