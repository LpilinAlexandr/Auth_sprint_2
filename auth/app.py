from authlib.integrations.flask_client import OAuth
from flasgger import Swagger
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


from auth.api.v1.auth_views import router as auth_router
from auth.api.v1.oauth_views import router as oauth_router
from auth.api.v1.roles_views import api
from auth.app_settings.settings import settings
from auth.db.initial import db, init_db

from jaeger_client import Config
from flask_opentracing import FlaskTracer


def main():
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(auth_router)
    app.register_blueprint(oauth_router)

    Swagger(app)
    JWTManager(app)
    api.init_app(app)
    init_db(app)
    app.app_context().push()

    migrate = Migrate()
    migrate.init_app(app, db)

    def _setup_jaeger():
        config = Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'local_agent': {
                    'reporting_host': "jaeger",
                    'reporting_port': 6831,
                },
            },
            service_name='auth',
            validate=True,
        )
        return config.initialize_tracer()

    tracer = FlaskTracer(_setup_jaeger, True, app=app)

    # @tracer.trace()
    # @app.before_request
    # def before_request():
    #     request_id = request.headers.get('X-Request-Id')
    #     if not request_id:
    #         raise RuntimeError('request id is requred')

    return app


if __name__ == '__main__':
    app = main()
    app.run()
