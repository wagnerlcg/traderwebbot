"""
Configuração específica para MariaDB
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MariaDBConfig:
    """Configurações específicas para MariaDB"""
    
    # Configurações do banco de dados MariaDB
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'trader_bot')
    
    # Configurações específicas do MariaDB
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_AUTOCOMMIT = True
    MYSQL_SSL_DISABLED = True  # Para MariaDB local sem SSL
    
    @classmethod
    def get_connection_string(cls):
        """Retorna string de conexão para PyMySQL com MariaDB"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}?charset={cls.MYSQL_CHARSET}&ssl_disabled=true"
    
    @classmethod
    def get_pymysql_config(cls):
        """Retorna configuração para PyMySQL com MariaDB"""
        return {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'user': cls.MYSQL_USER,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DATABASE,
            'charset': cls.MYSQL_CHARSET,
            'autocommit': cls.MYSQL_AUTOCOMMIT,
            'ssl_disabled': cls.MYSQL_SSL_DISABLED
        }
    
    @classmethod
    def test_connection(cls):
        """Testa conexão com MariaDB"""
        try:
            import pymysql
            config = cls.get_pymysql_config()
            connection = pymysql.connect(**config)
            connection.close()
            return True, "Conexão com MariaDB bem-sucedida!"
        except Exception as e:
            return False, f"Erro ao conectar com MariaDB: {e}"
