import pytest

from marhaba_app.middleware import Middleware


def test_add_route(app):
    @app.route("/home")
    def home(req, res):
        res.text = "Hello from home"


def test_duplicate_route_throws_exc(app):
    @app.route("/home")
    def home(req, res):
        res.text = "Hello from home"

    with pytest.raises(AssertionError):
        @app.route("/home")
        def home2(req, res):
            res.text = "Hello from home2"


def test_routing_accepts_request(app, test_client):
    @app.route("/home")
    def home(req, res):
        res.text = "Hello from home"

    response = test_client.get("http://testserver/home")
    assert response.status_code == 200
    assert response.text == "Hello from home"


def test_parametrized_routing(app, test_client):
    @app.route("/hello/{name}")
    def hello(req, res, name):
        res.text = f"Hello {name}"

    assert test_client.get("http://testserver/hello/John").text == "Hello John"
    assert test_client.get("http://testserver/hello/Brake").text == "Hello Brake"


def test_default_response(test_client):
    response = test_client.get("http://testserver/not-found")

    assert response.status_code == 404
    assert response.text == "Page not found."


def test_class_based_get(app, test_client):
    @app.route("/books")
    class Book:
        def get(self, req, res):
            res.text = "Books page."

    assert test_client.get("http://testserver/books").text == "Books page."


def test_class_based_post(app, test_client):
    @app.route("/books")
    class Book:
        def post(self, req, res):
            res.text = "Page to create books."

    assert test_client.post("http://testserver/books").text == "Page to create books."


def test_class_based_not_allowed(app, test_client):
    @app.route("/books")
    class Book:
        def get(self, req, res):
            res.text = "Books page."

        def post(self, req, res):
            res.text = "Page to create books."

    response = test_client.put("http://testserver/books")
    assert response.status_code == 405
    assert response.text == "Method Not Allowed."


def test_new_handler(app, test_client):
    def new_handler(request, response):
        response.text = "Hello from new handler."
    app.add_route("/new-handler", new_handler)

    assert test_client.get("http://testserver/new-handler").text == "Hello from new handler."


def test_template_handler(app, test_client):
    @app.route("/template")
    def template(req, res):
        res.html = app.template(
            "tests/test_home_page.html",
            context={"title": "My custom html title", "body": "My custom html body"},
        )

    response = test_client.get("http://testserver/template")

    assert "My custom html title" in response.text
    assert "My custom html body" in response.text
    assert "text/html" in response.headers["Content-Type"]


def test_custom_exception_handler(app, test_client):
    def custom_exception_handler(request, response):
        response.text = "Something went wrong."
        response.status_code = 500

    app.set_default_exception_handler(custom_exception_handler)

    @app.route("/custom-exception")
    def custom_exception_handler():
        raise AttributeError

    response = test_client.get("http://testserver/custom-exception")
    assert response.text == "Something went wrong."
    assert response.status_code == 500


def test_non_existent_static_file(test_client):
    assert test_client.get("http://testserver/static/nonexistent.css").status_code == 404


def test_serving_static_file(test_client):
    response = test_client.get("http://testserver/static/test.css")

    assert response.text == "body { background-color: chocolate; }"


def test_middleware_methods_are_called(app, test_client):
    request_processed = False
    response_processed = False

    class SimpleMiddleware(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, req):
            nonlocal request_processed
            request_processed = True

        def process_response(self, req, res):
            nonlocal response_processed
            response_processed = True

    app.add_middleware(SimpleMiddleware)

    @app.route("/initial")
    def initial(req, res):
        res.text = "Hello from initial."

    test_client.get("http://testserver/initial")

    assert request_processed is True
    assert response_processed is True


def test_allowed_methods(app, test_client):
    @app.route("/home", allowed_methods=["post"])
    def home(req, res):
        res.text = "Hello from home."

    response = test_client.get("http://testserver/home")

    assert response.status_code == 405
    assert response.text == "Method Not Allowed."


def test_json_helper(app, test_client):

    @app.route("/json", allowed_methods=["get"])
    def json_response(req, res):
        json_data = {"name": "My name is fulan ibn fulan", "type": "json"}
        res.json = json_data

    response = test_client.get("http://testserver/json")
    assert "application/json" in response.headers["Content-Type"]
    assert response.json()["name"] == "My name is fulan ibn fulan"


def test_text_helper(app, test_client):
    @app.route("/text", allowed_methods=["get"])
    def text_response(req, res):
        res.text = "Hello from text."

    response = test_client.get("http://testserver/text")
    assert response.text == "Hello from text."
    assert "text/plain" in response.headers["Content-Type"]
