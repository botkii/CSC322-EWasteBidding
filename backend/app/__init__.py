#App Factory for Flask Initialization
from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configurations
    CORS(app)

    from app.api.test import test_api
    app.register_blueprint(test_api, url_prefix="/api/v1/test")

    return app