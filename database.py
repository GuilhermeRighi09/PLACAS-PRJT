import psycopg2
from datetime import datetime, timedelta

# Configurações do seu banco PostgreSQL
DB_HOST = "localhost"
DB_NAME = "leitorplacas"
DB_USER = "postgres"
DB_PASS = "1234"


def conectar():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)


def criar_banco_e_tabelas():
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Tabela de veículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos (
                id SERIAL PRIMARY KEY,
                placa VARCHAR(10) UNIQUE NOT NULL,
                proprietario VARCHAR(100),
                modelo VARCHAR(50),
                status VARCHAR(20) NOT NULL
            )
        ''')

        # Tabela de histórico (ADICIONADA A COLUNA PROPRIETARIO)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_acesso (
                id SERIAL PRIMARY KEY,
                placa_lida VARCHAR(10) NOT NULL,
                proprietario VARCHAR(100),
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status_acesso VARCHAR(20) NOT NULL,
                leitor_usado VARCHAR(50)
            )
        ''')

        veiculos_teste = [
            ('ABC1234', 'João Silva', 'Fiat Uno', 'Liberada'),
            ('FJL1234', 'Maria Souza', 'Honda Civic', 'Bloqueada'),
            ('BRA0S11', 'Carlos Santos', 'VW Gol', 'Pendências'),
            ('SEN4I24', 'Oficial SENAI', 'Chevrolet Onix', 'Liberada')
        ]

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                login VARCHAR(50) UNIQUE NOT NULL,
                senha VARCHAR(100) NOT NULL,   
                placa VARCHAR(10) NOT NULL     
                )
            ''')

        for placa, prop, modelo, status in veiculos_teste:
            cursor.execute('''
                INSERT INTO veiculos (placa, proprietario, modelo, status) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (placa) DO NOTHING
            ''', (placa, prop, modelo, status))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabelas sincronizadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")


# FUNÇÃO CORRIGIDA: Agora retorna status E proprietário
def buscar_dados_veiculo(placa):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT status, proprietario FROM veiculos WHERE placa = %s', (placa,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado:
            return resultado[0], resultado[1]  # Retorna (status, dono)
        return "Não Cadastrada", "Desconhecido"
    except Exception as e:
        print(f"Erro no banco: {e}")
        return "Erro Banco", "Erro"


# FUNÇÃO CORRIGIDA: Agora aceita o proprietário para salvar no histórico
def registrar_historico(placa, status, leitor, proprietario):
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Opcional: Evita duplicados em menos de 10 segundos
        cursor.execute('''
            SELECT id FROM registros_acesso 
            WHERE placa_lida = %s AND data_hora > %s
        ''', (placa, datetime.now() - timedelta(seconds=10)))

        if cursor.fetchone():
            return

        cursor.execute('''
            INSERT INTO registros_acesso (placa_lida, status_acesso, leitor_usado, proprietario)
            VALUES (%s, %s, %s, %s)
        ''', (placa, status, leitor, proprietario))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar histórico: {e}")