from flask import Blueprint, render_template, request, redirect, session, url_for
from app.controllers.user_controller import cadastrar_usuario, realizar_login, gerar_codigo_2fa, enviar_codigo_email

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
        mensagem="Erro ao cadastrar!",
        tipo="erro"
    )

# ========================
# LOGIN
# ========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    result = realizar_login(request.form)
    session["tentativas"] = 0

    while session.get("tentativas") <= 3:
        if result["success"]:
            usuario = result["usuario"]

            # Gerar codigo de autenticação em 2 Fatores (2FA)
            codigo, expiracao = gerar_codigo_2fa()

            # Salva dados temporários na sessão
            session["usuario_nome"] = usuario["nome"]
            session["usuario_temp_id"] = usuario["id"]
            session["codigo_2fa"] = codigo
            session["codigo_expira"] = expiracao.strftime("%Y-%m-%d %H:%M:%S")

            # envia email
            enviar_codigo_email(usuario["email"], codigo)

            return redirect(url_for("auth.verificar_2fa"))
    
        return render_template(
            "login.html",
            mensagem=result["erro"],
            tipo="erro"
        )
    
    else:
        pass
        # Tempo de espera
   
# ========================
# Autenticação 2FA
# ========================
@auth_bp.route("/verificar-2fa", methods=["GET", "POST"])
def verificar_2fa():
    if request.method == "POST":
        codigo_digitado = request.form["codigo"]
        codigo_salvo = session.get("codigo_2fa")
        expiracao = session.get("codigo_expira")

        if not codigo_salvo:
            return "Sessão expirada"

        # verifica expiração
        if datetime.now() > datetime.strptime(expiracao, "%Y-%m-%d %H:%M:%S"):
            session.clear()
            return render_template(
                "2fa.html.html",
                mensagem="Código expirado. Faça login novamente.",
                tipo="erro"
            )

        if codigo_digitado == codigo_salvo:
            # Cria a sessão real do usuário com duração de 30min
            session.permanent = True  # ativa expiração (30 min)

            # login definitivo
            session["usuario_id"] = session["usuario_temp_id"]

            # limpa dados temporários
            session.pop("codigo_2fa", None)
            session.pop("codigo_expira", None)
            session.pop("usuario_temp_id", None)

            return redirect("/indexUsers")

        return "Código inválido"

    return render_template("2fa.html")

# ========================
# LOGOUT
# ========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")