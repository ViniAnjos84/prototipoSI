from flask import Blueprint, render_template, request, redirect, session, url_for
from app import limiter
from app.models.user_model import find_user_by_email

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

MAX_TENTATIVAS = 5
@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def login():

    # GET
    if request.method == "GET":

        # Inicializa tentativas
        session.setdefault("tentativas", 0)

        return render_template(
            "login.html", 
        )

    # Inicializa tentativas
    session.setdefault("tentativas", 0)

    # Verifica bloqueio
    if session["tentativas"] >= MAX_TENTATIVAS and request.method == "POST":

        return render_template(
            "login.html",
            tipo="erro",
            tentativas_restantes = 0
        )

    # Login
    result = realizar_login(request.form)

    # Login inválido
    if not result["success"]:

        session["tentativas"] += 1
        tentativas_restantes = (MAX_TENTATIVAS - session["tentativas"])

        return render_template(
            "login.html",
            mensagem=result["erro"],
            tipo="erro",
            tentativas_restantes=tentativas_restantes
        )

    usuario = result["usuario"]
    session["tentativas"] = 0

    # Gerar 2FA
    codigo, expiracao = gerar_codigo_2fa()
    print("Codigo Autenticação:", codigo)

    # Sessão
    session["usuario_temp_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["usuario_telefone"] = usuario["telefone"]
    session["usuario_cep"] = usuario["cep"]
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
# RECUPERAÇÃO DE SENHA
# ========================
@auth_bp.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():

    if request.method == "GET":
        return render_template("recuperarSenha.html")

    email = request.form["email"]

    # controller
    usuario = find_user_by_email(email)

    if not usuario:
        return render_template(
            "recuperarSenha.html",
            mensagem="Email não encontrado",
            tipo="erro"
        )

    # gera código
    codigo, expiracao = gerar_codigo_2fa()

    # sessão temporária
    session["reset_user_id"] = usuario["id"]
    session["reset_codigo"] = codigo
    session["reset_expira"] = expiracao.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # envia email
    enviar_codigo_email(email, codigo)

    return redirect(
        url_for("auth.validar_codigo_recuperacao")
    )

@auth_bp.route("/validar-recuperacao", methods=["GET", "POST"])
def validar_codigo_recuperacao():

    # GET → apenas mostra a tela
    if request.method == "GET":
        return render_template("validarCodigoRecuperacao.html")

    # POST → valida código digitado
    codigo_digitado = request.form["codigo"]

    codigo_salvo = session.get("reset_codigo")
    expiracao = session.get("reset_expira")

    # sessão inexistente
    if not codigo_salvo or not expiracao:

        session.clear()

        return render_template(
            "validarCodigoRecuperacao.html",
            mensagem="Sessão expirada. Solicite um novo código.",
            tipo="erro"
        )

    # verifica expiração
    expiracao_datetime = datetime.strptime(
        expiracao,
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expiracao_datetime:

        # limpa apenas dados da recuperação
        session.pop("reset_user_id", None)
        session.pop("reset_codigo", None)
        session.pop("reset_expira", None)

        return render_template(
            "validar_recuperacao.html",
            mensagem="Código expirado. Solicite outro código.",
            tipo="erro"
        )

    # código inválido
    if codigo_digitado != codigo_salvo:

        return render_template(
            "validar_recuperacao.html",
            mensagem="Código inválido.",
            tipo="erro"
        )

    # código válido
    session["reset_validado"] = True

    # remove código usado
    session.pop("reset_codigo", None)
    session.pop("reset_expira", None)

    return redirect(
        url_for("auth.redefinir_senha")
    )

# ========================
# LOGOUT
# ========================
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")