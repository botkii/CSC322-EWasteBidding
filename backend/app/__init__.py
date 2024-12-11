#App Factory for Flask Initialization
from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configurations
    CORS(app)

    # Register items blueprint
    from app.api.items import items_api  # Import the items blueprint
    app.register_blueprint(items_api, url_prefix="/api/v1")

    from app.api.users import users_api
    app.register_blueprint(users_api, url_prefix="/api/v1/users")

    return app