# Python Web Framework for learning purposes

Marhaba App is a Python web framework built to learn how a framework works behind.

It's a WSGI framework that can be used any WSGI application server like Gunicorn.


## Installation
```shell
pip install marhaba-app
```

## How to use

## Basic usage
```python
from marhaba_app.app import MarhabaApp

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


def default_exception_handler(request, response):
    response.text = "Something wrong happened."
    response.status = 500

app.set_default_exception_handler(default_exception_handler)



@app.route("/json-page")
def json_page(request, response):
    response.json = {"name": "Falon", "info": "Falan ibn fulan"}

```

## Unit tests
The recommended way of writing tests is using Pytest. 
There are two built-in fixtures. One is app, the main Marhaba app instance.
```python
import pytest

def test_duplicate_route_throws_exc(app):
    @app.route("/home")
    def home(req, res):
        res.text = "Hello from home"

    with pytest.raises(AssertionError):
        @app.route("/home")
        def home2(req, res):
            res.text = "Hello from home2"

```

Another is test-client, the api client to send HTTP requests to the handlers.
```python
def test_parametrized_routing(app, test_client):
    @app.route("/hello/{name}")
    def hello(req, res, name):
        res.text = f"Hello {name}"

    assert test_client.get("http://testserver/hello/John").text == "Hello John"
    assert test_client.get("http://testserver/hello/Brake").text == "Hello Brake"
```

## Templates

The default directory for templates is `templates`. You can change it when initializing the app.
Then you can use HTML files.
```python
from marhaba_app.app import MarhabaApp

app = MarhabaApp(templates="templates_dir_name")

@app.route("/home")
def template(request, response):
    response.body = app.template(
        "home.html",
        context={"title": "Home page", "body": "Hello from home page", "name": "Bekzod"}
    )
```

The default directory for static files is `static`. You can change it when initializing the app.
```python
from marhaba_app.app import MarhabaApp

app = MarhabaApp(static_dir="static_dir_name")
```
Then you can use static files inside HTML documents.
```html
<html lang="en">
    <header>
        <title>{{title}}</title>

        <link rel="stylesheet" href="/static/home.css">
    </header>
    <body>
        Hello, <b>{{name}}</b>.
        <p>Welcome to my custom framework.</p>
    </body>
</html>
```

## Middleware
You can create custom middleware by inheriting from `marhaba_app.middleware.Middleware`
and overriding two methods which are called before and after request.
```python
from marhaba_app.app import MarhabaApp
from marhaba_app.middleware import Middleware

app = MarhabaApp()

class CustomMiddleware(Middleware):
    def process_request(self, req):
        print("Request is being called.", req.url)

    def process_response(self, req, resp):
        print("Response has been generated.", req.url)

app.add_middleware(CustomMiddleware)
```
