from app.database import get_connection


# =========================
# CREATE CLIENTE
# =========================
def create_cliente(data):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO clientes (
                nome,
                telefone,
                email,
                senha,
                cpf,
                rg
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data["nome"],
            data["telefone"],
            data["email"],
            data["senha"],
            data["cpf"],
            data["rg"]
        ))

        cliente_id = cursor.fetchone()["id"]

        # ENDEREÇO
        cursor.execute("""
            INSERT INTO enderecos (
                cep,
                numero,
                complemento,
                cliente_id
            )
            VALUES (%s, %s, %s, %s)
        """, (
            data["cep"],
            data["numero"],
            data["complemento"],
            cliente_id
        ))

        return conn, cursor, cliente_id

    except:
        raise

    finally:
        pass


# =========================
# CREATE DEPENDENTE
# =========================
def create_dependente(cursor, data, cliente_id):

    cursor.execute("""
        INSERT INTO dependentes (
            nome,
            data_nascimento,
            parentesco,
            cliente_id
        )
        VALUES (%s, %s, %s, %s)
    """, (
        data["nome_dependente"],
        data["data_nascimento"],
        data["parentesco"],
        cliente_id
    ))


# =========================
# CREATE PET
# =========================
def create_pet(cursor, data, cliente_id):

    cursor.execute("""
        INSERT INTO pets (
            nome,
            especie,
            raca,
            cliente_id
        )
        VALUES (%s, %s, %s, %s)
    """, (
        data["nome_pet"],
        data["especie"],
        data["raca"],
        cliente_id
    ))


# =========================
# BUSCAR USUÁRIO POR EMAIL
# =========================
def find_user_by_email(email):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT

                c.id,
                c.nome,
                c.telefone,
                c.email,
                c.senha,
                c.cpf,
                c.rg,

                e.cep,
                e.numero,
                e.complemento

            FROM clientes c

            LEFT JOIN enderecos e
            ON e.cliente_id = c.id

            WHERE c.email = %s
        """, (email,))

        usuario = cursor.fetchone()

        return usuario

    except:
        raise

    finally:
        cursor.close()
        conn.close()


# =========================
# BUSCAR POR CPF
# =========================
def find_user_by_cpf(cpf):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT * FROM clientes WHERE cpf = %s",
            (cpf,)
        )

        usuario = cursor.fetchone()

        return usuario

    except:
        raise

    finally:
        cursor.close()
        conn.close()


# =========================
# BUSCAR POR RG
# =========================
def find_user_by_rg(rg):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT * FROM clientes WHERE rg = %s",
            (rg,)
        )

        usuario = cursor.fetchone()

        return usuario

    except:
        raise

    finally:
        cursor.close()
        conn.close()


# =========================
# BUSCAR POR TELEFONE
# =========================
def find_user_by_telefone(tel):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT * FROM clientes WHERE telefone = %s",
            (tel,)
        )

        usuario = cursor.fetchone()

        return usuario

    except:
        raise

    finally:
        cursor.close()
        conn.close()