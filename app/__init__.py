from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static"
    )

    app.secret_key = "chave_secreta_super_segura" 

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
