import psycopg2

def configurar_projeto():
    # 1. Dados de conexão (AJUSTE SUA SENHA AQUI)
    config = {
        "dbname": "room_db",
        "user": "postgres",
        "password": "mounjaro", 
        "host": "localhost",
        "port": "5432"
    }

    # SQL para criar as tabelas do seu projeto
    comandos_sql = (
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            tipo VARCHAR(20) DEFAULT 'profissional' -- 'admin' ou 'profissional'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS salas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50) NOT NULL,
            localizacao VARCHAR(50), -- ex: SP HQ, NY HQ
            capacidade_max INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS posicoes (
            id SERIAL PRIMARY KEY,
            sala_id INTEGER REFERENCES salas(id) ON DELETE CASCADE,
            coord_x INTEGER,
            coord_y INTEGER,
            tem_pc BOOLEAN DEFAULT FALSE,
            status VARCHAR(20) DEFAULT 'disponivel'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reservas (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            posicao_id INTEGER REFERENCES posicoes(id),
            data_reserva DATE NOT NULL,
            periodo VARCHAR(10) -- 'manha', 'tarde' ou 'integral'
        )
        """
    )

    try:
        print("🔌 Conectando ao banco de dados...")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()

        # Executando cada comando de criação
        for comando in comandos_sql:
            cur.execute(comando)
        
        conn.commit()
        print("✅ Estrutura de tabelas criada com sucesso!")

        # Inserindo um Admin de teste para você já ter alguém no banco
        cur.execute("INSERT INTO usuarios (nome, email, tipo) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    ('Felipe Admin', 'felipe@empresa.com', 'admin'))
        conn.commit()
        print("👤 Usuário administrador de teste inserido.")

        cur.close()
        conn.close()
        print("🚪 Processo finalizado e conexão fechada.")

    except Exception as e:
        print(f"❌ Erro ao configurar o banco: {e}")

if __name__ == "__main__":
    configurar_projeto()