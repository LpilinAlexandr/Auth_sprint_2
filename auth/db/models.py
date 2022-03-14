import enum
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from db.initial import db


class SexType(enum.Enum):
    male = 'male'
    female = 'female'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    phone = db.Column(db.String(255), nullable=False, default='')
    birthday = db.Column(db.Date, nullable=True)
    sex = db.Column(db.Enum(SexType), nullable=True)
    first_name = db.Column(db.String(255), nullable=False, default='')
    last_name = db.Column(db.String(255), nullable=False, default='')

    # NOTE: Если надо будет почту подтверждать. То тут по дефолту можно ставить False
    is_active = db.Column(db.Boolean, default=True)

    roles = db.relationship('Role', secondary='roles_relations', backref=db.backref('users', lazy='dynamic'))
    logins = db.relationship('LoginHistory', lazy='dynamic', cascade='all, delete-orphan', backref=db.backref('user'))

    def __repr__(self):
        return f'<User {self.email}>'

    def get_name(self):
        last_name = f' {self.last_name}'
        first_name = f'{self.first_name or "User"}'

        return first_name + last_name


class LoginHistory(db.Model):
    __tablename__ = 'login_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_agent = db.Column(db.String(255), nullable=False, default='')
    platform = db.Column(db.String(255), nullable=False, default='')
    browser = db.Column(db.String(255), nullable=False, default='')
    ip4 = db.Column(db.String(255), nullable=False, default='')


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)


class RoleRelation(db.Model):
    __tablename__ = 'roles_relations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'))
    role_id = db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('roles.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # NOTE: Активной считается роль, у которой finish_at = NULL
    finish_at = db.Column(db.DateTime, nullable=True)
