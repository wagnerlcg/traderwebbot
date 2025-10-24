-- Script para configurar o banco de dados do Trader Bot
-- Execute este script no seu MariaDB/MySQL

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS trader_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Selecionar o banco
USE trader_bot;

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `e-mail` VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255),
    celular VARCHAR(14),
    pagou BOOLEAN DEFAULT TRUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir usuário de exemplo
INSERT IGNORE INTO usuarios (`e-mail`, nome, celular, pagou) 
VALUES ('wagnerlcg@gmail.com', 'Administrador', '24981148429', TRUE);

-- Inserir usuário adicional de exemplo
INSERT IGNORE INTO usuarios (`e-mail`, nome, celular, pagou) 
VALUES ('exemplo@exemplo.com', 'Nome Um', '24981148430', TRUE);

-- Verificar se os usuários foram inseridos
SELECT * FROM usuarios;

-- Mostrar informações do banco
SELECT 
    'Banco de dados criado com sucesso!' as status,
    COUNT(*) as total_usuarios 
FROM usuarios;
