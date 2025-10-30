# Quick Deploy - Guia Rápido

## Para Deploy em Servidor Ubuntu/Debian

### Opção 1: Deploy Manual (Recomendado para primeira vez)

```bash
# 1. Conectar ao servidor
ssh user@seu-servidor

# 2. Clonar ou fazer upload dos arquivos
git clone https://github.com/seu-usuario/traderwebbot.git
# OU fazer upload via SCP/SFTP

# 3. Entrar no diretório
cd traderwebbot

# 4. Executar o script de deploy
sudo bash deploy.sh

# 5. Configurar .env
sudo nano /var/www/trader_bot/.env
# Editar as credenciais do banco de dados

# 6. Iniciar o banco de dados
sudo mysql -u root -p < database/init.sql  # Se houver

# 7. Testar
curl http://localhost:5000
```

### Opção 2: Deploy com Script Automatizado

```bash
# No servidor:
sudo apt update && sudo apt install -y git
git clone https://github.com/seu-usuario/traderwebbot.git
cd traderwebbot
sudo bash deploy.sh
```

## Configuração do Nginx

### 1. Editar arquivo de configuração
```bash
sudo nano /etc/nginx/sites-available/trader_bot
```

### 2. Alterar domínio
```nginx
server_name seu-dominio.com;  # Linha 8
```

### 3. Testar e recarregar
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Configurar SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Testar renovação
sudo certbot renew --dry-run
```

## Comandos Principais

```bash
# Ver status
sudo systemctl status trader_bot

# Ver logs
sudo journalctl -u trader_bot -f

# Reiniciar
sudo systemctl restart trader_bot

# Parar
sudo systemctl stop trader_bot

# Habilitar no boot
sudo systemctl enable trader_bot
```

## Solução de Problemas

### Serviço não inicia
```bash
sudo journalctl -u trader_bot.service --no-pager
```

### Porta em uso
```bash
sudo netstat -tlnp | grep 5000
```

### Erro 502 no Nginx
- Verificar se o serviço está rodando
- Verificar logs do Nginx: `sudo tail -f /var/log/nginx/trader_bot_error.log`
- Verificar se o Gunicorn está na porta correta

## Checklist Pós-Deploy

- [ ] Serviço está rodando: `sudo systemctl status trader_bot`
- [ ] Logs sem erros: `sudo journalctl -u trader_bot -n 50`
- [ ] Nginx respondendo: `curl http://seu-dominio.com`
- [ ] SSL configurado: `https://seu-dominio.com`
- [ ] Firewall configurado: `sudo ufw status`
- [ ] Backups configurados
- [ ] Monitoramento configurado

