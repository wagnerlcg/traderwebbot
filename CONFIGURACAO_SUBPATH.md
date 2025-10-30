# Configuração para Acesso via Subpath `/trader_bot`

## Objetivo
Configurar a aplicação para ser acessada via `nomadtradersystem.com/trader_bot` ao invés de ser servida diretamente na raiz.

## Alterações Realizadas

### 1. **Flask (`web_interface.py`)**
- Configurado middleware para capturar `X-Script-Name` do header enviado pelo Nginx
- SocketIO configurado para funcionar com qualquer path base

### 2. **JavaScript (`web/static/js/app.js`)**
- Adicionada detecção automática do path base da aplicação
- Todas as chamadas de API agora usam `${API_BASE}/api/...`
- SocketIO configurado para usar o path base correto: `${basePath}/socket.io`

### 3. **Templates HTML**
- Adicionado script para definir `APP_BASE_PATH` baseado na URL gerada pelo Flask

### 4. **Nginx (`nginx_config.conf`)**
- Configurado `location /trader_bot/` para fazer proxy reverso
- `rewrite` rule para remover `/trader_bot` antes de enviar ao Gunicorn
- Headers `X-Script-Name` configurado para informar o Flask sobre o subpath
- Arquivos estáticos servidos diretamente pelo Nginx

## Instruções para Aplicar no Servidor

### 1. Atualizar arquivo Nginx
```bash
sudo nano /etc/nginx/sites-available/trader_bot
```

Cole o conteúdo do arquivo `nginx_config.conf` atualizado.

### 2. Testar configuração Nginx
```bash
sudo nginx -t
```

### 3. Recarregar Nginx
```bash
sudo systemctl reload nginx
```

### 4. Verificar Gunicorn
```bash
sudo systemctl status trader_bot
```

### 5. Verificar logs
```bash
# Logs do Nginx
sudo tail -f /var/log/nginx/trader_bot_error.log

# Logs do Gunicorn
sudo tail -f /var/www/trader_bot/logs/gunicorn_error.log
```

### 6. Testar acesso
```bash
# Do próprio servidor
curl -I http://localhost/trader_bot/

# Ou acesse no navegador
# http://nomadtradersystem.com/trader_bot
```

## Pontos Importantes

1. **Redirecionamento**: `/trader_bot` (sem barra) redireciona para `/trader_bot/` (com barra)
2. **Arquivos estáticos**: Servidos diretamente pelo Nginx em `/trader_bot/static`
3. **WebSocket**: Funciona automaticamente via `/trader_bot/socket.io`
4. **APIs**: Todas as rotas `/api/*` funcionam com o path base correto

## Troubleshooting

### Se não carregar estáticos:
```bash
# Verificar permissões
sudo chmod -R 755 /var/www/trader_bot/web/static
sudo chmod -R 644 /var/www/trader_bot/web/static/*
```

### Se WebSocket não conectar:
- Verificar logs do Nginx e Gunicorn
- Confirmar que o header `Upgrade` está sendo passado corretamente

### Se APIs retornarem 404:
- Verificar se o `rewrite` no Nginx está removendo `/trader_bot` corretamente
- Verificar logs do Nginx para ver o path que está chegando ao Gunicorn

