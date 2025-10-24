"""
Sistema de autenticação com MySQL
"""
import pymysql
from config.mariadb_config import MariaDBConfig
import hashlib
import secrets
from datetime import datetime, timedelta

class MySQLAuth:
    """Sistema de autenticação usando MySQL"""
    
    def __init__(self):
        self.config = MariaDBConfig.get_pymysql_config()
    
    def get_connection(self):
        """Cria conexão com o banco de dados"""
        try:
            connection = pymysql.connect(**self.config)
            return connection
        except Exception as e:
            print(f"Erro ao conectar com MySQL: {e}")
            return None
    
    def verificar_usuario(self, email):
        """
        Verifica se o usuário existe na tabela usuarios
        
        Args:
            email: E-mail do usuário
            
        Returns:
            dict: Dados do usuário se encontrado, None caso contrário
        """
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Consultar usuário pelo campo e-mail
                sql = "SELECT * FROM usuarios WHERE `e-mail` = %s"
                cursor.execute(sql, (email,))
                usuario = cursor.fetchone()
                
                return usuario
                
        except Exception as e:
            print(f"Erro ao verificar usuário: {e}")
            return None
        finally:
            connection.close()
    
    def autenticar_usuario(self, email):
        """
        Autentica um usuário verificando se existe na base de dados
        
        Args:
            email: E-mail do usuário
            
        Returns:
            dict: Dados do usuário se autenticado, None caso contrário
        """
        usuario = self.verificar_usuario(email)
        
        if usuario:
            # Verificar se o usuário pagou
            if not usuario.get('pagou', False):
                return None  # Usuário não pagou
            
            # Usuário encontrado e pagou - autenticação bem-sucedida
            return {
                'id': usuario.get('id'),
                'email': usuario.get('e-mail'),
                'nome': usuario.get('nome', ''),
                'celular': usuario.get('celular', ''),
                'pagou': usuario.get('pagou', False),
                'data_cadastro': usuario.get('data_cadastro'),
                'ultimo_acesso': datetime.now()
            }
        
        return None
    
    def registrar_acesso(self, email):
        """
        Registra o último acesso do usuário
        
        Args:
            email: E-mail do usuário
        """
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            with connection.cursor() as cursor:
                # Atualizar último acesso
                sql = "UPDATE usuarios SET ultimo_acesso = %s WHERE `e-mail` = %s"
                cursor.execute(sql, (datetime.now(), email))
                connection.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao registrar acesso: {e}")
            return False
        finally:
            connection.close()
    
    def listar_usuarios(self):
        """
        Lista todos os usuários cadastrados (para administração)
        
        Returns:
            list: Lista de usuários
        """
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT id, `e-mail`, nome, celular, pagou, data_cadastro, ultimo_acesso FROM usuarios ORDER BY data_cadastro DESC"
                cursor.execute(sql)
                usuarios = cursor.fetchall()
                
                return usuarios
                
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
        finally:
            connection.close()
    
    def criar_tabela_usuarios(self):
        """
        Cria a tabela usuarios se não existir
        
        Returns:
            bool: True se criada com sucesso
        """
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            with connection.cursor() as cursor:
                # SQL para criar tabela usuarios
                sql = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    `e-mail` VARCHAR(255) UNIQUE NOT NULL,
                    nome VARCHAR(255),
                    celular VARCHAR(14),
                    pagou BOOLEAN DEFAULT TRUE,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_acesso TIMESTAMP NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(sql)
                connection.commit()
                
                print("Tabela 'usuarios' criada/verificada com sucesso!")
                return True
                
        except Exception as e:
            print(f"Erro ao criar tabela usuarios: {e}")
            return False
        finally:
            connection.close()
    
    def inserir_usuario_exemplo(self):
        """
        Insere um usuário de exemplo para teste
        
        Returns:
            bool: True se inserido com sucesso
        """
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            with connection.cursor() as cursor:
                # Verificar se já existe
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE `e-mail` = %s", ('wagnerlcg@gmail.com',))
                if cursor.fetchone()[0] > 0:
                    print("Usuário de exemplo já existe!")
                    return True
                
                # Inserir usuário de exemplo
                sql = """
                INSERT INTO usuarios (`e-mail`, nome, celular, pagou) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, ('wagnerlcg@gmail.com', 'Administrador', '24981148429', True))
                connection.commit()
                
                print("Usuário de exemplo criado: wagnerlcg@gmail.com")
                return True
                
        except Exception as e:
            print(f"Erro ao inserir usuário de exemplo: {e}")
            return False
        finally:
            connection.close()
