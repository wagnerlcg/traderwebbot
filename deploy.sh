#!/bin/bash

# Script de Deploy para Trader Web Bot
# Uso: bash deploy.sh

set -e  # Parar em caso de erro

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    print_error "Por favor, execute como root (sudo bash deploy.sh)"
    exit 1
fi

print_info "Iniciando deploy do Trader Web Bot..."

# Variáveis
APP_DIR="/var/www/trader_bot"
APP_USER="trader"
SERVICE_NAME="trader_bot"

# 1. Criar usuário se não existir
if ! id "$APP_USER" &>/dev/null; then
    print_info "Criando usuário $APP_USER..."
    useradd -m -s /bin/bash $APP_USER
else
    print_info "Usuário $APP_USER já existe."
fi

# 2. Criar diretório da aplicação
print_info "Criando diretório da aplicação..."
mkdir -p $APP_DIR
chown $APP_USER:$APP_USER $APP_DIR

# 3. Copiar arquivos (assumindo que estamos no diretório do projeto)
print_info "Copiando arquivos da aplicação..."
cp -r * $APP_DIR/ 2>/dev/null || true
chown -R $APP_USER:$APP_USER $APP_DIR

# 4. Criar virtual environment
print_info "Criando ambiente virtual Python..."
cd $APP_DIR
sudo -u $APP_USER python3 -m venv .venv
sudo -u $APP_USER .venv/bin/pip install --upgrade pip

# 5. Instalar dependências
print_info "Instalando dependências Python..."
sudo -u $APP_USER .venv/bin/pip install -r requirements.txt

# 6. Configurar .env se não existir
if [ ! -f "$APP_DIR/.env" ]; then
    print_warning "Arquivo .env não encontrado. Criando arquivo de exemplo..."
    sudo -u $APP_USER cat > $APP_DIR/.env << EOF
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=trader
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DATABASE=trader_bot
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
    print_warning "Por favor, edite $APP_DIR/.env com suas configurações!"
fi

# 7. Criar diretórios necessários
print_info "Criando diretórios necessários..."
sudo -u $APP_USER mkdir -p $APP_DIR/logs
sudo -u $APP_USER mkdir -p $APP_DIR/data
sudo -u $APP_USER mkdir -p $APP_DIR/config

# 8. Configurar systemd service
print_info "Configurando serviço systemd..."
cp trader_bot.service /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload

# 9. Configurar Nginx
print_info "Configurando Nginx..."
if [ -f "nginx_config.conf" ]; then
    cp nginx_config.conf /etc/nginx/sites-available/$SERVICE_NAME
    
    # Testar configuração do Nginx
    if nginx -t; then
        ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
        print_info "Configuração do Nginx OK"
    else
        print_error "Erro na configuração do Nginx. Corrija antes de continuar."
        exit 1
    fi
fi

# 10. Habilitar e iniciar serviço
print_info "Iniciando serviço..."
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Aguardar um momento
sleep 2

# Verificar status
if systemctl is-active --quiet $SERVICE_NAME; then
    print_info "Serviço iniciado com sucesso!"
else
    print_error "Falha ao iniciar o serviço. Verifique os logs:"
    print_error "sudo journalctl -u $SERVICE_NAME.service -n 50"
    exit 1
fi

# 11. Recarregar Nginx
print_info "Recarregando Nginx..."
systemctl reload nginx

# 12. Resumo
print_info "Deploy concluído!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Resumo do Deploy:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Diretório: $APP_DIR"
echo "👤 Usuário: $APP_USER"
echo "🔧 Serviço: $SERVICE_NAME"
echo ""
print_info "Comandos úteis:"
echo "  - Ver status: sudo systemctl status $SERVICE_NAME"
echo "  - Ver logs: sudo journalctl -u $SERVICE_NAME.service -f"
echo "  - Reiniciar: sudo systemctl restart $SERVICE_NAME"
echo "  - Parar: sudo systemctl stop $SERVICE_NAME"
echo ""
print_warning "IMPORTANTE:"
echo "  1. Configure o arquivo .env em $APP_DIR/.env"
echo "  2. Configure seu domínio no arquivo do Nginx"
echo "  3. Configure SSL com Let's Encrypt"
echo "  4. Configure o firewall (ufw allow 'Nginx Full')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

