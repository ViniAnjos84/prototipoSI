from app.models.user_model import (
    create_cliente,
    create_dependente,
    create_pet,
    find_user_by_email,
    find_user_by_cpf,
    find_user_by_telefone,
    salvar_consentimento,
    revogar_consentimento,
    update_cliente,
    update_senha,
    buscar_consentimento_ativo as _buscar_consentimento_ativo,
    create_log_auth,
)
from app.database import get_connection
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from email.mime.text import MIMEText
from flask import request
import secrets
import smtplib
import os
import re
 
 
# =========================
# PASSWORD HASHER
# =========================
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=8
)
 
 
# =========================
# BUSCAR CONSENTIMENTO ATIVO
# =========================
def buscar_consentimento_ativo(cliente_id):
    return _buscar_consentimento_ativo(cliente_id)
 
 
# =========================
# VALIDAR SENHA
# =========================
def validar_nova_senha(senha):
 
    if len(senha) < 8:
        return "A senha deve ter no mínimo 8 caracteres"
 
    if not re.search(r"[A-Z]", senha):
        return "A senha deve conter letra maiúscula"
 
    if not re.search(r"[a-z]", senha):
        return "A senha deve conter letra minúscula"
 
    if not re.search(r"\d", senha):
        return "A senha deve conter número"
 
    if not re.search(r"[^A-Za-z0-9]", senha):
        return "A senha deve conter caractere especial"
 
    return None
 
 
# =========================
# CADASTRAR USUÁRIO
# =========================
def cadastrar_usuario(form):
 
    conn = None
    cursor = None
 
    try:
 
        if not form.get("termos"):
 
            return {
                "success": False,
                "erro": "Você precisa aceitar os termos."
            }
 
        senha = form.get("senha", "").strip()
        senha_ver = form.get("senhaVER", "").strip()
 
        if senha != senha_ver:
 
            return {
                "success": False,
                "erro": "As senhas não coincidem"
            }
 
        erro_validacao = validar_nova_senha(senha)
 
        if erro_validacao:
 
            return {
                "success": False,
                "erro": erro_validacao
            }
 
        if find_user_by_email(form.get("email")):
 
            return {
                "success": False,
                "erro": "Email já cadastrado"
            }
 
        if find_user_by_cpf(form.get("cpf")):
 
            return {
                "success": False,
                "erro": "CPF já cadastrado"
            }
 
        if find_user_by_telefone(form.get("telefone")):
 
            return {
                "success": False,
                "erro": "Telefone já cadastrado"
            }
 
        senha_hash = ph.hash(senha)
 
        data = {
            "nome": form.get("nome"),
            "telefone": form.get("telefone"),
            "email": form.get("email"),
            "senha": senha_hash,
            "cpf": form.get("cpf"),
            "cep": form.get("cep"),
            "nome_dependente": form.get("nome_dependente"),
            "data_nascimento": form.get("data_nascimento"),
            "parentesco": form.get("parentesco"),
            "nome_pet": form.get("nome_pet"),
            "especie": form.get("especie"),
            "raca": form.get("raca"),
        }
 
        conn, cursor, cliente_id = create_cliente(data)
 
        if form.get("nome_dependente"):
            create_dependente(cursor, data, cliente_id)
 
        if form.get("nome_pet"):
            create_pet(cursor, data, cliente_id)
 
        salvar_consentimento(
            cursor=cursor,
            cliente_id=cliente_id,
            aceitou=True,
            versao_termo="1.0",
            ip_aceite=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )
 
        conn.commit()
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao cadastrar usuário: {e}")
 
        if conn:
            conn.rollback()
 
        return {
            "success": False,
            "erro": "Erro ao cadastrar usuário"
        }
 
    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception:
            pass
 
 
# =========================
# LOGIN
# =========================
def realizar_login(form, ip=None, user_agent=None):
 
    email = form.get("email")
    senha = form.get("senha")
 
    usuario = find_user_by_email(email)
 
    if not usuario:
 
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Usuário não encontrado"
        )
 
        return {
            "success": False,
            "erro": "Usuário não encontrado"
        }
 
    try:
 
        ph.verify(usuario["senha"], senha)
 
    except Exception:
 
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Senha incorreta"
        )
 
        return {
            "success": False,
            "erro": "Senha incorreta"
        }
 
    create_log_auth(
        email=email,
        sucesso=True,
        ip=ip,
        user_agent=user_agent
    )
 
    return {
        "success": True,
        "usuario": usuario
    }
 
 
# =========================
# GERAR CÓDIGO 2FA
# =========================
def gerar_codigo_2fa():
 
    codigo = secrets.randbelow(900000) + 100000
    expiracao = datetime.now() + timedelta(minutes=5)
 
    return codigo, expiracao
 
 
# =========================
# ENVIAR EMAIL 2FA
# =========================
def enviar_codigo_email(destinatario, codigo):
 
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")
 
    msg = MIMEText(
        f"Seu código de verificação é: {codigo}"
    )
 
    msg["Subject"] = "Código de verificação"
    msg["From"] = remetente
    msg["To"] = destinatario
 
    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
 
        servidor.starttls()
 
        servidor.login(
            remetente,
            senha
        )
 
        servidor.send_message(msg)
 
 
# =========================
# REVOGAR ACEITE
# =========================
def revogar_aceite_controller(session):
 
    cliente_id = session.get("usuario_id")
 
    if not cliente_id:
 
        return {
            "success": False
        }
 
    try:
 
        revogar_consentimento(cliente_id)
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao revogar aceite: {e}")
 
        return {
            "success": False
        }
 
 
# =========================
# ACEITAR TERMOS NOVAMENTE
# =========================
def aceitar_termos_novamente(session, request):
 
    cliente_id = session.get("usuario_id")
 
    if not cliente_id:
 
        return {
            "success": False
        }
 
    conn = None
    cursor = None
 
    try:
 
        conn = get_connection()
        cursor = conn.cursor()
 
        salvar_consentimento(
            cursor=cursor,
            cliente_id=cliente_id,
            aceitou=True,
            versao_termo="1.0",
            ip_aceite=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )
 
        conn.commit()
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao aceitar termos novamente: {e}")
 
        if conn:
            conn.rollback()
 
        return {
            "success": False
        }
 
    finally:
 
        try:
 
            if cursor:
                cursor.close()
 
            if conn:
                conn.close()
 
        except Exception:
            pass
 
 
# =========================
# EDITAR DADOS
# =========================
def editar_dados_controller(session, form):
 
    cliente_id = session.get("usuario_id")
 
    if not cliente_id:
 
        return {
            "success": False,
            "erro": "Sessão inválida."
        }
 
    novo_nome = form.get("nome", "").strip()
    novo_telefone = form.get("telefone", "").strip()
    novo_email = form.get("email", "").strip()
    novo_cep = form.get("cep", "").strip()
 
    if not all([
        novo_nome,
        novo_telefone,
        novo_email,
        novo_cep
    ]):
 
        return {
            "success": False,
            "erro": "Todos os campos são obrigatórios."
        }
 
    usuario_email = find_user_by_email(novo_email)
 
    if usuario_email and str(usuario_email["id"]) != str(cliente_id):
 
        return {
            "success": False,
            "erro": "Este e-mail já está em uso."
        }
 
    usuario_tel = find_user_by_telefone(novo_telefone)
 
    if usuario_tel and str(usuario_tel["id"]) != str(cliente_id):
 
        return {
            "success": False,
            "erro": "Este telefone já está em uso."
        }
 
    try:
 
        update_cliente(cliente_id, {
            "nome": novo_nome,
            "telefone": novo_telefone,
            "email": novo_email,
            "cep": novo_cep,
        })
 
        session["usuario_nome"] = novo_nome
        session["usuario_telefone"] = novo_telefone
        session["usuario_email"] = novo_email
        session["usuario_cep"] = novo_cep
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao editar dados: {e}")
 
        return {
            "success": False,
            "erro": "Erro ao atualizar os dados."
        }
 
 
# =========================
# REDEFINIR SENHA
# =========================
def redefinir_senha(email, form):
 
    try:
 
        nova_senha = form.get(
            "nova_senha",
            ""
        ).strip()
 
        confirmar_senha = form.get(
            "confirmar_senha",
            ""
        ).strip()
 
        if not nova_senha or not confirmar_senha:
 
            return {
                "success": False,
                "erro": "Preencha todos os campos"
            }
 
        if nova_senha != confirmar_senha:
 
            return {
                "success": False,
                "erro": "As senhas não coincidem"
            }
 
        erro_validacao = validar_nova_senha(nova_senha)
 
        if erro_validacao:
 
            return {
                "success": False,
                "erro": erro_validacao
            }
 
        usuario = find_user_by_email(email)
 
        if not usuario:
 
            return {
                "success": False,
                "erro": "Usuário não encontrado"
            }
 
        senha_hash = ph.hash(nova_senha)
 
        atualizado = update_senha(
            usuario["id"],
            senha_hash
        )
 
        if not atualizado:
 
            return {
                "success": False,
                "erro": "Erro ao atualizar senha"
            }
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao redefinir senha: {e}")
 
        return {
            "success": False,
            "erro": "Erro interno ao redefinir senha"
        }


# =========================
# SALVAR DEPENDENTE
# =========================
def salvar_dependente_controller(session, form):
 
    cliente_id = session.get("usuario_id")
 
    if not cliente_id:
 
        return {
            "success": False
        }
 
    conn = None
    cursor = None
 
    try:
 
        conn = get_connection()
        cursor = conn.cursor()
 
        data = {
            "nome_dependente": form.get("nome_dependente"),
            "data_nascimento": form.get("data_nascimento"),
            "parentesco": form.get("parentesco"),
        }
 
        create_dependente(
            cursor,
            data,
            cliente_id
        )
 
        conn.commit()
 
        session["usuario_dependente"] = data["nome_dependente"]
        session["usuario_parentesco"] = data["parentesco"]
        session["usuario_data_nascimento"] = data["data_nascimento"]
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao salvar dependente: {e}")
 
        if conn:
            conn.rollback()
 
        return {
            "success": False
        }
 
    finally:
 
        try:
 
            if cursor:
                cursor.close()
 
            if conn:
                conn.close()
 
        except Exception:
            pass
 
 
# =========================
# SALVAR PET
# =========================
def salvar_pet_controller(session, form):
 
    cliente_id = session.get("usuario_id")
 
    if not cliente_id:
 
        return {
            "success": False
        }
 
    conn = None
    cursor = None
 
    try:
 
        conn = get_connection()
        cursor = conn.cursor()
 
        data = {
            "nome_pet": form.get("nome_pet"),
            "especie": form.get("especie"),
            "raca": form.get("raca"),
        }
 
        create_pet(
            cursor,
            data,
            cliente_id
        )
 
        conn.commit()
 
        session["usuario_pet"] = data["nome_pet"]
        session["usuario_especie"] = data["especie"]
        session["usuario_raca"] = data["raca"]
 
        return {
            "success": True
        }
 
    except Exception as e:
 
        print(f"Erro ao salvar pet: {e}")
 
        if conn:
            conn.rollback()
 
        return {
            "success": False
        }
 
    finally:
 
        try:
 
            if cursor:
                cursor.close()
 
            if conn:
                conn.close()
 
        except Exception:
            pass