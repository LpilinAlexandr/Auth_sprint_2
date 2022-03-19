from datetime import timedelta
from typing import List

from flask_wtf import FlaskForm
from werkzeug.exceptions import NotFound
from wtforms import DateField, IntegerField

from auth.db.models import LoginHistory, User


class LoginHistoryForm(FlaskForm):
    """
    Форма регистрации по двум полям: email и password.
    """
    class Meta:
        csrf = False

    date_from = DateField(format="%d-%m-%Y")
    date_to = DateField(format="%d-%m-%Y")
    page = IntegerField()
    per_page = IntegerField()

    def get_login_history(self, user: User) -> dict:
        date_from = self.data['date_from']
        date_to = self.data['date_to']
        query = LoginHistory.query.filter(LoginHistory.user_id == str(user.id))

        if date_from:
            query = query.filter(LoginHistory.created_at > date_from)

        if date_to:
            query = query.filter(LoginHistory.created_at < date_to + timedelta(days=1))

        try:
            query = query.paginate(page=self.data['page'], per_page=self.data['per_page'])
        except NotFound:
            query = query.paginate(page=1, per_page=self.data['per_page'])

        return {
            'items': [
                dict(
                    user_agent=model.user_agent,
                    platform=model.platform,
                    browser=model.browser,
                    created_at=model.created_at,
                    ip4=model.ip4,
                ) for model in query.items
            ],
            'has_next': query.has_next,
            'has_prev': query.has_prev,
            'page': query.page,
            'pages': query.pages,
            'total': query.total,
        }
