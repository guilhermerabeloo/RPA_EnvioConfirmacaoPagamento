import pyodbc
import os
from configparser import ConfigParser

def sqlPool(operacao, script):
    def readConfig():
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, '..', 'config', 'config.ini')

        config = ConfigParser()
        config.read(config_path)
        return config['DatabaseConfig']

    dadosConfig = readConfig()

    dados_conexao = (
        f"Driver={dadosConfig['Driver']};"
        f"Server={dadosConfig['Server']};"
        f"Database={dadosConfig['Database']};"
        f"UID={dadosConfig['UID']};"
        f"PWD={dadosConfig['PWD']};"
    )

    try: 
        conexao = pyodbc.connect(dados_conexao)
        try:
            cursor = conexao.cursor()
            cursor.execute(script)
            if operacao == 'SELECT':
                result = cursor.fetchall()
            
                return result
            else: 
                conexao.commit()

                return None
        except Exception as err:
            print(f"Erro ao executar a stored procedure: {err}")

    except Exception as err:
        print(f'Erro ao realizar conexão com o banco de dados: {err}')
    
    finally:
        conexao.close()