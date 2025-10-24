"""
Configuração do banco de dados MySQL
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseConfig:
    """Configurações do banco de dados MySQL"""
    
    # Configurações do banco de dados
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'trader_bot')
    
    # Configurações de conexão
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_AUTOCOMMIT = True
    
    @classmethod
    def get_connection_string(cls):
        """Retorna string de conexão para PyMySQL"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}?charset={cls.MYSQL_CHARSET}"
    
    @classmethod
    def get_pymysql_config(cls):
        """Retorna configuração para PyMySQL"""
        return {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'user': cls.MYSQL_USER,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DATABASE,
            'charset': cls.MYSQL_CHARSET,
            'autocommit': cls.MYSQL_AUTOCOMMIT
        }
