from app.models.user_model import create_cliente
from app.models.user_model import find_user_by_email, find_user_by_cpf, find_user_by_telefone
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from email.mime.text import MIMEText
import random, smtplib, os


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=8
)

def cadastrar_usuario(form):
    try:
    
        senha = form.get("senha")
        senha_ver = form.get("senhaVER")

        # Validar senha
        if senha != senha_ver:
            return {
                "success": False,
                "erro": "As senhas não coincidem"
            }

        # Verificar dados duplicados
        usuario_existente = find_user_by_email(form.get("email"))
        if usuario_existente:
            return {
                "success": False,
                "erro": "Email já cadastrado"
            }

        usuario_existente = find_user_by_cpf(form.get("cpf"))
        if usuario_existente:
            return {
                "success": False,
                "erro": "CPF já cadastrado"
            }

        usuario_existente = find_user_by_telefone(form.get("telefone"))
        if usuario_existente:
            return {
                "success": False,
                "erro": "Telefone já cadastrado"
            }

        senha_hash = ph.hash(form.get("senha"))

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

        #tipo = form.get("tipoCadastro")

        #if tipo == "dependente":
        #    create_dependente(cursor, data, cliente_id)

        #elif tipo == "pet":
        #    create_pet(cursor, data, cliente_id)

        # Salva as alterações no banco
        conn.commit()

        return {"success": True}

    except Exception:
        import traceback
        traceback.print_exc()
        return {"success": False}

    # Sempre executado
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def realizar_login(form):
    email = form.get("email")
    senha = form.get("senha")

    usuario = find_user_by_email(email)

    if not usuario:
        return {"success": False, "erro": "Usuário não encontrado"}
    
    try:
        ph.verify(usuario["senha"], senha)
    except:
        return {"success": False, "erro": "Senha incorreta"}

    return {
        "success": True,
        "usuario": usuario
    }

def gerar_codigo_2fa():
    codigo = str(random.randint(100000, 999999))
    expiracao = datetime.now() + timedelta(minutes=5)
    
    return codigo, expiracao

def enviar_codigo_email(destinatario, codigo):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA")

    msg = MIMEText(f"Seu código de verificação é: {codigo}")
    msg["Subject"] = "Código de verificação"
    msg["From"] = remetente
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.send_message(msg)
