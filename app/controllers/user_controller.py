from app.models.user_model import create_cliente, create_dependente, create_pet
from app.models.user_model import find_user_by_email
from argon2 import PasswordHasher
import random

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

        # Verificar email duplicado
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

        usuario_existente = find_user_by_rg(form.get("rg"))
        if usuario_existente:
            return {
                "success": False,
                "erro": "RG já cadastrado"
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
            "rg": form.get("rg"),
            "cep": form.get("cep"),
            "numero": form.get("numero"),
            "complemento": form.get("complemento"),
            "nome_dependente": form.get("nome_dependente"),
            "data_nascimento": form.get("data_nascimento"),
            "parentesco": form.get("parentesco"),
            "nome_pet": form.get("nome_pet"),
            "especie": form.get("especie"),
            "raca": form.get("raca"),
        }

        conn, cursor, cliente_id = create_cliente(data)

        tipo = form.get("tipoCadastro")

        if tipo == "dependente":
            create_dependente(cursor, data, cliente_id)

        elif tipo == "pet":
            create_pet(cursor, data, cliente_id)

        # Salva as alterações no banco
        conn.commit()

        return {"success": True}

    except Exception as e:
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
    return str(random.randint(100000, 999999))


