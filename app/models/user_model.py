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
                cpf
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data["nome"],
            data["telefone"],
            data["email"],
            data["senha"],
            data["cpf"]
        ))

        cliente_id = cursor.fetchone()["id"]

        cursor.execute("""
            INSERT INTO enderecos (
                cep,
                cliente_id
            )
            VALUES (%s, %s)
        """, (
            data["cep"],
            cliente_id
        ))

        return conn, cursor, cliente_id

    except:
        conn.rollback()
        raise


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
                e.cep
            FROM clientes c
            LEFT JOIN enderecos e
            ON e.cliente_id = c.id
            WHERE c.email = %s
        """, (email,))

        return cursor.fetchone()

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

        return cursor.fetchone()

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

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


# =========================
# SALVAR CONSENTIMENTO
# =========================
def salvar_consentimento(
    cursor,
    cliente_id,
    aceitou=True,
    versao_termo="1.0",
    ip_aceite=None,
    user_agent=None
):

    cursor.execute("""
        INSERT INTO consentimentos_termos (
            cliente_id,
            aceitou,
            versao_termo,
            ip_aceite,
            user_agent
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        cliente_id,
        aceitou,
        versao_termo,
        ip_aceite,
        user_agent
    ))


# =========================
# BUSCAR CONSENTIMENTO ATIVO
# =========================
def buscar_consentimento_ativo(cliente_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT *
            FROM consentimentos_termos
            WHERE cliente_id = %s
              AND aceitou = TRUE
              AND data_revogacao IS NULL
            ORDER BY data_aceite DESC
            LIMIT 1
        """, (cliente_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


# =========================
# REVOGAR CONSENTIMENTO
# =========================
def revogar_consentimento(cliente_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE consentimentos_termos
            SET
                aceitou = FALSE,
                data_revogacao = CURRENT_TIMESTAMP
            WHERE cliente_id = %s
              AND aceitou = TRUE
              AND data_revogacao IS NULL
        """, (cliente_id,))

        conn.commit()

    finally:
        cursor.close()
        conn.close()


# =========================
# ATUALIZAR DADOS CADASTRAIS
# =========================
def update_cliente(cliente_id, data):
    """
    Atualiza nome, telefone, email na tabela clientes
    e cep na tabela enderecos.
    CPF nunca é alterado.
    Retorna dict com os campos que foram de fato alterados,
    ou lança exceção em caso de erro.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE clientes
            SET
                nome     = %s,
                telefone = %s,
                email    = %s
            WHERE id = %s
        """, (
            data["nome"],
            data["telefone"],
            data["email"],
            cliente_id
        ))

        cursor.execute("""
            UPDATE enderecos
            SET cep = %s
            WHERE cliente_id = %s
        """, (
            data["cep"],
            cliente_id
        ))

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()