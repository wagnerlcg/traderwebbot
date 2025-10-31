(function() {
// Evitar múltiplas cargas do mesmo script
if (window.__TRADERBOT_APP_LOADED__) {
  console.warn('App JS já inicializado. Ignorando recarga.');
  return;
}
window.__TRADERBOT_APP_LOADED__ = true;

// Conexão WebSocket
// Determinar o path base da aplicação
// Usar APP_BASE_PATH se definido pelo servidor, senão usar pathname
const basePath = window.APP_BASE_PATH || (() => {
    let path = window.location.pathname;
    // Remover barra final se existir
    if (path.endsWith('/') && path.length > 1) {
        path = path.slice(0, -1);
    }
    // Se estiver na raiz ou vazio, usar string vazia
    if (path === '/' || path === '') {
        path = '';
    }
    return path;
})();

const socketPath = basePath ? `${basePath}/socket.io` : '/socket.io';
let socket = null;

// Configurar base path para todas as chamadas API
const API_BASE = basePath || '';
// Expor para uso fora desta IIFE (handlers inline)
window.API_BASE = API_BASE;

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
// Expor estado para fora da IIFE (garantir acesso global)
window.__APP_STATE = appState;
window.appState = appState;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadConfig();
    loadStatus();
    updateEstrategia(); // Atualizar campos da estratégia baseado na seleção padrão

    // Restaurar tema salvo
    try {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark');
        }
    } catch {}

    // Garantir botão de tema no header (fallback caso o template esteja em cache)
    try {
        if (!document.getElementById('theme-toggle-btn')) {
            const headerRight = document.querySelector('.header-right');
            if (headerRight) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.id = 'theme-toggle-btn';
                btn.className = 'btn btn-secondary';
                btn.title = 'Alternar tema';
                btn.textContent = '🌓 Tema';
                btn.addEventListener('click', toggleTheme);
                headerRight.appendChild(btn);
            }
        }
    } catch {}

    // Conectar ao WebSocket (se Socket.IO estiver disponível)
    try {
        if (window.io) {
            // Forçar polling no PythonAnywhere (não suporta WebSockets nativos)
            // O PythonAnywhere funciona apenas com long-polling via HTTP
            socket = io({ 
                path: socketPath,
                transports: ['polling'],  // Usar apenas polling, sem tentar WebSocket
                upgrade: false,           // Desabilitar upgrade para WebSocket
                rememberUpgrade: false    // Não lembrar tentativas de upgrade
            });

            socket.on('connect', () => {
                console.log('Conectado ao servidor');
                updateWebSocketStatus(true);
                socket.emit('request_status');
            });

            socket.on('disconnect', () => {
                console.log('Desconectado do servidor');
                updateWebSocketStatus(false);
            });

            socket.on('status_update', (data) => {
                console.log('[WebSocket] Recebido status_update:', data);
                updateStatus(data);
            });

            socket.on('log_update', (log) => {
                addLog(log);
            });

            socket.on('bot_stopped', () => {
                updateBotButtons(false);
                showNotification('Bot encerrado', 'info');
            });

            // Solicitar status periodicamente para garantir atualizações
            setInterval(() => {
                if (socket && socket.connected) {
                    socket.emit('request_status');
                }
            }, 2000); // A cada 2 segundos
        } else {
            console.warn('Socket.IO não carregado. Continuando sem WebSocket.');
            updateWebSocketStatus(false);
        }
    } catch (e) {
        console.warn('Falha ao iniciar Socket.IO:', e);
        updateWebSocketStatus(false);
    }
});

})();

// Variáveis globais para funções fora da IIFE
var API_BASE = (typeof window !== 'undefined' && window.API_BASE) ? window.API_BASE : '';
var appState = (typeof window !== 'undefined' && window.appState) ? window.appState : {
    running: false, mode: null, saldo_inicial: 0, saldo_atual: 0,
    sinais_executados: 0, sinais_totais: 0, wins: 0, losses: 0,
    lucro_total: 0, logs: [], sinais: [], configuracoes: {}
};

// Tabs
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });

    // Restaurar aba ativa do localStorage
    const savedTab = (localStorage.getItem('activeTab') || 'controle');
    if (savedTab && savedTab !== 'controle') {
        switchTab(savedTab);
    }
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

    // Persistir aba ativa
    try { localStorage.setItem('activeTab', tabName); } catch {}
}

// Tema claro/escuro
function toggleTheme() {
    document.body.classList.toggle('dark');
    try {
        localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    } catch {}
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
        
        const response = await fetch(`${API_BASE}/api/start`, {
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
        
        const response = await fetch(`${API_BASE}/api/stop`, {
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

function updateWebSocketStatus(connected) {
    const wsIndicator = document.getElementById('ws-status');
    if (wsIndicator) {
        if (connected) {
            wsIndicator.textContent = '🟢';
            wsIndicator.className = 'ws-indicator connected';
            wsIndicator.title = 'WebSocket Conectado';
        } else {
            wsIndicator.textContent = '🔴';
            wsIndicator.className = 'ws-indicator disconnected';
            wsIndicator.title = 'WebSocket Desconectado';
        }
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
        const response = await fetch(`${API_BASE}/api/sinais`, {
            method: 'POST',
            body: formData
        });
        
        // Verificar se a resposta foi bem-sucedida
        if (!response.ok) {
            // Tentar ler a mensagem de erro se for JSON
            let errorMessage = `Erro ${response.status}: ${response.statusText}`;
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } else {
                    // Se não for JSON, ler como texto (mas limitar tamanho)
                    const text = await response.text();
                    if (text && text.length < 200) {
                        errorMessage = text;
                    }
                }
            } catch (e) {
                // Se falhar ao ler erro, usar mensagem padrão
            }
            showNotification('Erro ao enviar arquivo: ' + errorMessage, 'danger');
            return;
        }
        
        // Verificar se o conteúdo é JSON antes de fazer parse
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            showNotification('Erro: resposta do servidor não é JSON', 'danger');
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${data.total} sinais carregados com sucesso!`, 'success');
            displaySinais(data.sinais);
        } else {
            showNotification('Erro ao carregar sinais: ' + (data.error || 'Erro desconhecido'), 'danger');
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
        const response = await fetch(`${API_BASE}/api/sinais`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });
        
        // Verificar se a resposta foi bem-sucedida
        if (!response.ok) {
            // Tentar ler a mensagem de erro se for JSON
            let errorMessage = `Erro ${response.status}: ${response.statusText}`;
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } else {
                    // Se não for JSON, ler como texto (mas limitar tamanho)
                    const text = await response.text();
                    if (text && text.length < 200) {
                        errorMessage = text;
                    }
                }
            } catch (e) {
                // Se falhar ao ler erro, usar mensagem padrão
            }
            showNotification('Erro ao processar sinais: ' + errorMessage, 'danger');
            return;
        }
        
        // Verificar se o conteúdo é JSON antes de fazer parse
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            showNotification('Erro: resposta do servidor não é JSON', 'danger');
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${data.total} sinais carregados com sucesso!`, 'success');
            displaySinais(data.sinais);
        } else {
            showNotification('Erro ao carregar sinais: ' + (data.error || 'Erro desconhecido'), 'danger');
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
        const response = await fetch(`${API_BASE}/api/config`);
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
    const estrategia = document.getElementById('estrategia').value;
    
    const config = {
        stop_loss: parseFloat(document.getElementById('stop-loss').value),
        stop_win: parseFloat(document.getElementById('stop-win').value),
        estrategia: estrategia,
        valor_entrada_tipo: document.querySelector('input[name="valor-tipo"]:checked').value,
        valor_entrada: parseFloat(document.getElementById('valor-entrada').value),
        sons_habilitados: document.getElementById('sons-habilitados').checked
    };
    
    // Adicionar parâmetros específicos da estratégia
    if (estrategia === 'Martingale') {
        const nivelEl = document.getElementById('martingale-nivel');
        if (nivelEl) {
            config.martingale_nivel = nivelEl.value;
        }
    } else if (estrategia === 'Masaniello') {
        const entradasEl = document.getElementById('masaniello-entradas');
        const acertosEl = document.getElementById('masaniello-acertos');
        if (entradasEl) config.masaniello_entradas = parseInt(entradasEl.value);
        if (acertosEl) config.masaniello_acertos = parseInt(acertosEl.value);
    } else if (estrategia === 'Soros') {
        const payoutEl = document.getElementById('soros-payout');
        if (payoutEl) config.soros_payout = parseFloat(payoutEl.value);
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/config`, {
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
    const estrategia = document.getElementById('estrategia').value;
    const paramsDiv = document.getElementById('estrategia-params');
    
    let html = '';
    
    if (estrategia === 'Valor Fixo') {
        html = '<small>Esta estratégia usa o mesmo valor para todas as operações</small>';
    } else if (estrategia === 'Martingale') {
        html = `
            <div class="form-group">
                <label for="martingale-nivel">Nível do Martingale</label>
                <select id="martingale-nivel">
                    <option value="G1">Nível 1 (G1) - Multiplicador 2x</option>
                    <option value="G2" selected>Nível 2 (G2) - Multiplicador 4x</option>
                </select>
                <small>Quanto maior o nível, maior a progressão de valor</small>
            </div>
        `;
    } else if (estrategia === 'Masaniello') {
        html = `
            <div class="form-group">
                <label for="masaniello-entradas">Quantidade de Entradas</label>
                <input type="number" id="masaniello-entradas" min="3" max="10" value="5">
                <small>Número de entradas no ciclo Masaniello (3-10)</small>
            </div>
            <div class="form-group">
                <label for="masaniello-acertos">Número de Acertos Necessários</label>
                <input type="number" id="masaniello-acertos" min="1" max="5" value="3">
                <small>Quantos acertos precisam para recuperar o investimento</small>
            </div>
        `;
    } else if (estrategia === 'Soros') {
        html = `
            <div class="form-group">
                <label for="soros-payout">Payout (%)</label>
                <input type="number" id="soros-payout" min="70" max="95" value="87" step="1">
                <small>Percentual de retorno esperado (70-95%)</small>
            </div>
        `;
    }
    
    paramsDiv.innerHTML = html;
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
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        updateStatus(data);
    } catch (error) {
        console.error('Erro ao carregar status:', error);
    }
}

function updateStatus(data) {
    // Sempre usar window.appState como fonte da verdade (disponível globalmente)
    if (typeof window !== 'undefined') {
        window.appState = window.appState || {
            running: false, mode: null, saldo_inicial: 0, saldo_atual: 0,
            sinais_executados: 0, sinais_totais: 0, wins: 0, losses: 0,
            lucro_total: 0, logs: [], sinais: [], configuracoes: {}
        };
        window.appState = { ...window.appState, ...data };
        // Sincronizar variável local também
        if (typeof appState !== 'undefined') {
            appState = window.appState;
        }
    } else {
        // Fallback se window não estiver disponível (não deveria acontecer no browser)
        if (typeof appState === 'undefined') {
            appState = {};
        }
        appState = { ...appState, ...data };
    }
    
    // Atualizar badges
    updateBotButtons(data.running);
    
    if (data.mode) {
        document.getElementById('mode-badge').textContent = data.mode.toUpperCase();
    }
    
    // Atualizar cards de estatísticas com animação
    const saldoAtual = data.saldo_atual || 0;
    const saldoInicial = data.saldo_inicial || 0;
    
    // Saldo atual com animação
    const saldoElement = document.getElementById('saldo-atual');
    if (saldoElement) {
        saldoElement.textContent = `$${saldoAtual.toFixed(2)}`;
        saldoElement.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => saldoElement.style.animation = '', 500);
    }
    
    // Variação do saldo
    const variacao = saldoAtual - saldoInicial;
    const variacaoEl = document.getElementById('saldo-variacao');
    if (variacaoEl) {
        variacaoEl.textContent = `${variacao >= 0 ? '+' : ''}$${variacao.toFixed(2)}`;
        variacaoEl.style.color = variacao >= 0 ? 'var(--success)' : 'var(--danger)';
        variacaoEl.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => variacaoEl.style.animation = '', 500);
    }
    
    // Sinais executados com animação
    const sinaisElement = document.getElementById('sinais-executados');
    if (sinaisElement) {
        sinaisElement.textContent = `${data.sinais_executados || 0} / ${data.sinais_totais || 0}`;
        sinaisElement.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => sinaisElement.style.animation = '', 500);
    }
    
    // Wins e Losses com animação
    const winsElement = document.getElementById('wins');
    const lossesElement = document.getElementById('losses');
    
    if (winsElement) {
        winsElement.textContent = data.wins || 0;
        winsElement.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => winsElement.style.animation = '', 500);
    }
    
    if (lossesElement) {
        lossesElement.textContent = data.losses || 0;
        lossesElement.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => lossesElement.style.animation = '', 500);
    }
    
    // Taxas de acerto
    const total = (data.wins || 0) + (data.losses || 0);
    const winRate = total > 0 ? ((data.wins / total) * 100).toFixed(1) : 0;
    const lossRate = total > 0 ? ((data.losses / total) * 100).toFixed(1) : 0;
    
    const winRateElement = document.getElementById('win-rate');
    const lossRateElement = document.getElementById('loss-rate');
    
    if (winRateElement) {
        winRateElement.textContent = `${winRate}% taxa`;
    }
    if (lossRateElement) {
        lossRateElement.textContent = `${lossRate}% taxa`;
    }
    
    // Log de debug para verificar atualizações
    console.log('[UI] Status atualizado:', {
        saldo_atual: saldoAtual,
        saldo_inicial: saldoInicial,
        sinais_executados: data.sinais_executados,
        sinais_totais: data.sinais_totais,
        wins: data.wins,
        losses: data.losses
    });
    
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
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.05);
            opacity: 0.8;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    @keyframes glow {
        0% {
            box-shadow: 0 0 5px rgba(16, 185, 129, 0.5);
        }
        50% {
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
        }
        100% {
            box-shadow: 0 0 5px rgba(16, 185, 129, 0.5);
        }
    }
`;
document.head.appendChild(style);

// ========================================
// FERRAMENTAS DO SISTEMA
// ========================================

// Atualizar API IQ Option
async function updateIQOptionAPI() {
    const output = document.getElementById('tools-output');
    output.innerHTML = '🔄 Atualizando API IQ Option...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/tools/update-api`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ ${data.message}\n`;
            output.innerHTML += `📦 Versão instalada: ${data.version}\n`;
            showNotification('API IQ Option atualizada com sucesso!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao atualizar API', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Configurar Gravação de Vídeo
async function setupVideoRecording() {
    const output = document.getElementById('tools-output');
    output.innerHTML = '🎥 Configurando ambiente de gravação...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/tools/setup-video`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ ${data.message}\n`;
            output.innerHTML += `📁 Pastas criadas:\n`;
            data.folders.forEach(folder => {
                output.innerHTML += `   - ${folder}\n`;
            });
            output.innerHTML += `\n🎬 Instruções:\n`;
            output.innerHTML += `1. Instale OBS Studio (gratuito)\n`;
            output.innerHTML += `2. Configure para salvar em: Videos_TraderBot/Raw/\n`;
            output.innerHTML += `3. Execute uma demonstração\n`;
            output.innerHTML += `4. Grave a tela durante a execução\n`;
            showNotification('Ambiente de gravação configurado!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao configurar gravação', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Diagnóstico do Sistema
async function runSystemDiagnostic() {
    const output = document.getElementById('tools-output');
    output.innerHTML = '🔍 Executando diagnóstico do sistema...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/tools/diagnostic`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ Sistema OK\n\n`;
            output.innerHTML += `📊 Informações do Sistema:\n`;
            output.innerHTML += `   - Python: ${data.python_version}\n`;
            output.innerHTML += `   - IQ Option API: ${data.iqoption_version}\n`;
            output.innerHTML += `   - Flask: ${data.flask_version}\n`;
            output.innerHTML += `   - Sistema: ${data.os_info}\n\n`;
            
            if (data.warnings && data.warnings.length > 0) {
                output.innerHTML += `⚠️ Avisos:\n`;
                data.warnings.forEach(warning => {
                    output.innerHTML += `   - ${warning}\n`;
                });
            }
            
            showNotification('Diagnóstico concluído!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro no diagnóstico', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Gerenciador de Arquivos
async function openFileManager() {
    const output = document.getElementById('tools-output');
    output.innerHTML = '📂 Carregando arquivos do sistema...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/tools/files`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `📁 Arquivos encontrados:\n\n`;
            
            data.files.forEach(file => {
                const icon = file.type === 'folder' ? '📁' : '📄';
                const size = file.size ? ` (${file.size})` : '';
                output.innerHTML += `${icon} ${file.name}${size}\n`;
            });
            
            output.innerHTML += `\n💡 Dica: Use o upload na aba Sinais para carregar novos arquivos\n`;
            showNotification('Arquivos carregados!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao carregar arquivos', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// ========================================
// RELATÓRIOS E ANÁLISES
// ========================================

// Relatório de Performance
async function generatePerformanceReport() {
    const output = document.getElementById('reports-output');
    output.innerHTML = '📊 Gerando relatório de performance...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/reports/performance`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ Relatório gerado!\n\n`;
            output.innerHTML += `📈 Estatísticas:\n`;
            output.innerHTML += `   - Total de operações: ${data.total_operations}\n`;
            output.innerHTML += `   - Taxa de acerto: ${data.win_rate}%\n`;
            output.innerHTML += `   - Lucro total: $${data.total_profit}\n`;
            output.innerHTML += `   - Melhor sequência: ${data.best_streak} wins\n`;
            output.innerHTML += `   - Pior sequência: ${data.worst_streak} losses\n\n`;
            
            if (data.recommendations) {
                output.innerHTML += `💡 Recomendações:\n`;
                data.recommendations.forEach(rec => {
                    output.innerHTML += `   - ${rec}\n`;
                });
            }
            
            showNotification('Relatório de performance gerado!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao gerar relatório', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Relatório Diário
async function generateDailyReport() {
    const output = document.getElementById('reports-output');
    output.innerHTML = '📅 Gerando relatório diário...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/reports/daily`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ Relatório diário gerado!\n\n`;
            output.innerHTML += `📊 Resumo do dia:\n`;
            output.innerHTML += `   - Data: ${data.date}\n`;
            output.innerHTML += `   - Operações: ${data.operations}\n`;
            output.innerHTML += `   - Lucro: $${data.profit}\n`;
            output.innerHTML += `   - Tempo ativo: ${data.active_time}\n`;
            
            showNotification('Relatório diário gerado!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao gerar relatório', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Relatório Semanal
async function generateWeeklyReport() {
    const output = document.getElementById('reports-output');
    output.innerHTML = '📆 Gerando relatório semanal...\n';
    
    try {
        const response = await fetch(`${API_BASE}/api/reports/weekly`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            output.innerHTML += `✅ Relatório semanal gerado!\n\n`;
            output.innerHTML += `📊 Resumo da semana:\n`;
            output.innerHTML += `   - Período: ${data.period}\n`;
            output.innerHTML += `   - Dias ativos: ${data.active_days}\n`;
            output.innerHTML += `   - Total operações: ${data.total_operations}\n`;
            output.innerHTML += `   - Lucro semanal: $${data.weekly_profit}\n`;
            output.innerHTML += `   - Melhor dia: ${data.best_day}\n`;
            
            showNotification('Relatório semanal gerado!', 'success');
        } else {
            output.innerHTML += `❌ Erro: ${data.error}\n`;
            showNotification('Erro ao gerar relatório', 'danger');
        }
    } catch (error) {
        output.innerHTML += `❌ Erro de conexão: ${error.message}\n`;
        showNotification('Erro de conexão', 'danger');
    }
}

// Exportar CSV
async function exportToCSV() {
    try {
        const response = await fetch(`${API_BASE}/api/reports/export-csv`, {
            method: 'POST'
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'trader_bot_report.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Arquivo CSV exportado!', 'success');
    } catch (error) {
        showNotification('Erro ao exportar CSV: ' + error.message, 'danger');
    }
}

// Exportar Excel
async function exportToExcel() {
    try {
        const response = await fetch(`${API_BASE}/api/reports/export-excel`, {
            method: 'POST'
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'trader_bot_report.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Arquivo Excel exportado!', 'success');
    } catch (error) {
        showNotification('Erro ao exportar Excel: ' + error.message, 'danger');
    }
}

// Exportar Logs
async function exportLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/reports/export-logs`, {
            method: 'POST'
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'trader_bot_logs.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Logs exportados!', 'success');
    } catch (error) {
        showNotification('Erro ao exportar logs: ' + error.message, 'danger');
    }
}

// Atualizar Gráfico
function updateChart(period) {
    const canvas = document.getElementById('performanceChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Dados de exemplo - em produção, buscar do servidor
    const data = {
        daily: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            profits: [0, 5, -2, 8, 12, 15]
        },
        weekly: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            profits: [20, -5, 15, 30, 10, 0, 0]
        },
        monthly: {
            labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            profits: [50, 75, 30, 60]
        }
    };
    
    const selectedData = data[period];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: selectedData.labels,
            datasets: [{
                label: 'Lucro ($)',
                data: selectedData.profits,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Performance - ${period.charAt(0).toUpperCase() + period.slice(1)}`
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e5e7eb'
                    }
                },
                x: {
                    grid: {
                        color: '#e5e7eb'
                    }
                }
            }
        }
    });
}

// Garantir que variáveis globais estão disponíveis
if (typeof window !== 'undefined') {
    if (!window.appState) {
        window.appState = {
            running: false, mode: null, saldo_inicial: 0, saldo_atual: 0,
            sinais_executados: 0, sinais_totais: 0, wins: 0, losses: 0,
            lucro_total: 0, logs: [], sinais: [], configuracoes: {}
        };
    }
    if (!window.API_BASE) {
        window.API_BASE = '';
    }
}
