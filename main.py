from marhaba_app.app import MarhabaApp
from marhaba_app.middleware import Middleware

app = MarhabaApp()


@app.route("/about")
def about(request, response):
    response.text = "Welcome to About page. Enjoy coding."


@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello {name}! Welcome to Greeting page."


@app.route("/books")
class Book:
    def get(self, request, response):
        response.text = "Welcome to Books page. Enjoy coding."

    def post(self, request, response):
        response.text = "Page to create books. Enjoy coding."


def new_handler(request, response):
    response.text = "Hello from new handler. Enjoy coding."


app.add_route("/new-handler", new_handler)


@app.route("/home")
def template(request, response):
    response.body = app.template(
        "home.html",
        context={"title": "Home page", "body": "Hello from home page", "name": "Bekzod"}
    )


def default_exception_handler(request, response):
    response.text = "Something wrong happened."
    response.status = 500


app.set_default_exception_handler(default_exception_handler)


@app.route("/exception")
def exception_page():
    raise AssertionError


class LoggingMiddleware(Middleware):
    def process_request(self, req):
        print("Request is being called.", req.url)

    def process_response(self, req, resp):
        print("Response has been generated.", req.url)


app.add_middleware(LoggingMiddleware)


@app.route("/json-page")
def json_page(request, response):
    response.json = {"name": "Falon", "info": "Falan ibn fulan"}
