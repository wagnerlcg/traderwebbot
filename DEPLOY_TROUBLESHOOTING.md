# Troubleshooting - 503 Service Unavailable com Proxy Reverso

## Problema
- `curl http://localhost` → `302 FOUND` ✅ (funciona)
- `curl http://200.9.22.250` → `503 Service Unavailable` ❌

## Diagnóstico

O IP `200.9.22.250` é um proxy reverso/load balancer na frente da VPS. O Nginx local está funcionando, mas o proxy externo não consegue se conectar.

### Comandos para executar no servidor:

```bash
# 1. Verificar IPs da VPS
ip addr show | grep "inet " | grep -v "127.0.0.1"

# 2. Verificar firewall (ufw)
sudo ufw status verbose

# 3. Verificar iptables (se não usar ufw)
sudo iptables -L -n -v | grep -E "80|443"

# 4. Verificar se Nginx está escutando em todas as interfaces
sudo netstat -tlnp | grep :80

# 5. Testar acesso externo (do próprio servidor)
curl -I http://$(hostname -I | awk '{print $1}')

# 6. Verificar logs do Nginx quando acessa via IP externo
sudo tail -f /var/log/nginx/error.log /var/log/nginx/trader_bot_error.log

# 7. Verificar configuração do Nginx
sudo nginx -T | grep -A 10 "server_name\|listen"

# 8. Verificar se há conflitos de porta
sudo lsof -i :80
```

## Possíveis Soluções

### 1. Firewall Bloqueando Porta 80
```bash
# Se usar ufw:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Se usar iptables:
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables-save
```

### 2. Nginx não está escutando em todas as interfaces
Verificar se `listen 80` está sem especificar interface (deve estar OK)

### 3. Proxy externo precisa de configuração especial
O suporte técnico pode precisar:
- Configurar o proxy para apontar para o IP INTERNO da VPS (não 200.9.22.250)
- Configurar headers especiais para proxy reverso

### 4. Verificar IP interno da VPS
O proxy reverso precisa apontar para o IP real da VPS, não para 200.9.22.250.

