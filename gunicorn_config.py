# Configuração do Gunicorn
# Uso: gunicorn -c gunicorn_config.py web_interface:app

# Endereço e porta onde o Gunicorn vai ouvir
bind = "127.0.0.1:5000"

# Número de workers (processos)
# Fórmula recomendada: (2 x cores) + 1
workers = 4

# Tipo de worker
worker_class = "gevent"  # Compatível com Flask-SocketIO

# Timeout
timeout = 60
keepalive = 5

# Logs
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Preload da aplicação para melhor performance
preload_app = True

# Process name
proc_name = "trader_bot"

# User e group (opcional - configure conforme seu servidor)
# user = "trader"
# group = "trader"

