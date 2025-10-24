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
# Configurar SocketIO sem especificar async_mode para compatibilidade
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

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

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
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
        
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
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
    
    # Filtrar mensagens técnicas específicas
    technical_patterns = [
        'sinal demo encontrado:',
        'entrada principal:',
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
    print(f"DEBUG: Atualizando saldo para ${saldo_atual:.2f} (inicial={is_initial})")
    
    # Se for o saldo inicial da conexão, atualizar ambos
    if is_initial or bot_state['saldo_inicial'] == 0:
        bot_state['saldo_inicial'] = saldo_atual
        logger_callback(f"Saldo inicial definido: ${saldo_atual:.2f}")
    
    bot_state['saldo_atual'] = saldo_atual
    logger_callback(f"Saldo atualizado: ${saldo_atual:.2f}")
    socketio.emit('status_update', bot_state)

def run_bot_async(mode, arquivo_sinais, email, senha, config):
    """Executa o bot em modo assíncrono"""
    global stop_bot_flag
    stop_bot_flag = False
    
    # Criar diretório de logs se não existir
    import os
    os.makedirs('logs', exist_ok=True)
    
    logger = setup_logger("bot_web", "logs/bot_web.log")
    
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
                    stop_callback=lambda: stop_bot_flag
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
                    stop_callback=lambda: stop_bot_flag
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
            return redirect(url_for('index'))
        else:
            flash('E-mail não encontrado ou usuário não possui acesso. Verifique se você está cadastrado e pagou.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

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
    
    stop_bot_flag = True
    logger_callback("Comando de parada recebido via interface web...")
    
    # Aguardar um pouco para a thread processar a parada
    import time
    time.sleep(0.5)
    
    # Verificar se a thread ainda está rodando
    if bot_thread and bot_thread.is_alive():
        logger_callback("Aguardando thread do bot finalizar...")
        # Aguardar até 5 segundos para a thread terminar
        bot_thread.join(timeout=5)
        
        if bot_thread.is_alive():
            logger_callback("⚠️ Thread não finalizou em tempo hábil")
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
        print("⚠️ Aviso: Não foi possível inicializar o banco de dados.")
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

