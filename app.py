from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import base64
import os
import uuid
import re
import database
from OCRespecifico import ler_especifico
from OCRnormal import ler_normal

app = Flask(__name__)

app.secret_key = "chave_secreta_super_segura_do_senai"


os.makedirs('fotos', exist_ok=True)


database.criar_banco_e_tabelas()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_form = request.form['login']
        senha_form = request.form['senha']

        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM usuarios WHERE login = %s AND senha = %s", (login_form, senha_form))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            return render_template('index.html')
        else:
            flash("Login ou senha incorretos!")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT placa FROM veiculos ORDER BY placa ASC")
    placas_bd = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        senha = request.form['senha']
        placa = request.form['placa']

        try:
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nome, login, senha, placa)
                VALUES (%s, %s, %s, %s)
            ''', (nome, login, senha, placa))
            conn.commit()
            cursor.close()
            conn.close()

            flash("Usuário cadastrado com sucesso!")
            return redirect(url_for('login'))

        except Exception as e:
            if "usuarios_login_key" in str(e):
                flash("Este login já está cadastrado! Escolha outro.")
            else:
                flash(f"Erro ao cadastrar: {e}")

    return render_template('cadastro_usuario.html', placas=placas_bd)


@app.route('/processar_imagem', methods=['POST'])
def processar_imagem():
    try:
        # 1. Recebe os dados da imagem (Base64) do Front-end
        dados = request.get_json()
        if not dados or 'imagem' not in dados:
            return jsonify({"status": "Erro: Imagem não recebida"}), 400

        imagem_base64 = dados['imagem'].split(',')[1]
        nome_arquivo = f"fotos/captura_{uuid.uuid4().hex}.jpg"


        with open(nome_arquivo, "wb") as fh:
            fh.write(base64.b64decode(imagem_base64))


        resultado_esp = ler_especifico(nome_arquivo)
        resultado_norm = ler_normal(nome_arquivo)

        # Valores padrão
        status_exibicao = "Aguardando..."
        proprietario = "Desconhecido"
        placa_limpa = ""


        if "✅" in resultado_esp:

            busca = re.search(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}', resultado_esp)

            if busca:
                placa_limpa = busca.group()


                status_db, prop_db = database.buscar_dados_veiculo(placa_limpa)
                proprietario = prop_db


                if status_db == "Liberada":
                    status_exibicao = "Liberada"
                elif status_db == "Não Cadastrada":
                    status_exibicao = "Acesso Negado"
                else  :
                    status_exibicao = status_db


                database.registrar_historico(placa_limpa, status_exibicao, "EasyOCR Específico", proprietario)

        elif "❌" in resultado_esp:
            status_exibicao = "Placa ilegível"


        return jsonify({
            "especifico": resultado_esp,
            "normal": resultado_norm,
            "status": status_exibicao,
            "placa_lida": placa_limpa,
            "proprietario": proprietario
        })

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return jsonify({"status": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    # Roda o servidor Flask
    app.run(debug=True, port=5000)