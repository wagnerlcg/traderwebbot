# 🔄 INSTRUÇÕES DE RESTAURAÇÃO - TRADER BOT

## 📦 Backups Disponíveis

### **Backup 1 (Básico)**
- **Arquivo**: `TraderBot_Backup_2025-10-24_17-22-54.zip`
- **Tamanho**: 43.01 MB
- **Conteúdo**: Código fonte completo do projeto

### **Backup 2 (Completo)**
- **Arquivo**: `TraderBot_Complete_Backup_2025-10-24_17-27-37.zip`
- **Tamanho**: 43.01 MB
- **Conteúdo**: Código fonte + arquivo de informações

---

## 🚀 Como Restaurar o Sistema

### **Passo 1: Preparar Ambiente**
```bash
# Criar diretório para o projeto
mkdir TraderBot
cd TraderBot

# Extrair o backup
# (Extrair o arquivo ZIP para esta pasta)
```

### **Passo 2: Configurar Ambiente Python**
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **Passo 3: Configurar Banco de Dados**
```bash
# O banco será criado automaticamente na primeira execução
# Não é necessário configuração adicional
```

### **Passo 4: Executar Sistema**
```bash
# Iniciar interface web
python web_interface.py

# Ou usar o script de inicialização
INICIAR-SIMPLES.bat
```

### **Passo 5: Acessar Interface**
- **URL**: http://localhost:5000
- **Usuário**: usuario@exemplo.com
- **Senha**: 123456

---

## ⚙️ Configurações Importantes

### **Arquivo de Sinais**
- **Localização**: `data/sinais.txt`
- **Formato**: `M5;PAR;HORA;DIREÇÃO`
- **Exemplo**: `M5;EURUSD-OTC;16:00;PUT`

### **Configurações do Bot**
- **Stop Loss**: 10% (configurável)
- **Stop Win**: 20% (configurável)
- **Estratégias**: Valor Fixo, Masaniello, Martingale, Soros

### **Logs**
- **Localização**: `logs/`
- **Arquivo principal**: `logs/bot_web.log`

---

## 🔧 Solução de Problemas

### **Erro de Dependências**
```bash
# Reinstalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### **Erro de Porta**
```bash
# Se a porta 5000 estiver ocupada, alterar em web_interface.py
# Linha final: app.run(host='127.0.0.1', port=5000)
```

### **Erro de Conexão IQ Option**
- Verificar credenciais na interface web
- Testar primeiro em modo DEMO
- Verificar conexão com internet

---

## 📊 Status do Sistema no Backup

### ✅ **Funcionalidades Testadas e Funcionando:**
- ✅ Interface web responsiva
- ✅ Autenticação de usuários
- ✅ Conexão com IQ Option (Demo/Real)
- ✅ Carregamento de sinais (17 sinais válidos)
- ✅ Execução de operações binárias
- ✅ Atualizações em tempo real via WebSocket
- ✅ Saldo atual: $13,924.87
- ✅ Sistema de estratégias completo
- ✅ Proteções (Stop Loss, Stop Win)
- ✅ Logs detalhados

### 🎯 **Problemas Resolvidos:**
- ✅ Erro EOF em modo web
- ✅ Erro de formatação com estratégia Valor Fixo
- ✅ Problemas de Unicode/Emoji no Windows
- ✅ Thread de parada do bot

---

## 🎉 **SISTEMA 100% FUNCIONAL!**

Este backup contém um sistema de trading automatizado completamente funcional e testado. Todas as funcionalidades principais estão operacionais e prontas para uso.

**Data do Backup**: 24/10/2025 17:22
**Status**: ✅ COMPLETAMENTE FUNCIONAL
