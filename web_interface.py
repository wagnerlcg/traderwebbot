"""
Interface Web para Trader Bot - Sinais
Servidor Flask com WebSockets para controle em tempo real
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import threading
import os
import json
import time
from datetime import datetime
import asyncio
from bot.iqoption_bot import executar_real, executar_demo
from bot.utils import setup_logger, carregar_sinais
from auth.mysql_auth import MySQLAuth

app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')
app.config['SECRET_KEY'] = 'trader-bot-secret-key-2024'

# Configurar para funcionar com subpath /trader_bot
# Isso permite que a aplicação funcione em nomadtradersystem.com/trader_bot
import os
# Em ambiente local, não usar prefixo por padrão para evitar 404 em /trader_bot/static
SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
# Configurar APPLICATION_ROOT do Flask (usado pelo url_for)
app.config['APPLICATION_ROOT'] = SCRIPT_NAME

# Configurar SocketIO com threading para compatibilidade e path correto
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, async_mode='threading')

# Middleware para definir APPLICATION_ROOT dinamicamente baseado no header
@app.before_request
def set_application_root():
    """Define APPLICATION_ROOT baseado no header X-Script-Name do Nginx"""
    script_name = request.headers.get('X-Script-Name', '')
    if script_name:
        app.config['APPLICATION_ROOT'] = script_name
        # Definir SCRIPT_NAME no ambiente WSGI para url_for funcionar
        request.environ['SCRIPT_NAME'] = script_name
    else:
        # Fallback para variável de ambiente
        app.config['APPLICATION_ROOT'] = SCRIPT_NAME
        if SCRIPT_NAME:
            request.environ['SCRIPT_NAME'] = SCRIPT_NAME

# Filtro customizado para adicionar APPLICATION_ROOT às URLs
@app.template_filter('prefix_url')
def prefix_url(url):
    """Adiciona APPLICATION_ROOT ao início de uma URL se necessário"""
    if not url:
        return url
    app_root = app.config.get('APPLICATION_ROOT', '')
    if app_root and app_root != '/' and not url.startswith(app_root):
        if app_root.endswith('/'):
            app_root = app_root.rstrip('/')
        if not url.startswith('/'):
            url = '/' + url
        return app_root + url
    return url

# Context processor para templates - injeta APPLICATION_ROOT
@app.context_processor
def inject_globals():
    """Injeta variáveis globais nos templates"""
    return dict(
        APPLICATION_ROOT=app.config.get('APPLICATION_ROOT', '')
    )

# Estado global do bot
bot_state = {
    'running': False,
    'mode': None,
    'saldo_inicial': 0,
    'saldo_atual': 0,
    'sinais_executados': 0,
    'sinais_totais': 0,
    'wins': 0,
    'losses': 0,
    'lucro_total': 0,
    'logs': [],
    'sinais': [],
    'configuracoes': {
        'stop_loss': 10,
        'stop_win': 20,
        'estrategia': 'Martingale',
        'valor_entrada_tipo': 'fixo',
        'valor_entrada': 10.0,
        'sons_habilitados': True
    }
}

# Thread do bot
bot_thread = None
stop_bot_flag = False

# Sistema de autenticação
auth_system = MySQLAuth()

def url_for_with_prefix(endpoint, **values):
    """Wrapper para url_for que sempre inclui o APPLICATION_ROOT"""
    try:
        # Obter o APPLICATION_ROOT atual (pode mudar por request)
        app_root = app.config.get('APPLICATION_ROOT', SCRIPT_NAME)
        # Usar url_for normal e adicionar o prefixo se necessário
        url = url_for(endpoint, **values, _external=False)
        if app_root and app_root != '/' and not url.startswith(app_root):
            # Garantir que o app_root tenha barra inicial e url não tenha duplicação
            if app_root.endswith('/'):
                app_root = app_root.rstrip('/')
            if not url.startswith('/'):
                url = '/' + url
            url = app_root + url
        return url
    except RuntimeError:
        # Se não estiver em contexto de request, usar url_for normal
        return url_for(endpoint, **values, _external=False)

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for_with_prefix('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def init_database():
    """Inicializa o banco de dados e cria tabelas se necessário"""
    try:
        # Criar tabela usuarios
        auth_system.criar_tabela_usuarios()
        
        # Inserir usuário de exemplo se não existir
        auth_system.inserir_usuario_exemplo()
        
        print("[OK] Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao inicializar banco de dados: {e}")
        return False

def logger_callback(message):
    """Callback para capturar logs e enviar via WebSocket"""
    # Filtrar mensagens técnicas que não devem aparecer para o usuário
    if should_filter_message(message):
        return
    
    # Converter mensagem técnica em mensagem amigável
    friendly_message = create_friendly_message(message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': friendly_message
    }
    bot_state['logs'].append(log_entry)
    
    # Manter apenas os últimos 100 logs
    if len(bot_state['logs']) > 100:
        bot_state['logs'] = bot_state['logs'][-100:]
    
    # Enviar para todos os clientes conectados
    socketio.emit('log_update', log_entry)

def should_filter_message(message):
    """Determina se uma mensagem deve ser filtrada (não mostrada ao usuário)"""
    message_lower = message.lower()
    
    # SIMPLIFICADO: Mostrar TODAS as mensagens importantes
    return False  # Não filtrar nenhuma mensagem

def create_friendly_message_old(original_message):
    """Código antigo - não usado mais"""
    # Filtrar mensagens técnicas específicas
    technical_patterns = [
        'saldo antes:',
        'saldo atual:',
        'ordem put executada:',
        'ordem call executada:',
        'executando put em',
        'executando call em',
        'compra rejeitada pela corretora:',
        'ativo rejeitado:',
        'erro tecnico',
        'operacao nao executada',
        'nao conta como loss',
        'cannot purchase an option',
        'active is suspended',
        '>>>',
        '[!]',
        'max:',
        'margem:',
        'saldo:',
        'entrada:',
        'protecao 1:',
        'protecao 2:',
        'false,',
        'true,',
        'gbpusd',
        'eurusd',
        'audcad',
        'nzdusd',
        'usdchf',
        'gbpjp',
        'euraud',
        'gbpaud',
        'por 5 min',
        'por 1 min',
        'por 15 min',
        'por 30 min',
        'minuto(s)',
        'minutos',
        'minuto',
        'min',
        'otc',
        'atual: $',
        'antes: $',
        'definido: $',
        'atualizado: $'
    ]
    
    # Verificar se a mensagem contém algum padrão técnico
    for pattern in technical_patterns:
        if pattern in message_lower:
            return True
    
    # Filtrar mensagens que começam com caracteres técnicos (exceto mensagens amigáveis)
    if message.startswith(('>>>', '[!]')):
        return True
    
    # Filtrar mensagens que começam com 💰 ou 📊 apenas se contêm informações técnicas
    if message.startswith(('💰', '📊')):
        # Permitir mensagens amigáveis que começam com esses emojis
        if any(termo in message_lower for termo in ['detectado', 'iniciado', 'conectado', 'vencedora', 'perdedora']):
            return False
        return True
    
    # Filtrar mensagens muito longas (provavelmente técnicas)
    if len(message) > 200:
        return True
    
    return False

def create_friendly_message(original_message):
    """Converte mensagens técnicas em mensagens amigáveis para o usuário"""
    message_lower = original_message.lower()
    
    # Mensagens de sinal encontrado
    if 'sinal encontrado:' in message_lower:
        if 'put' in message_lower:
            return "📉 Sinal de VENDA detectado"
        elif 'call' in message_lower:
            return "📈 Sinal de COMPRA detectado"
        else:
            return "📊 Sinal detectado"
    
    # Mensagens de erro de ativo
    if 'cannot purchase an option' in message_lower or 'active is suspended' in message_lower:
        return "⚠️ Ativo temporariamente indisponível"
    
    # Mensagens de erro técnico
    if 'erro tecnico' in message_lower:
        return "⚠️ Problema técnico detectado (não afeta o resultado)"
    
    # Mensagens de operação rejeitada
    if 'compra rejeitada' in message_lower:
        return "❌ Operação rejeitada pela corretora"
    
    # Mensagens de ativo não disponível
    if 'não disponível no momento' in message_lower:
        return "⚠️ Ativo não disponível no momento"
    
    # Mensagens de saldo
    if 'saldo inicial definido:' in message_lower:
        return "💰 Saldo inicial configurado"
    
    if 'saldo atualizado:' in message_lower:
        return "💰 Saldo atualizado"
    
    # Mensagens de início/fim
    if 'iniciando bot' in message_lower:
        return "🚀 Bot iniciado com sucesso"
    
    if 'bot encerrado' in message_lower:
        return "⏹️ Bot encerrado"
    
    # Mensagens de conexão
    if 'conectando' in message_lower:
        return "🔗 Conectando à IQ Option..."
    
    if 'conectado' in message_lower:
        return "✅ Conectado com sucesso"
    
    # Mensagens de operação executada
    if 'operacao executada' in message_lower or 'operação executada' in message_lower:
        return "✅ Operação executada"
    
    # Mensagens de resultado
    if 'resultado:' in message_lower:
        if 'win' in message_lower or 'ganhou' in message_lower:
            return "🎉 Operação vencedora!"
        elif 'loss' in message_lower or 'perdeu' in message_lower:
            return "😔 Operação perdedora"
        else:
            return "📊 Resultado da operação"
    
    # Se não conseguir converter, retornar a mensagem original
    return original_message

def status_callback(status_update):
    """Callback para atualizar status do bot"""
    bot_state.update(status_update)
    socketio.emit('status_update', bot_state)

def update_balance_callback(saldo_atual, is_initial=False):
    """Callback para atualizar saldo atual"""
    # Atualizar estado do bot
    if is_initial or bot_state['saldo_inicial'] == 0:
        bot_state['saldo_inicial'] = saldo_atual
        logger_callback(f"Saldo inicial definido: ${saldo_atual:.2f}")
    
    bot_state['saldo_atual'] = saldo_atual
    logger_callback(f"Saldo atualizado: ${saldo_atual:.2f}")
    
    # Emitir atualização via WebSocket
    try:
        socketio.emit('status_update', bot_state)
        print(f"[WEB] Saldo: ${saldo_atual:.2f} | WS: OK")
    except Exception as e:
        print(f"[WEB] Saldo: ${saldo_atual:.2f} | WS: ERRO - {e}")

def update_stats_callback(stats_update):
    """Callback para atualizar estatísticas do bot"""
    # Atualizar estatísticas
    if 'sinais_executados' in stats_update:
        bot_state['sinais_executados'] = stats_update['sinais_executados']
    if 'sinais_totais' in stats_update:
        bot_state['sinais_totais'] = stats_update['sinais_totais']
    if 'wins' in stats_update:
        bot_state['wins'] = stats_update['wins']
    if 'losses' in stats_update:
        bot_state['losses'] = stats_update['losses']
    if 'lucro_total' in stats_update:
        bot_state['lucro_total'] = stats_update['lucro_total']
    
    # Emitir atualização via WebSocket
    try:
        socketio.emit('status_update', bot_state)
        sinais_info = f"{stats_update.get('sinais_executados', 0)}/{stats_update.get('sinais_totais', 0)}"
        wins_losses = f"W:{stats_update.get('wins', 0)} L:{stats_update.get('losses', 0)}"
        print(f"[WEB] Stats: {sinais_info} | {wins_losses} | WS: OK")
    except Exception as e:
        print(f"[WEB] Stats: ERRO | WS: ERRO - {e}")

def run_bot_async(mode, arquivo_sinais, email, senha, config):
    """Executa o bot em modo assíncrono"""
    global stop_bot_flag
    stop_bot_flag = False
    
    # Criar diretório de logs se não existir
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Setup logger com callback para web interface
    logger = setup_logger("bot_web", "logs/bot_web.log", callback=logger_callback)
    
    # Criar novo loop de eventos para esta thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        bot_state['running'] = True
        bot_state['mode'] = mode
        
        logger_callback(f"Iniciando bot em modo {mode.upper()}...")
        
        # Criar wrapper para capturar saldo inicial e verificar parada
        async def run_with_balance_update():
            if mode == 'demo':
                await executar_demo(
                    arquivo_sinais, 
                    logger, 
                    email, 
                    senha, 
                    config.get('stop_loss', 10),
                    config.get('sons_habilitados', True),
                    balance_callback=update_balance_callback,
                    stats_callback=update_stats_callback,
                    stop_callback=lambda: stop_bot_flag,
                    web_config=config  # Passar todas as configurações
                )
            else:
                await executar_real(
                    arquivo_sinais, 
                    logger, 
                    email, 
                    senha, 
                    config.get('stop_loss', 10),
                    config.get('sons_habilitados', True),
                    balance_callback=update_balance_callback,
                    stats_callback=update_stats_callback,
                    stop_callback=lambda: stop_bot_flag,
                    web_config=config  # Passar todas as configurações
                )
        
        loop.run_until_complete(run_with_balance_update())
        
        # Bot terminou normalmente
        logger_callback("Bot encerrado normalmente.")
        
    except Exception as e:
        error_msg = str(e)
        logger_callback(f"Erro ao executar bot: {error_msg}")
        
        # Tratamento específico para erros de conexão
        if "Connection is already closed" in error_msg or "connection" in error_msg.lower():
            logger_callback("⚠️ Erro de conexão detectado. Aguarde 2-3 minutos antes de tentar novamente.")
        elif "authentication" in error_msg.lower() or "credenciais" in error_msg.lower() or "login" in error_msg.lower():
            logger_callback("⚠️ Erro de autenticação. Verifique email e senha.")
        elif "timeout" in error_msg.lower():
            logger_callback("⚠️ Timeout de conexão. Verifique sua internet.")
        elif "balance" in error_msg.lower() or "saldo" in error_msg.lower():
            logger_callback("⚠️ Erro de saldo. Verifique sua conta.")
        else:
            logger_callback(f"⚠️ Erro inesperado: {error_msg}")
            
    finally:
        bot_state['running'] = False
        stop_bot_flag = False  # Resetar flag de parada
        logger_callback("Bot parado completamente.")
        
        # Emitir evento para atualizar a interface
        socketio.emit('bot_stopped', {})
        
        try:
            loop.close()
        except:
            pass

@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Por favor, informe seu e-mail.', 'error')
            return render_template('login.html')
        
        # Verificar se o usuário existe no banco
        usuario = auth_system.autenticar_usuario(email)
        
        if usuario:
            # Login bem-sucedido
            session['user_email'] = email
            session['user_name'] = usuario.get('nome', '')
            session['user_id'] = usuario.get('id')
            session['user_celular'] = usuario.get('celular', '')
            
            # Registrar último acesso
            auth_system.registrar_acesso(email)
            
            flash(f'Bem-vindo, {usuario.get("nome", email)}!', 'success')
            return redirect(url_for_with_prefix('index'))
        else:
            flash('E-mail não encontrado ou usuário não possui acesso. Verifique se você está cadastrado e pagou.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for_with_prefix('login'))

@app.route('/api/status')
@login_required
def get_status():
    """Retorna status atual do bot"""
    global bot_thread
    
    # Verificar se a thread realmente está rodando
    if bot_state['running'] and bot_thread and not bot_thread.is_alive():
        # Thread morreu mas o estado não foi atualizado
        bot_state['running'] = False
        stop_bot_flag = False
        logger_callback("⚠️ Bot parou inesperadamente")
        socketio.emit('bot_stopped', {})
    
    return jsonify(bot_state)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config():
    """Gerencia configurações do bot"""
    if request.method == 'POST':
        data = request.json
        bot_state['configuracoes'].update(data)
        return jsonify({'success': True, 'config': bot_state['configuracoes']})
    return jsonify(bot_state['configuracoes'])

@app.route('/api/sinais', methods=['GET', 'POST'])
@login_required
def sinais():
    """Gerencia arquivo de sinais"""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.txt'):
                filepath = os.path.join('data', 'sinais.txt')
                file.save(filepath)
                
                # Carregar e validar sinais
                try:
                    sinais_carregados = carregar_sinais(filepath)
                    bot_state['sinais'] = sinais_carregados
                    bot_state['sinais_totais'] = len(sinais_carregados)
                    return jsonify({
                        'success': True, 
                        'sinais': sinais_carregados,
                        'total': len(sinais_carregados)
                    })
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)}), 400
        
        # Receber sinais como texto
        elif 'content' in request.json:
            content = request.json['content']
            filepath = os.path.join('data', 'sinais.txt')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            try:
                sinais_carregados = carregar_sinais(filepath)
                bot_state['sinais'] = sinais_carregados
                bot_state['sinais_totais'] = len(sinais_carregados)
                return jsonify({
                    'success': True, 
                    'sinais': sinais_carregados,
                    'total': len(sinais_carregados)
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
    
    return jsonify({
        'sinais': bot_state['sinais'],
        'total': bot_state['sinais_totais']
    })

@app.route('/api/start', methods=['POST'])
@login_required
def start_bot():
    """Inicia o bot"""
    global bot_thread
    
    # Verificar se há uma thread anterior ainda rodando
    if bot_thread and bot_thread.is_alive():
        return jsonify({'success': False, 'error': 'Bot já está rodando'}), 400
    
    if bot_state['running']:
        return jsonify({'success': False, 'error': 'Bot já está rodando'}), 400
    
    data = request.json
    mode = data.get('mode', 'demo')
    email = data.get('email')
    senha = data.get('senha')
    
    if not email or not senha:
        return jsonify({'success': False, 'error': 'Email e senha são obrigatórios'}), 400
    
    # Verificar se há arquivo de sinais
    arquivo_sinais = os.path.join('data', 'sinais.txt')
    if not os.path.exists(arquivo_sinais):
        return jsonify({'success': False, 'error': 'Nenhum arquivo de sinais carregado'}), 400
    
    # Resetar flags e estado
    stop_bot_flag = False
    bot_state['running'] = True
    bot_state['mode'] = mode
    
    # Resetar estatísticas
    bot_state['sinais_executados'] = 0
    bot_state['wins'] = 0
    bot_state['losses'] = 0
    bot_state['lucro_total'] = 0
    bot_state['logs'] = []
    
    # Iniciar bot em thread separada
    bot_thread = threading.Thread(
        target=run_bot_async,
        args=(mode, arquivo_sinais, email, senha, bot_state['configuracoes']),
        daemon=True
    )
    bot_thread.start()
    
    return jsonify({'success': True, 'message': f'Bot iniciado em modo {mode}'})

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_bot():
    """Para o bot"""
    global stop_bot_flag, bot_thread
    
    if not bot_state['running']:
        return jsonify({'success': False, 'error': 'Bot não está rodando'}), 400
    
    logger_callback("Comando de parada recebido via interface web...")
    stop_bot_flag = True
    
    # Aguardar um pouco para a thread processar a parada
    import time
    time.sleep(1)
    
    # Verificar se a thread ainda está rodando
    if bot_thread and bot_thread.is_alive():
        logger_callback("Aguardando thread do bot finalizar...")
        # Aguardar até 10 segundos para a thread terminar (aumentado de 5 para 10)
        bot_thread.join(timeout=10)
        
        if bot_thread.is_alive():
            logger_callback("⚠️ Thread não finalizou em tempo hábil - forçando parada")
            # Se ainda estiver rodando, marcar como parado mesmo assim
            bot_state['running'] = False
            stop_bot_flag = False
            socketio.emit('bot_stopped', {})
            return jsonify({'success': True, 'message': 'Bot parado (forçado)'})
        else:
            logger_callback("✅ Thread do bot finalizada com sucesso")
    
    # Garantir que o estado seja resetado
    bot_state['running'] = False
    stop_bot_flag = False
    
    # Emitir evento para atualizar a interface
    socketio.emit('bot_stopped', {})
    
    return jsonify({'success': True, 'message': 'Bot parado com sucesso'})

@app.route('/api/logs')
@login_required
def get_logs():
    """Retorna logs do bot"""
    return jsonify(bot_state['logs'])

# ========================================
# ROTAS DE FERRAMENTAS DO SISTEMA
# ========================================

@app.route('/api/tools/update-api', methods=['POST'])
@login_required
def update_iqoption_api():
    """Atualiza a API IQ Option"""
    try:
        import subprocess
        import sys
        
        logger_callback("🔄 Iniciando atualização da API IQ Option...")
        
        # Desinstalar versão antiga
        result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'iqoptionapi'], 
                              capture_output=True, text=True)
        
        # Instalar versão do GitHub
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 
                               'git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Obter versão instalada
            version_result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'iqoptionapi'], 
                                          capture_output=True, text=True)
            
            version = "Desconhecida"
            if version_result.returncode == 0:
                for line in version_result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        break
            
            logger_callback("✅ API IQ Option atualizada com sucesso!")
            return jsonify({
                'success': True, 
                'message': 'API IQ Option atualizada com sucesso!',
                'version': version
            })
        else:
            logger_callback(f"❌ Erro ao atualizar API: {result.stderr}")
            return jsonify({
                'success': False, 
                'error': f'Erro ao atualizar: {result.stderr}'
            }), 500
            
    except Exception as e:
        logger_callback(f"❌ Erro na atualização: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/tools/setup-video', methods=['POST'])
@login_required
def setup_video_recording():
    """Configura ambiente para gravação de vídeo"""
    try:
        import os
        
        logger_callback("🎥 Configurando ambiente de gravação...")
        
        # Criar pastas necessárias
        folders = [
            'Videos_TraderBot',
            'Videos_TraderBot/Raw',
            'Videos_TraderBot/Edited',
            'Videos_TraderBot/Social'
        ]
        
        created_folders = []
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                created_folders.append(folder)
        
        logger_callback("✅ Ambiente de gravação configurado!")
        
        return jsonify({
            'success': True,
            'message': 'Ambiente de gravação configurado com sucesso!',
            'folders': created_folders
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro na configuração: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/tools/diagnostic', methods=['POST'])
@login_required
def system_diagnostic():
    """Executa diagnóstico do sistema"""
    try:
        import subprocess
        import sys
        import platform
        
        logger_callback("🔍 Executando diagnóstico do sistema...")
        
        # Informações do sistema
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        os_info = f"{platform.system()} {platform.release()}"
        
        # Verificar versões das bibliotecas
        packages = ['iqoptionapi', 'flask', 'flask-socketio']
        versions = {}
        warnings = []
        
        for package in packages:
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            versions[package] = line.split(':')[1].strip()
                            break
                else:
                    versions[package] = "Não instalado"
                    warnings.append(f"{package} não está instalado")
            except:
                versions[package] = "Erro ao verificar"
                warnings.append(f"Erro ao verificar {package}")
        
        logger_callback("✅ Diagnóstico concluído!")
        
        return jsonify({
            'success': True,
            'python_version': python_version,
            'iqoption_version': versions.get('iqoptionapi', 'Desconhecida'),
            'flask_version': versions.get('flask', 'Desconhecida'),
            'os_info': os_info,
            'warnings': warnings
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro no diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/tools/files', methods=['GET'])
@login_required
def list_files():
    """Lista arquivos do sistema"""
    try:
        import os
        
        logger_callback("📂 Listando arquivos do sistema...")
        
        files = []
        
        # Listar arquivos importantes
        important_files = [
            'data/sinais.txt',
            'logs/',
            'config/',
            'estrategias.json',
            'requirements.txt'
        ]
        
        for file_path in important_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    files.append({
                        'name': file_path,
                        'type': 'folder',
                        'size': None
                    })
                else:
                    size = os.path.getsize(file_path)
                    size_str = f"{size} bytes"
                    if size > 1024:
                        size_str = f"{size/1024:.1f} KB"
                    if size > 1024*1024:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    
                    files.append({
                        'name': file_path,
                        'type': 'file',
                        'size': size_str
                    })
        
        logger_callback("✅ Arquivos listados!")
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro ao listar arquivos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ========================================
# ROTAS DE RELATÓRIOS
# ========================================

@app.route('/api/reports/performance', methods=['POST'])
@login_required
def generate_performance_report():
    """Gera relatório de performance"""
    try:
        logger_callback("📊 Gerando relatório de performance...")
        
        # Calcular estatísticas básicas
        total_operations = bot_state['sinais_executados']
        wins = bot_state['wins']
        losses = bot_state['losses']
        total_profit = bot_state['lucro_total']
        
        win_rate = (wins / total_operations * 100) if total_operations > 0 else 0
        
        # Simular sequências (em produção, calcular dos logs)
        best_streak = min(wins, 5)  # Simulação
        worst_streak = min(losses, 3)  # Simulação
        
        recommendations = []
        if win_rate < 50:
            recommendations.append("Considere ajustar a estratégia")
        if total_profit < 0:
            recommendations.append("Revise o gerenciamento de risco")
        if total_operations < 10:
            recommendations.append("Execute mais operações para análise estatística")
        
        logger_callback("✅ Relatório de performance gerado!")
        
        return jsonify({
            'success': True,
            'total_operations': total_operations,
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'best_streak': best_streak,
            'worst_streak': worst_streak,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro ao gerar relatório: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/reports/daily', methods=['POST'])
@login_required
def generate_daily_report():
    """Gera relatório diário"""
    try:
        from datetime import datetime
        
        logger_callback("📅 Gerando relatório diário...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Simular dados diários (em produção, buscar do banco de dados)
        operations = bot_state['sinais_executados']
        profit = bot_state['lucro_total']
        active_time = "2h 30min"  # Simulação
        
        logger_callback("✅ Relatório diário gerado!")
        
        return jsonify({
            'success': True,
            'date': today,
            'operations': operations,
            'profit': round(profit, 2),
            'active_time': active_time
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro ao gerar relatório diário: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/reports/weekly', methods=['POST'])
@login_required
def generate_weekly_report():
    """Gera relatório semanal"""
    try:
        from datetime import datetime, timedelta
        
        logger_callback("📆 Gerando relatório semanal...")
        
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        period = f"{week_start.strftime('%d/%m')} - {today.strftime('%d/%m')}"
        
        # Simular dados semanais (em produção, buscar do banco de dados)
        active_days = 5  # Simulação
        total_operations = bot_state['sinais_executados']
        weekly_profit = bot_state['lucro_total']
        best_day = "Segunda-feira"  # Simulação
        
        logger_callback("✅ Relatório semanal gerado!")
        
        return jsonify({
            'success': True,
            'period': period,
            'active_days': active_days,
            'total_operations': total_operations,
            'weekly_profit': round(weekly_profit, 2),
            'best_day': best_day
        })
        
    except Exception as e:
        logger_callback(f"❌ Erro ao gerar relatório semanal: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/reports/export-csv', methods=['POST'])
@login_required
def export_csv():
    """Exporta dados para CSV"""
    try:
        import csv
        import io
        
        logger_callback("📄 Exportando dados para CSV...")
        
        # Criar CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Data', 'Operações', 'Wins', 'Losses', 'Lucro'])
        
        # Dados (simulação - em produção, buscar do banco)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d'),
            bot_state['sinais_executados'],
            bot_state['wins'],
            bot_state['losses'],
            bot_state['lucro_total']
        ])
        
        # Preparar resposta
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=trader_bot_report.csv'}
        )
        
    except Exception as e:
        logger_callback(f"❌ Erro ao exportar CSV: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/reports/export-excel', methods=['POST'])
@login_required
def export_excel():
    """Exporta dados para Excel"""
    try:
        logger_callback("📊 Exportando dados para Excel...")
        
        # Simular exportação Excel (em produção, usar openpyxl)
        csv_response = export_csv()
        
        # Converter CSV para Excel (simulação)
        excel_data = csv_response.get_data(as_text=True)
        
        from flask import Response
        return Response(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=trader_bot_report.xlsx'}
        )
        
    except Exception as e:
        logger_callback(f"❌ Erro ao exportar Excel: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/reports/export-logs', methods=['POST'])
@login_required
def export_logs():
    """Exporta logs do sistema"""
    try:
        logger_callback("📋 Exportando logs...")
        
        # Coletar logs
        logs_text = ""
        for log in bot_state['logs']:
            logs_text += f"[{log['timestamp']}] {log['message']}\n"
        
        from flask import Response
        return Response(
            logs_text,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment; filename=trader_bot_logs.txt'}
        )
        
    except Exception as e:
        logger_callback(f"❌ Erro ao exportar logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@socketio.on('connect')
def handle_connect():
    """Cliente conectado via WebSocket"""
    emit('status_update', bot_state)
    print('Cliente conectado via WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print('Cliente desconectado')

@socketio.on('request_status')
def handle_status_request():
    """Cliente solicitou atualização de status"""
    emit('status_update', bot_state)

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('web/static', exist_ok=True)
    os.makedirs('web/templates', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('auth', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    # Inicializar banco de dados
    print("Inicializando banco de dados...")
    if not init_database():
        print("[AVISO] Aviso: Não foi possível inicializar o banco de dados.")
        print("   A aplicação funcionará, mas sem autenticação.")
    
    # Iniciar servidor
    # Usar porta do ambiente (para Render, Heroku, etc) ou 3000 como padrão para Easypanel
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')  # 0.0.0.0 para aceitar conexões externas
    
    print("="*60)
    print("TRADER BOT - Interface Web")
    print("="*60)
    print("")
    print(f"Servidor iniciado em: http://localhost:{port}")
    print("")
    print("Acesse pelo navegador para controlar o bot")
    print("Usuário de exemplo: wagnerlcg@gmail.com")
    print("="*60)
    
    try:
        socketio.run(app, debug=False, host=host, port=port, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        print("Tentando porta alternativa...")
        try:
            socketio.run(app, debug=False, host=host, port=8080, allow_unsafe_werkzeug=True)
        except Exception as e2:
            print(f"Erro na porta alternativa: {e2}")
            print("Tente fechar outros programas que possam estar usando as portas 3000 ou 8080")

