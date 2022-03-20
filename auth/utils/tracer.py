from functools import wraps

from flask import current_app, request
import opentracing
from flask_opentracing import FlaskTracer
from jaeger_client import Config


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


def trace(operation_name: str):

    operation_name = operation_name or 'mega-trace'

    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            tracer: FlaskTracer = current_app.tracer
            request_id = request.headers.get('X-Request-Id')
            parent_span = tracer.get_span()
            parent_span.set_tag('http.request_id', request_id)

            with opentracing.tracer.start_span(operation_name, child_of=parent_span) as span:
                result = func(*args, **kwargs)
                return result

        return decorator
    return wrapper
