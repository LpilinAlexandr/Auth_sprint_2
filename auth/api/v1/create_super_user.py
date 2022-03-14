import click
from authorization.forms.registration import RegistrationForm
from db.models import User, Role, RoleRelation
from permission.forms.create_role import RoleCreateForm


@click.command()
@click.option('--admin_email', prompt='Type Admin email', help='This is Admin login.')
@click.option('--admin_password', prompt='Type Admin password', help='This is Admin password.')
@click.option('--confirm_admin_password', prompt='Confirm Admin password', help='Type Admin password one more time.')
def create_superuser(admin_email, admin_password, confirm_admin_password):
    """Создание роли Super User"""
    if '@' in admin_email and admin_password == confirm_admin_password:
        role = Role.query.filter_by(name='Admin').first()
        if not role:
            form = RoleCreateForm(name='Admin', description='Admin role')
            role = form.create_new_role()

        user = User.query.filter_by(email=admin_email).first()
        if not user:
            form = RegistrationForm(email=admin_email, password=admin_password)
            user = form.create_new_user()
            user_msg = f'Super user {admin_email} was created successfully!'

            relation = User.query.filter_by(user_id=user.id, role_id=role.id).first()
            if not relation:
                RoleRelation(user_id=user.id, role_id=role.id)
        else:
            user_msg = 'Sorry, this User is already exists!'

        return click.echo(user_msg)
    else:
        return click.echo('Try again. Passwords do not match!')


if __name__ == '__main__':
    create_superuser()
