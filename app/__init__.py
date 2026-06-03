import secrets
from flask import Flask
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman  # <--- ADICIONEI ESTA LINHA
 
# Limita a quantidade de tentativas de acesso do usuario
# Requisito 1.11: Proteção contra força bruta (rate limit,bloqueio, atraso)
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
 
    # Configuraçôs da aplicação (feito quando o sistema inicia)
    app.secret_key = secrets.token_hex(32)

    # Requisito 1.9 Sessões com tempo de expiração
    app.permanent_session_lifetime = timedelta(minutes=10)
 
    # =======================================================
    # CONFIGURAÇÕES DE PROTEÇÃO DE COOKIE PARA TLS/HTTPS
    # Requisito 3.1: Comunicação protegida por TLS/HTTPS
    # =======================================================
    # 1. Garante que o cookie de sessão SÓ trafegará se a URL for HTTPS
    app.config['SESSION_COOKIE_SECURE'] = True
   
    # 2. Impede que códigos JavaScript tenham acesso ao cookie (previne ataques XSS)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
   
    # 3. Restringe o envio do cookie em requisições de sites terceiros (previne ataques CSRF)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # =======================================================
 
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
 
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Requisito 1.11: Proteção contra força bruta (rate limit,bloqueio, atraso)
    limiter.init_app(app)
 
    # =======================================================
    # CONFIGURAÇÃO DO FLASK-TALISMAN (BLOQUEIO DE HTTP)
    # # Requisito 3.2: Bloqueio de conexões não seguras
    # =======================================================
    # force_https=True garante que conexões HTTP normais sejam recusadas e redirecionadas para HTTPS.
    # content_security_policy=None é usado temporariamente para que o Talisman não bloqueie os estilos CSS locais do seu protótipo.
    Talisman(app, force_https=True, content_security_policy=None)
    # =======================================================
 
    from flask import render_template
   
   # Requisito 1.11: Proteção contra força bruta (rate limit,bloqueio, atraso)
    @app.errorhandler(429)
    def ratelimit_handler(e):
 
        return render_template(
            "login.html",
            mensagem="Muitas tentativas de login. Aguarde alguns minutos.",
            tipo="erro",
            tentativas_restantes=0
        ), 429
 
    return app