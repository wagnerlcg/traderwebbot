# 🚀 GUIA COMPLETO - DEPLOY NO RENDER.COM

## ✅ **POR QUE RENDER.COM?**

- ✅ Python já instalado
- ✅ Deploy super fácil
- ✅ SSL grátis (HTTPS)
- ✅ Plano gratuito disponível
- ✅ Deploy automático via Git
- ✅ Logs em tempo real
- ✅ Restart automático

---

## 📋 **MÉTODO 1: DEPLOY VIA GITHUB (RECOMENDADO)**

### **PASSO 1: Criar conta no GitHub**
1. Acesse: https://github.com
2. Crie uma conta gratuita (se não tiver)
3. Confirme seu email

### **PASSO 2: Criar repositório**
1. Clique em "New repository"
2. Nome: `web-trader-bot-sinais`
3. Privado ✅ (para proteger suas credenciais)
4. Crie o repositório

### **PASSO 3: Fazer upload do código**

**Opção A - Via interface web (mais fácil):**
1. No repositório, clique em "uploading an existing file"
2. Arraste todos os arquivos do projeto
3. Commit changes

**Opção B - Via Git (se souber usar):**
```bash
cd C:\Users\conta\apps-python\web-trader-bot-sinais

# Inicializar Git
git init
git add .
git commit -m "Initial commit"

# Conectar ao GitHub
git remote add origin https://github.com/SEU-USUARIO/web-trader-bot-sinais.git
git branch -M main
git push -u origin main
```

### **PASSO 4: Criar conta no Render**
1. Acesse: https://render.com
2. Clique em "Get Started"
3. **"Sign up with GitHub"** (conectar com GitHub)
4. Autorize o Render a acessar seus repositórios

### **PASSO 5: Criar Web Service**
1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório `web-trader-bot-sinais`
4. Configure:
   - **Name:** web-trader-bot-sinais
   - **Region:** Oregon (US West) ou mais próximo
   - **Branch:** main
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_interface.py`
   - **Plan:** Free (para teste)

### **PASSO 6: Configurar Variáveis de Ambiente**
No Render, adicione as variáveis:
- `IQOPTION_EMAIL`: seu-email@iqoption.com
- `IQOPTION_SENHA`: sua-senha

### **PASSO 7: Deploy!**
1. Clique em "Create Web Service"
2. Aguarde o deploy (2-5 minutos)
3. Acesse a URL fornecida: `https://web-trader-bot-sinais.onrender.com`

---

## 📋 **MÉTODO 2: DEPLOY MANUAL (SEM GITHUB)**

### **PASSO 1: Criar conta no Render**
1. Acesse: https://render.com
2. Crie conta com email

### **PASSO 2: Usar Docker ou Blueprint**
(Mais complexo, recomendo Método 1)

---

## 🔧 **CONFIGURAÇÕES IMPORTANTES**

### **Modificar web_interface.py para Render:**

O Render fornece a porta via variável de ambiente. Atualize o arquivo:

```python
import os

# No final do arquivo, onde tem:
# socketio.run(app, debug=False, host='127.0.0.1', port=5000)

# Mudar para:
port = int(os.environ.get('PORT', 5000))
socketio.run(app, debug=False, host='0.0.0.0', port=port)
```

### **Criar .gitignore:**
```
__pycache__/
*.pyc
*.pyo
*.log
logs/*.log
config/credentials.json
.env
venv/
.venv/
```

### **Proteger credenciais:**
Não commit credenciais! Use variáveis de ambiente do Render.

---

## 🌐 **ACESSAR SUA APLICAÇÃO**

Depois do deploy:
- **URL:** `https://web-trader-bot-sinais.onrender.com`
- **Dashboard Render:** https://dashboard.render.com

---

## 📊 **MONITORAMENTO**

### Ver logs:
1. No dashboard do Render
2. Clique no seu serviço
3. Aba "Logs"

### Restart manual:
1. No dashboard
2. Clique em "Manual Deploy"
3. "Deploy latest commit"

---

## 💰 **PLANOS E PREÇOS**

### **Free (Gratuito):**
- ✅ 512MB RAM
- ✅ SSL grátis
- ⚠️ Dorme após 15 min de inatividade
- ⚠️ 750 horas/mês

### **Starter ($7/mês):**
- ✅ 512MB RAM
- ✅ Sempre ativo
- ✅ SSL grátis
- ✅ Deploy automático

### **Standard ($25/mês):**
- ✅ 2GB RAM
- ✅ Melhor performance
- ✅ Tudo do Starter

**Recomendo:** Começar no Free, depois migrar para Starter ($7/mês)

---

## 🚨 **PROBLEMAS COMUNS**

### **1. Build falhou**
- Verifique `requirements.txt`
- Verifique logs de build

### **2. App não inicia**
- Verifique porta (use variável PORT)
- Verifique logs

### **3. App dorme (plano Free)**
- Upgrade para Starter ($7/mês)
- Ou use serviço de "ping" para manter ativo

### **4. Credenciais não funcionam**
- Use variáveis de ambiente
- Não commit credenciais no Git

---

## 🔄 **ATUALIZAR APLICAÇÃO**

### Via Git:
```bash
# Fazer alterações no código
git add .
git commit -m "Atualização"
git push

# Render faz deploy automático!
```

### Via Dashboard:
1. Upload novos arquivos no GitHub
2. Render detecta e faz deploy automático

---

## ✅ **CHECKLIST DE DEPLOY**

- [ ] Criar conta no GitHub
- [ ] Criar repositório privado
- [ ] Upload do código (sem credenciais!)
- [ ] Criar conta no Render
- [ ] Conectar GitHub ao Render
- [ ] Criar Web Service
- [ ] Configurar variáveis de ambiente
- [ ] Verificar porta no código
- [ ] Deploy!
- [ ] Testar aplicação
- [ ] Configurar domínio (opcional)

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Criar conta GitHub** (se não tiver)
2. **Upload do código** no repositório privado
3. **Criar conta Render**
4. **Conectar e fazer deploy**
5. **Testar!**

---

## 📞 **SUPORTE**

- **Render Docs:** https://render.com/docs
- **GitHub Help:** https://docs.github.com

---

## 🎉 **VANTAGENS DO RENDER**

✅ **Deploy em 5 minutos**
✅ **Grátis para começar**
✅ **SSL automático**
✅ **Logs em tempo real**
✅ **Deploy automático via Git**
✅ **Fácil de usar**
✅ **Confiável**

**Status:** Pronto para deploy! 🚀

