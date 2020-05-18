from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="../static")
    # existing code omitted

    from . import views

    app.register_blueprint(views.bp)

    return app
