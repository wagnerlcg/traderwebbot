#!/bin/bash
# Script para criar os arquivos de deploy diretamente no servidor
# Execute: bash criar_deploy_no_servidor.sh

cat > /var/www/traderwebbot/deploy.sh << 'DEPLOY_END'
#!/bin/bash

# Script de Deploy para Trader Web Bot
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERRO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[AVISO]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then 
    print_error "Execute como root (sudo bash deploy.sh)"; exit 1
fi

print_info "Iniciando deploy..."

APP_DIR="/var/www/trader_bot"
APP_USER="trader"

# Criar usuário
if ! id "$APP_USER" &>/dev/null; then
    print_info "Criando usuário $APP_USER..."
    useradd -m -s /bin/bash $APP_USER
fi

# Criar diretório
mkdir -p $APP_DIR
chown $APP_USER:$APP_USER $APP_DIR

# Copiar arquivos
print_info "Copiando arquivos..."
cp -r /var/www/traderwebbot/* $APP_DIR/ 2>/dev/null || true
rm -rf $APP_DIR/deploy.sh
chown -R $APP_USER:$APP_USER $APP_DIR

# Criar venv
print_info "Criando ambiente virtual..."
cd $APP_DIR
sudo -u $APP_USER python3 -m venv .venv
sudo -u $APP_USER .venv/bin/pip install --upgrade pip
sudo -u $APP_USER .venv/bin/pip install -r requirements.txt

# Configurar .env
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u $APP_USER cat > $APP_DIR/.env << 'EOF'
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=trader
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DATABASE=trader_bot
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
    print_warning "Edite $APP_DIR/.env"
fi

# Criar diretórios
sudo -u $APP_USER mkdir -p $APP_DIR/logs $APP_DIR/data $APP_DIR/config

# Configurar systemd
cat > /etc/systemd/system/trader_bot.service << 'SERVICE_END'
[Unit]
Description=Trader Web Bot
After=network.target mysql.service

[Service]
Type=notify
User=trader
Group=trader
WorkingDirectory=/var/www/trader_bot
Environment="PATH=/var/www/trader_bot/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/var/www/trader_bot/.venv/bin/gunicorn -c gunicorn_config.py web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
SERVICE_END

systemctl daemon-reload
systemctl enable trader_bot

# Configurar Nginx
cat > /etc/nginx/sites-available/trader_bot << 'NGINX_END'
upstream trader_bot {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 10M;
    
    access_log /var/log/nginx/trader_bot_access.log;
    error_log /var/log/nginx/trader_bot_error.log;

    location / {
        proxy_pass http://trader_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /static {
        alias /var/www/trader_bot/web/static;
        expires 1y;
        add_header Cache-Control "Closed, immutable";
    }
}
NGINX_END

ln -sf /etc/nginx/sites-available/trader_bot /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Iniciar serviço
systemctl restart trader_bot
sleep 2

if systemctl is-active --quiet trader_bot; then
    print_info "Deploy concluído!"
    echo ""
    echo "Comandos:"
    echo "  Status: systemctl status trader_bot"
    echo "  Logs: journalctl -u trader_bot -f"
    echo "  Editar .env: nano /var/www/trader_bot/.env"
else
    print_error "Falha ao iniciar. Ver logs: journalctl -u trader_bot -n 50"
fi
DEPLOY_END

chmod +x /var/www/traderwebbot/deploy.sh
print_info "Arquivo deploy.sh criado em /var/www/traderwebbot/"

