import secrets
from flask import Flask
from datetime import timedelta

def create_app():
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static"
    )

    # Configuração da aplicação (feito quando o sistema inicia)
    app.secret_key = secrets.token_hex(32)
    app.permanent_session_lifetime = timedelta(minutes=10)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
