from typing import Optional

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from authorization.services import oauth


SERVICES = {
    'yandex': oauth.YandexOauth,
    'vk': oauth.VkOauth,
}


class OauthServiceValidator(InputRequired):
    """Валидирует наличие сервиса для взаимодействия через oauth."""

    def __call__(self, form, field):
        super().__call__(form, field)

        if field.data not in SERVICES:
            raise ValidationError('Service with this name not found')


class OauthServiceForm(FlaskForm):

    class Meta:
        csrf = False

    service = StringField(
        'service',
        validators=[
            OauthServiceValidator('Service is required'),
        ]
    )

    def get_service(self):
        if not self.validate():
            return

        service = SERVICES[self.data['service']]()

        return service


class OauthUrlForm(OauthServiceForm):

    def get_register_url(self) -> Optional[str]:
        service = self.get_service()
        return service.get_register_url()

    def get_login_url(self) -> Optional[str]:
        service = self.get_service()
        return service.get_login_url()
