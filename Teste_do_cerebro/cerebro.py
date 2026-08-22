import sqlite3 #Importa as funções sql no python
import config

def replicar_identidade():
    conexao_identidade = sqlite3.connect(config.identidade)
    cursor_identidade = conexao_identidade.cursor()
    cursor_identidade.execute("SELECT * FROM identidade")
    resultado_identidade = cursor_identidade.fetchone()
    conexao_identidade.close()
    return str(resultado_identidade)
    
def replicar_identidade():
    conexao_usuarios = sqlite3.connect(config.identidade)
    cursor_identidade = conexao_identidade.cursor()
    cursor_identidade.execute("SELECT * FROM identidade")
    resultado_identidade = cursor_identidade.fetchone()
    conexao_identidade.close()
    return str(resultado_identidade)