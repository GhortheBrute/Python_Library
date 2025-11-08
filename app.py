import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (senha do banco, etc.)
load_dotenv()

app = Flask(__name__)

# --- 1. Configuração do Banco de Dados ---
# Vamos pegar as credenciais do seu arquivo .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# String de conexão SQLAlchemy para MySQL (usando pymysql que instalamos)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Desativa um recurso do SQLAlchemy que não usaremos e que consome recursos
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa o objeto 'db' (o ORM) com o seu app.
# É essa variável 'db' que usaremos para criar e consultar tabelas.
db = SQLAlchemy(app)
# --- Fim da Configuração ---

# Rota principal (view)
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

# Bloco de execução
if __name__ == '__main__':
    # Habilitamos o 'debug=True'
    # Isso faz o servidor reiniciar automaticamente quando você salvar o arquivo.
    app.run(debug=True)