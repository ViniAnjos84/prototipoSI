from flask import Blueprint, render_template, request, redirect, session, url_for

from app.controllers.user_controller import (
    cadastrar_usuario,
    realizar_login,
    gerar_codigo_2fa,
    enviar_codigo_email
)

from datetime import datetime

auth_bp = Blueprint("auth", __name__)


# ========================
# CADASTRO
# ========================
@auth_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():

    if request.method == "GET":
        return render_template("cadastro.html")

    result = cadastrar_usuario(request.form)

    if result["success"]:

        return render_template(
            "cadastro.html",
            mensagem="Cadastro realizado com sucesso!",
            tipo="sucesso"
        )

    return render_template(
        "cadastro.html",
        mensagem=result.get("erro", "Erro ao cadastrar!"),
        tipo="erro"
    )


# ========================
# LOGIN
# ========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # GET
    if request.method == "GET":
        return render_template("login.html")

    # Inicializa tentativas
    if "tentativas" not in session:
        session["tentativas"] = 0

    # Limite de tentativas
    if session["tentativas"] >= 3:

        return render_template(
            "login.html",
            mensagem="Muitas tentativas. Tente novamente mais tarde.",
            tipo="erro"
        )

    # Login
    result = realizar_login(request.form)

    # Login inválido
    if not result["success"]:

        session["tentativas"] += 1

        return render_template(
            "login.html",
            mensagem=result["erro"],
            tipo="erro"
        )

    usuario = result["usuario"]

    # ========================
    # GERAR 2FA
    # ========================
    codigo, expiracao = gerar_codigo_2fa()

    # ========================
    # SESSÃO
    # ========================
    session["usuario_temp_id"] = usuario["id"]

    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["usuario_telefone"] = usuario["telefone"]

    session["usuario_cep"] = usuario["cep"]
    session["usuario_numero"] = usuario["numero"]
    session["usuario_complemento"] = usuario["complemento"]

    session["usuario_cpf"] = usuario["cpf"]

    # 2FA
    session["codigo_2fa"] = codigo

    session["codigo_expira"] = expiracao.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Envia email
    enviar_codigo_email(
        usuario["email"],
        codigo
    )

    return redirect(
        url_for("auth.verificar_2fa")
    )


# ========================
# VERIFICAR 2FA
# ========================
@auth_bp.route("/verificar-2fa", methods=["GET", "POST"])
def verificar_2fa():

    if request.method == "GET":
        return render_template("2fa.html")

    codigo_digitado = request.form["codigo"]

    codigo_salvo = session.get("codigo_2fa")

    expiracao = session.get("codigo_expira")

    if not codigo_salvo:

        return render_template(
            "2fa.html",
            mensagem="Sessão expirada.",
            tipo="erro"
        )

    # Expiração
    if datetime.now() > datetime.strptime(
        expiracao,
        "%Y-%m-%d %H:%M:%S"
    ):

        session.clear()

        return render_template(
            "2fa.html",
            mensagem="Código expirado.",
            tipo="erro"
        )

    # Código correto
    if codigo_digitado == codigo_salvo:

        session.permanent = True

        session["usuario_id"] = session["usuario_temp_id"]

        # Limpa temporários
        session.pop("codigo_2fa", None)
        session.pop("codigo_expira", None)
        session.pop("usuario_temp_id", None)

        # Reset tentativas
        session["tentativas"] = 0

        return redirect("/perfil")

    return render_template(
        "2fa.html",
        mensagem="Código inválido.",
        tipo="erro"
    )


# ========================
# PERFIL
# ========================
@auth_bp.route("/perfil")
def perfil():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("users/meu-perfil.html")


# ========================
# LOGOUT
# ========================
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")