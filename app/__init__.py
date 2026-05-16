import secrets
from flask import Flask
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Limita a quantidade de tentativas de acesso do usuario
limiter = Limiter(
    key_func=get_remote_address,
    
    # Limites globais para TODAS as rotas da aplicação
    default_limits=["2000 per day", "200 per hour"]
)

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

    limiter.init_app(app)
    from flask import render_template
    
    @app.errorhandler(429)
    def ratelimit_handler(e):

        return render_template(
            "login.html",
            mensagem="Muitas tentativas de login. Aguarde alguns minutos.",
            tipo="erro",
            tentativas_restantes=0
        ), 429

    return app
