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
                # Compatibilidade de esquemas: tenta 'email' e, se falhar, '`e-mail`'
                try:
                    sql = "SELECT * FROM usuarios WHERE email = %s"
                    cursor.execute(sql, (email,))
                except Exception:
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
            # Regras de acesso compatíveis com diferentes esquemas
            # 1) Se existir coluna 'status', exige status = 'ativo'
            status = usuario.get('status')
            if status is not None and str(status).lower() not in ('ativo', '1', 'true'):
                return None
            # 2) Se existir coluna 'pagou', exige True
            if 'pagou' in usuario and not bool(usuario.get('pagou')):
                return None
            
            # Mapear email conforme coluna existente
            email_val = usuario.get('email') or usuario.get('e-mail')
            
            return {
                'id': usuario.get('id'),
                'email': email_val,
                'nome': usuario.get('nome', ''),
                'celular': usuario.get('celular', ''),
                'pagou': usuario.get('pagou', True) if 'pagou' in usuario else True,
                'data_cadastro': usuario.get('data_cadastro') or usuario.get('criado_em'),
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
                # Atualizar último acesso (compatível com 'email' e '`e-mail`')
                try:
                    sql = "UPDATE usuarios SET ultimo_acesso = %s WHERE email = %s"
                    cursor.execute(sql, (datetime.now(), email))
                except Exception:
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
                # Tentar selecionar com coluna 'email'; se falhar, usar '`e-mail`'
                try:
                    sql = "SELECT id, email, nome, celular, status, is_admin, criado_em AS data_cadastro, ultimo_acesso FROM usuarios ORDER BY criado_em DESC"
                    cursor.execute(sql)
                except Exception:
                    sql = "SELECT id, `e-mail` AS email, nome, celular, pagou AS status, data_cadastro, ultimo_acesso FROM usuarios ORDER BY data_cadastro DESC"
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
                # Cria tabela básica se não existir (versão compatível)
                sql = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    nome VARCHAR(255),
                    celular VARCHAR(30),
                    status ENUM('ativo','inativo') DEFAULT 'ativo',
                    is_admin TINYINT(1) DEFAULT 0,
                    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    ultimo_acesso DATETIME NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
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
                try:
                    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", ('wagnerlcg@gmail.com',))
                except Exception:
                    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE `e-mail` = %s", ('wagnerlcg@gmail.com',))
                if cursor.fetchone()[0] > 0:
                    print("Usuário de exemplo já existe!")
                    return True
                
                # Inserir usuário de exemplo
                try:
                    sql = """
                    INSERT INTO usuarios (email, nome, celular, status, is_admin) 
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, ('wagnerlcg@gmail.com', 'Administrador', '24981148429', 'ativo', 1))
                except Exception:
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
