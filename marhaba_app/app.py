import inspect
import os

import requests
import wsgiadapter
from jinja2 import Environment, FileSystemLoader
from parse import parse
from webob import Request
from whitenoise import WhiteNoise

from marhaba_app.middleware import Middleware
from marhaba_app.response import Response


class MarhabaApp:

    def __init__(self, templates="templates", static_dir="static"):
        self.routes = dict()

        self.template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates))
        )

        self.default_exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir, prefix="/static")

        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith("/static"):
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()
        handler_data, kwargs = self.find_handler(request)

        if handler_data is not None:
            handler = handler_data["handler"]
            allowed_methods = handler_data["allowed_methods"]
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    return self.method_not_allowed_response(response)
            else:
                if request.method.lower() not in allowed_methods:
                    return self.method_not_allowed_response(response)
            try:
                handler(request, response, **kwargs)
            except Exception as e:
                if self.default_exception_handler is not None:
                    self.default_exception_handler(request, response)
                else:
                    raise e
        else:
            self.default_response(response)

        return response

    def find_handler(self, request):
        for path, handler_data in self.routes.items():
            parsed_result = parse(path, request.path)
            if parsed_result is not None:
                return handler_data, parsed_result.named
        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Page not found."

    def method_not_allowed_response(self, response):
        response.text = "Method Not Allowed."
        response.status_code = 405
        return response

    def add_route(self, path, handler, allowed_methods=None):
        assert path not in self.routes, "This url already exists."

        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "delete", "patch", "options", "head", "trace"]

        self.routes[path] = {"handler": handler, "allowed_methods": allowed_methods}

    def route(self, path, allowed_methods=None):
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def test_session(self):
        session = requests.Session()
        session.mount('http://testserver', wsgiadapter.WSGIAdapter(self))
        return session

    def template(self, template_path, context=None):
        if context is None:
            context = {}

        abs_template_path = self.template_env.get_template(template_path)
        rendered_template = abs_template_path.render(**context)
        return rendered_template

    def set_default_exception_handler(self, exception_handler):
        self.default_exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)
