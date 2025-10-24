// Conexão WebSocket
const socket = io();

// Estado da aplicação
let appState = {
    running: false,
    mode: null,
    saldo_inicial: 0,
    saldo_atual: 0,
    sinais_executados: 0,
    sinais_totais: 0,
    wins: 0,
    losses: 0,
    lucro_total: 0,
    logs: [],
    sinais: [],
    configuracoes: {}
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadConfig();
    loadStatus();
    
    // Conectar ao WebSocket
    socket.on('connect', () => {
        console.log('Conectado ao servidor');
        socket.emit('request_status');
    });
    
    socket.on('disconnect', () => {
        console.log('Desconectado do servidor');
    });
    
    socket.on('status_update', (data) => {
        updateStatus(data);
    });
    
    socket.on('log_update', (log) => {
        addLog(log);
    });
    
    socket.on('bot_stopped', () => {
        updateBotButtons(false);
        showNotification('Bot encerrado', 'info');
    });
});

// Tabs
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Atualizar botões
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// Controle do Bot
async function startBot() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const email = document.getElementById('email').value.trim();
    const senha = document.getElementById('senha').value.trim();
    
    if (!email || !senha) {
        showNotification('Por favor, preencha email e senha', 'danger');
        return;
    }
    
    try {
        // Atualizar botões imediatamente para feedback visual
        updateBotButtons(true);
        
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode, email, senha })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'danger');
            // Se houve erro, restaurar estado anterior
            updateBotButtons(false);
        }
    } catch (error) {
        showNotification('Erro ao iniciar bot: ' + error.message, 'danger');
        // Se houve erro, restaurar estado anterior
        updateBotButtons(false);
    }
}

async function stopBot() {
    try {
        // Atualizar botões imediatamente para feedback visual
        updateBotButtons(false);
        
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'info');
        } else {
            showNotification(data.error, 'danger');
            // Se houve erro, restaurar estado anterior
            updateBotButtons(true);
        }
    } catch (error) {
        showNotification('Erro ao parar bot: ' + error.message, 'danger');
        // Se houve erro, restaurar estado anterior
        updateBotButtons(true);
    }
}

function updateBotButtons(running) {
    document.getElementById('btn-start').disabled = running;
    document.getElementById('btn-stop').disabled = !running;
    
    const statusBadge = document.getElementById('status-badge');
    if (running) {
        statusBadge.textContent = 'ONLINE';
        statusBadge.className = 'status-badge online';
    } else {
        statusBadge.textContent = 'OFFLINE';
        statusBadge.className = 'status-badge offline';
    }
}

// Sinais
async function uploadSinais() {
    const fileInput = document.getElementById('file-sinais');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/sinais', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${data.total} sinais carregados com sucesso!`, 'success');
            displaySinais(data.sinais);
        } else {
            showNotification('Erro ao carregar sinais: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Erro ao enviar arquivo: ' + error.message, 'danger');
    }
}

async function submitSinaisText() {
    const content = document.getElementById('sinais-content').value.trim();
    
    if (!content) {
        showNotification('Por favor, cole o conteúdo dos sinais', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/api/sinais', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${data.total} sinais carregados com sucesso!`, 'success');
            displaySinais(data.sinais);
        } else {
            showNotification('Erro ao carregar sinais: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Erro ao processar sinais: ' + error.message, 'danger');
    }
}

function displaySinais(sinais) {
    const preview = document.getElementById('sinais-preview');
    
    if (!sinais || sinais.length === 0) {
        preview.innerHTML = '<p class="text-center">Nenhum sinal carregado</p>';
        return;
    }
    
    let html = `
        <h3>Sinais Carregados (${sinais.length})</h3>
        <p><small>💡 Os valores de entrada serão definidos pelas configurações e estratégias</small></p>
        <div style="overflow-x: auto;">
            <table class="sinais-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Horário</th>
                        <th>Ativo</th>
                        <th>Tipo</th>
                        <th>Tempo</th>
                        <th>Entrada</th>
                        <th>Proteção 1</th>
                        <th>Proteção 2</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    sinais.forEach((sinal, index) => {
        // No novo formato, valor_entrada é null até ser definido pela estratégia
        const entrada = (sinal.valor_entrada && sinal.valor_entrada > 0) ? `$${sinal.valor_entrada.toFixed(2)}` : 'Configurar';
        const p1 = (sinal.protecao1 && sinal.protecao1 > 0) ? `$${sinal.protecao1.toFixed(2)}` : 'Auto';
        const p2 = (sinal.protecao2 && sinal.protecao2 > 0) ? `$${sinal.protecao2.toFixed(2)}` : 'Auto';
        
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${String(sinal.hora).padStart(2, '0')}:${String(sinal.minuto).padStart(2, '0')}</td>
                <td>${sinal.ativo}</td>
                <td><strong>${sinal.tipo}</strong></td>
                <td>M${sinal.tempo_minutos}</td>
                <td>${entrada}</td>
                <td>${p1}</td>
                <td>${p2}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    preview.innerHTML = html;
}

// Configurações
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('stop-loss').value = config.stop_loss || 10;
        document.getElementById('stop-win').value = config.stop_win || 20;
        document.getElementById('estrategia').value = config.estrategia || 'Martingale';
        document.getElementById('valor-entrada').value = config.valor_entrada || 10;
        document.getElementById('sons-habilitados').checked = config.sons_habilitados !== false;
        
        if (config.valor_entrada_tipo) {
            document.querySelector(`input[name="valor-tipo"][value="${config.valor_entrada_tipo}"]`).checked = true;
            updateValorTipo();
        }
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
    }
}

async function saveConfig() {
    const config = {
        stop_loss: parseFloat(document.getElementById('stop-loss').value),
        stop_win: parseFloat(document.getElementById('stop-win').value),
        estrategia: document.getElementById('estrategia').value,
        valor_entrada_tipo: document.querySelector('input[name="valor-tipo"]:checked').value,
        valor_entrada: parseFloat(document.getElementById('valor-entrada').value),
        sons_habilitados: document.getElementById('sons-habilitados').checked
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Configurações salvas com sucesso!', 'success');
        } else {
            showNotification('Erro ao salvar configurações', 'danger');
        }
    } catch (error) {
        showNotification('Erro ao salvar: ' + error.message, 'danger');
    }
}

function updateEstrategia() {
    // Aqui você pode adicionar parâmetros específicos de cada estratégia
    const estrategia = document.getElementById('estrategia').value;
    const paramsDiv = document.getElementById('estrategia-params');
    
    // Por enquanto, vazio - pode ser expandido no futuro
    paramsDiv.innerHTML = '';
}

function updateValorTipo() {
    const tipo = document.querySelector('input[name="valor-tipo"]:checked').value;
    
    if (tipo === 'fixo') {
        document.getElementById('valor-fixo-group').classList.remove('hidden');
        document.getElementById('valor-percentual-group').classList.add('hidden');
    } else {
        document.getElementById('valor-fixo-group').classList.add('hidden');
        document.getElementById('valor-percentual-group').classList.remove('hidden');
    }
}

// Status
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateStatus(data);
    } catch (error) {
        console.error('Erro ao carregar status:', error);
    }
}

function updateStatus(data) {
    appState = { ...appState, ...data };
    
    // Atualizar badges
    updateBotButtons(data.running);
    
    if (data.mode) {
        document.getElementById('mode-badge').textContent = data.mode.toUpperCase();
    }
    
    // Atualizar cards de estatísticas
    document.getElementById('saldo-atual').textContent = `$${(data.saldo_atual || 0).toFixed(2)}`;
    
    const variacao = (data.saldo_atual || 0) - (data.saldo_inicial || 0);
    const variacaoEl = document.getElementById('saldo-variacao');
    variacaoEl.textContent = `${variacao >= 0 ? '+' : ''}$${variacao.toFixed(2)}`;
    variacaoEl.style.color = variacao >= 0 ? 'var(--success)' : 'var(--danger)';
    
    document.getElementById('sinais-executados').textContent = 
        `${data.sinais_executados || 0} / ${data.sinais_totais || 0}`;
    
    document.getElementById('wins').textContent = data.wins || 0;
    document.getElementById('losses').textContent = data.losses || 0;
    
    const total = (data.wins || 0) + (data.losses || 0);
    const winRate = total > 0 ? ((data.wins / total) * 100).toFixed(1) : 0;
    const lossRate = total > 0 ? ((data.losses / total) * 100).toFixed(1) : 0;
    
    document.getElementById('win-rate').textContent = `${winRate}% taxa`;
    document.getElementById('loss-rate').textContent = `${lossRate}% taxa`;
    
    // Atualizar sinais se disponível
    if (data.sinais && data.sinais.length > 0) {
        displaySinais(data.sinais);
    }
}

// Logs
function addLog(log) {
    const container = document.getElementById('logs-container');
    
    // Remover mensagem vazia
    const emptyMsg = container.querySelector('.log-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    // Detectar tipo de log baseado no conteúdo
    const message = log.message.toLowerCase();
    let logClass = 'log-entry';
    let messageClass = 'log-message';
    
    if (message.includes('error') || message.includes('erro') || message.includes('falha') || message.includes('fail')) {
        logClass += ' log-error';
        messageClass += ' log-error-text';
    } else if (message.includes('win') || message.includes('sucesso') || message.includes('success') || message.includes('✅')) {
        logClass += ' log-success';
        messageClass += ' log-success-text';
    } else if (message.includes('warning') || message.includes('aviso') || message.includes('alerta') || message.includes('⚠️')) {
        logClass += ' log-warning';
        messageClass += ' log-warning-text';
    } else if (message.includes('info') || message.includes('[status]') || message.includes('protecao')) {
        logClass += ' log-info';
        messageClass += ' log-info-text';
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = logClass;
    logEntry.innerHTML = `
        <span class="log-timestamp">[${log.timestamp}]</span>
        <span class="${messageClass}">${escapeHtml(log.message)}</span>
    `;
    
    container.appendChild(logEntry);
    
    // Auto-scroll para o final
    container.scrollTop = container.scrollHeight;
    
    // Manter apenas últimos 100 logs
    const logs = container.querySelectorAll('.log-entry');
    if (logs.length > 100) {
        logs[0].remove();
    }
}

function clearLogs() {
    const container = document.getElementById('logs-container');
    container.innerHTML = '<p class="log-empty">Logs limpos. Aguardando novos logs...</p>';
}

// Controle de tamanho de fonte dos logs
let tamanhoFonteLogs = 15;

function aumentarFonte() {
    tamanhoFonteLogs += 2;
    if (tamanhoFonteLogs > 24) tamanhoFonteLogs = 24;
    document.getElementById('logs-container').style.fontSize = tamanhoFonteLogs + 'px';
    localStorage.setItem('tamanhoFonteLogs', tamanhoFonteLogs);
}

function diminuirFonte() {
    tamanhoFonteLogs -= 2;
    if (tamanhoFonteLogs < 10) tamanhoFonteLogs = 10;
    document.getElementById('logs-container').style.fontSize = tamanhoFonteLogs + 'px';
    localStorage.setItem('tamanhoFonteLogs', tamanhoFonteLogs);
}

// Alternar tema dos logs (escuro/claro)
let temaEscuro = true;

function toggleTemaLogs() {
    const container = document.getElementById('logs-container');
    temaEscuro = !temaEscuro;
    
    if (temaEscuro) {
        // Tema escuro
        container.style.background = '#1f2937';
        container.style.color = '#f3f4f6';
        container.style.borderColor = '#374151';
    } else {
        // Tema claro
        container.style.background = '#f9fafb';
        container.style.color = '#1f2937';
        container.style.borderColor = '#d1d5db';
        
        // Atualizar cores dos logs existentes
        const entries = container.querySelectorAll('.log-entry');
        entries.forEach(entry => {
            entry.style.background = 'rgba(229, 231, 235, 0.5)';
        });
    }
    
    localStorage.setItem('temaEscuroLogs', temaEscuro);
}

// Restaurar preferências ao carregar
document.addEventListener('DOMContentLoaded', () => {
    // Restaurar tamanho de fonte
    const fonteSalva = localStorage.getItem('tamanhoFonteLogs');
    if (fonteSalva) {
        tamanhoFonteLogs = parseInt(fonteSalva);
        document.getElementById('logs-container').style.fontSize = tamanhoFonteLogs + 'px';
    }
    
    // Restaurar tema
    const temaSalvo = localStorage.getItem('temaEscuroLogs');
    if (temaSalvo === 'false') {
        toggleTemaLogs();
    }
});

// Notificações
function showNotification(message, type = 'info') {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        animation: slideIn 0.3s ease-out;
    `;
    
    const icon = type === 'success' ? '✅' : type === 'danger' ? '❌' : 'ℹ️';
    notification.innerHTML = `<strong>${icon}</strong> ${message}`;
    
    document.body.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Utilitários
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Adicionar animações CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

