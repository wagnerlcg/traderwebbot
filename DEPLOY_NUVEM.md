# Guia de Deploy em Servidor na Nuvem

## Pré-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Python 3.12 ou superior
- MySQL/MariaDB instalado e configurado
- Nginx instalado
- Usuário com privilégios sudo

## Passo 1: Preparar o Servidor

### 1.1. Atualizar o sistema
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2. Instalar dependências
```bash
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server
```

### 1.3. Criar usuário para a aplicação
```bash
sudo useradd -m -s /bin/bash trader
sudo usermod -aG sudo trader
```

### 1.4. Configurar MySQL
```bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

No MySQL:
```sql
CREATE DATABASE trader_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trader'@'localhost' IDENTIFIED BY 'sua_senha_aqui';
GRANT ALL PRIVILEGES ON trader_bot.* TO 'trader'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Passo 2: Deploy da Aplicação

### 2.1. Conectar ao servidor e clonar repositório
```bash
# No seu computador local
scp -r traderwebbot user@seu-servidor:/tmp/

# Ou se já estiver no servidor
git clone https://github.com/seu-usuario/traderwebbot.git /var/www/trader_bot
```

### 2.2. Mover arquivos para local apropriado
```bash
sudo mkdir -p /var/www/trader_bot
sudo cp -r /tmp/traderwebbot/* /var/www/trader_bot/
sudo chown -R trader:trader /var/www/trader_bot
```

### 2.3. Configurar ambiente virtual
```bash
cd /var/www/trader_bot
sudo -u trader python3 -m venv .venv
sudo -u trader .venv/bin/pip install --upgrade pip
sudo -u trader .venv/bin/pip install -r requirements.txt
```

### 2.4. Configurar variáveis de ambiente
```bash
sudo -u trader nano /var/www/trader_bot/.env
```

Adicionar:
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=trader
MYSQL_PASSWORD=sua_senha_mysql
MYSQL_DATABASE=trader_bot
SECRET_KEY=gerar_uma_chave_secreta_aqui
FLASK_ENV=production
```

## Passo 3: Configurar Gunicorn

### 3.1. Copiar arquivo de configuração
O arquivo `gunicorn_config.py` já está no repositório.

### 3.2. Testar manualmente
```bash
cd /var/www/trader_bot
sudo -u trader .venv/bin/gunicorn -c gunicorn_config.py web_interface:app
```

Se funcionar, pare com Ctrl+C.

## Passo 4: Configurar Systemd

### 4.1. Copiar arquivo de serviço
```bash
sudo cp trader_bot.service /etc/systemd/system/
```

### 4.2. Ajustar o arquivo de serviço (se necessário)
```bash
sudo nano /etc/systemd/system/trader_bot.service
```

Verificar se os caminhos estão corretos.

### 4.3. Habilitar e iniciar serviço
```bash
sudo systemctl daemon-reload
sudo systemctl enable trader_bot.service
sudo systemctl start trader_bot.service
sudo systemctl status trader_bot.service
```

## Passo 5: Configurar Nginx

### 5.1. Copiar configuração
```bash
sudo cp nginx_config.conf /etc/nginx/sites-available/trader_bot
```

### 5.2. Editar configuração
```bash
sudo nano /etc/nginx/sites-available/trader_bot
```

Alterar:
- `seudominio.com` para seu domínio real
- Ajustar caminhos se necessário

### 5.3. Habilitar site
```bash
sudo ln -s /etc/nginx/sites-available/trader_bot /etc/nginx/sites-enabled/
sudo nginx -t  # Testar configuração
sudo systemctl reload nginx
```

## Passo 6: Configurar SSL (HTTPS) - Recomendado

### 6.1. Instalar Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2. Obter certificado
```bash
sudo certbot --nginx -d seu-dominio.com
```

### 6.3. Renovação automática
O Certbot já configura a renovação automática.

## Passo 7: Firewall

### 7.1. Configurar UFW
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

## Passo 8: Verificação

### 8.1. Verificar logs
```bash
# Logs da aplicação
sudo journalctl -u trader_bot.service -f

# Logs do Gunicorn
tail -f /var/www/trader_bot/logs/gunicorn_error.log

# Logs do Nginx
sudo tail -f /var/log/nginx/trader_bot_error.log
```

### 8.2. Testar conexão
```bash
curl http://localhost:5000  # Deve funcionar
curl http://seu-servidor.com  # Deve funcionar via Nginx
```

### 8.3. Acessar no navegador
Abrir: `http://seu-dominio.com` ou `https://seu-dominio.com`

## Comandos Úteis

### Reiniciar aplicação
```bash
sudo systemctl restart trader_bot.service
```

### Ver status
```bash
sudo systemctl status trader_bot.service
```

### Ver logs em tempo real
```bash
sudo journalctl -u trader_bot.service -f
```

### Atualizar aplicação
```bash
cd /var/www/trader_bot
sudo -u trader git pull  # Se usando git
sudo -u trader .venv/bin/pip install -r requirements.txt
sudo systemctl restart trader_bot.service
```

### Backup
```bash
# Backup do banco de dados
mysqldump -u trader -p trader_bot > backup_$(date +%Y%m%d).sql

# Backup da aplicação
tar -czf trader_bot_backup_$(date +%Y%m%d).tar.gz /var/www/trader_bot/
```

## Troubleshooting

### Aplicação não inicia
```bash
sudo journalctl -u trader_bot.service --no-pager
# Verificar erros específicos
```

### Erro de permissão
```bash
sudo chown -R trader:trader /var/www/trader_bot
sudo chmod -R 755 /var/www/trader_bot
```

### Erro de porta já em uso
```bash
sudo netstat -tlnp | grep 5000
sudo kill -9 PID_DO_PROCESSO
```

### Nginx retorna 502 Bad Gateway
- Verificar se o serviço está rodando: `sudo systemctl status trader_bot.service`
- Verificar logs: `tail -f /var/log/nginx/trader_bot_error.log`
- Verificar se o Gunicorn está escutando na porta correta

## Manutenção

### Atualizações de segurança
```bash
sudo apt update && sudo apt upgrade -y
sudo -u trader .venv/bin/pip install --upgrade -r requirements.txt
```

### Monitoramento de recursos
```bash
htop  # CPU e memória
df -h  # Espaço em disco
mysqladmin processlist  # Conexões MySQL
```

## Segurança Adicional

1. **Fail2Ban**: Proteger contra brute force
   ```bash
   sudo apt install fail2ban
   ```

2. **Firewall**: Configurar regras restritivas

3. **SSL/TLS**: SEMPRE usar HTTPS em produção

4. **Backups**: Automatizar backups do banco de dados

5. **Logs**: Monitorar logs regularmente

## Suporte

Para problemas específicos, consulte:
- Logs da aplicação: `/var/www/trader_bot/logs/`
- Logs do sistema: `sudo journalctl -u trader_bot.service`
- Logs do Nginx: `/var/log/nginx/`

