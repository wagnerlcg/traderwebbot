# 🌐 Interface Web - Trader Bot

Interface web moderna para controle do bot de trading com recursos em tempo real.

## 🚀 Início Rápido

### 1. Instalação
```bash
pip install -r requirements.txt
```

### 2. Iniciar Interface
```bash
python web_interface.py
```
Ou execute: `INICIAR-INTERFACE-WEB.bat`

### 3. Acessar
Abra seu navegador em: **http://localhost:3000**

## ✨ Recursos Principais

### 🎮 Controle do Bot
- **Iniciar/Parar**: Botões visuais para controle
- **Modo Demo/Real**: Seleção do tipo de operação
- **Credenciais**: Login IQ Option integrado
- **Status em Tempo Real**: Indicadores visuais de estado

### 📊 Dashboard
- **Saldo Atual**: Valor atual da conta
- **Variação**: Diferença do saldo inicial
- **Sinais Executados**: Progresso das operações
- **Wins/Losses**: Estatísticas de sucesso
- **Taxa de Acerto**: Percentual de vitórias

### 📋 Gerenciamento de Sinais
- **Upload de Arquivo**: Carregar arquivo .txt
- **Colar Texto**: Inserir sinais diretamente
- **Visualização**: Tabela com todos os sinais
- **Validação**: Verificação automática do formato

### ⚙️ Configurações
- **Stop Loss**: Proteção contra perdas (1-10%)
- **Stop Win**: Meta de lucro (5-100%)
- **Estratégias**: Martingale, Soros, Masaniello
- **Valor de Entrada**: Fixo ou percentual da banca

### 📄 Logs em Tempo Real
- **Atualizações Instantâneas**: Via WebSockets
- **Categorização**: Sucesso, erro, aviso, info
- **Controles**: Aumentar/diminuir fonte, tema claro/escuro
- **Histórico**: Últimos 100 logs mantidos

## 📱 Formato de Sinais Simplificado

### Formato Atual
```
M1;ATIVO;HH:MM;PUT/CALL
```

### Exemplos
```
M1;EURUSD-OTC;19:00;CALL
M5;GBPUSD-OTC;19:05;PUT
M15;AUDCAD-OTC;19:10;CALL
M30;NZDUSD-OTC;19:15;PUT
```

### Campos
- **M1/M5/M15/M30**: Tempo de execução (minutos)
- **ATIVO**: Nome do ativo (ex: EURUSD-OTC)
- **HH:MM**: Hora de entrada (formato 24h)
- **PUT/CALL**: Tipo de operação

### ⚠️ Importante
- Os valores de entrada são definidos **globalmente** nas configurações
- Não inclua valores monetários no arquivo de sinais
- Comentários começam com `#` e são ignorados
- Linhas em branco são ignoradas

## 🔧 Configurações Avançadas

### Proteções
- **Stop Loss**: Perda máxima permitida (padrão: 10%)
- **Stop Win**: Meta de lucro para parar (padrão: 20%)

### Estratégias
- **Martingale**: Dobra o valor após perda
- **Soros**: Estratégia de recuperação progressiva
- **Masaniello**: Sistema de recuperação em sequência

### Valores de Entrada
- **Valor Fixo**: Valor constante em dólares
- **Percentual**: Porcentagem do saldo atual

## 🚨 Troubleshooting

### Erros Comuns

#### ❌ Erro de Conexão
```
⚠️ Erro de conexão detectado. Aguarde 2-3 minutos antes de tentar novamente.
```
**Solução**: Aguarde alguns minutos e tente novamente.

#### ❌ Erro de Autenticação
```
⚠️ Erro de autenticação. Verifique email e senha.
```
**Solução**: Verifique suas credenciais IQ Option.

#### ❌ Erro de Timeout
```
⚠️ Timeout de conexão. Verifique sua internet.
```
**Solução**: Verifique sua conexão com a internet.

#### ❌ Erro de Saldo
```
⚠️ Erro de saldo. Verifique sua conta.
```
**Solução**: Verifique o saldo da sua conta IQ Option.

### Problemas de Interface

#### 🔄 Interface não carrega
- Verifique se a porta 3000 está livre
- Tente acessar http://localhost:8080
- Reinicie o servidor

#### 📡 WebSockets não funcionam
- Verifique se o JavaScript está habilitado
- Tente atualizar a página (F5)
- Verifique o console do navegador (F12)

#### 📁 Arquivo de sinais não carrega
- Verifique o formato (4 campos separados por `;`)
- Certifique-se que o arquivo é .txt
- Verifique se não há caracteres especiais

## 🛠️ Desenvolvimento

### Estrutura de Arquivos
```
web_interface.py          # Servidor Flask principal
web/
├── templates/
│   └── index.html        # Interface HTML
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   └── js/
│       └── app.js        # JavaScript frontend
config/
└── interface_config.json # Configurações da interface
```

### Tecnologias
- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Comunicação**: WebSockets para tempo real
- **Estilo**: Design responsivo e moderno

### Portas
- **Padrão**: 3000 (compatível com Easypanel)
- **Alternativa**: 8080 (se 3000 estiver ocupada)
- **Variável**: PORT (para Render, Heroku, etc.)

## 📞 Suporte

Para problemas específicos da interface web:

1. **Verifique os logs** na aba "Logs" da interface
2. **Consulte o console** do navegador (F12)
3. **Reinicie o servidor** se necessário
4. **Verifique as dependências** com `pip install -r requirements.txt`

---

**🎯 Interface web operacional e pronta para uso!**