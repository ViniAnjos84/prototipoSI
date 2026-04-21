from flask import Blueprint, render_template, request, redirect, session
from app.controllers.user_controller import cadastrar_usuario, realizar_login

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

    if result["success"]:
        usuario = result["usuario"]

        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        
        return redirect("/indexUsers")
    

    return render_template(
        "login.html",
        mensagem=result["erro"],
        tipo="erro"
    )
   
# ========================
# LOGOUT
# ========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")