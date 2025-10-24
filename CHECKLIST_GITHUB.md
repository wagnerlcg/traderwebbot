# ✅ CHECKLIST - UPLOAD PARA GITHUB

## 📋 **ARQUIVOS OBRIGATÓRIOS**

Verifique se TODOS estes arquivos foram enviados para o GitHub:

### **Arquivos principais:**
- [ ] `web_interface.py`
- [ ] `requirements.txt` ⚠️ **MUITO IMPORTANTE!**
- [ ] `runtime.txt`
- [ ] `Procfile`
- [ ] `render.yaml`
- [ ] `.gitignore`
- [ ] `README.md`

### **Diretório bot/:**
- [ ] `bot/iqoption_bot.py`
- [ ] `bot/utils.py`
- [ ] `bot/estrategias.py`
- [ ] `bot/main.py`

### **Diretório web/:**
- [ ] `web/templates/index.html`
- [ ] `web/static/css/style.css`
- [ ] `web/static/js/app.js`

### **Diretório config/:**
- [ ] `config/credentials.json.example`
- [ ] ⚠️ **NÃO ENVIAR:** `config/credentials.json` (suas credenciais reais!)

### **Diretórios vazios (criar):**
- [ ] `data/` (pode estar vazio)
- [ ] `logs/` (pode estar vazio)
- [ ] `sounds/` (opcional)

---

## 🚫 **NÃO ENVIAR (já está no .gitignore):**

- ❌ `config/credentials.json` (suas credenciais!)
- ❌ `__pycache__/`
- ❌ `*.pyc`
- ❌ `logs/*.log`
- ❌ `.venv/`
- ❌ `venv/`

---

## 🔍 **VERIFICAR NO GITHUB:**

Depois de fazer upload, verifique se no seu repositório você vê:

```
web-trader-bot-sinais/
├── bot/
│   ├── iqoption_bot.py
│   ├── utils.py
│   ├── estrategias.py
│   └── main.py
├── web/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── config/
│   └── credentials.json.example
├── data/
├── logs/
├── web_interface.py
├── requirements.txt ← IMPORTANTE!
├── runtime.txt
├── Procfile
├── render.yaml
├── .gitignore
└── README.md
```

---

## ⚠️ **SE O RENDER DER ERRO:**

### **Erro: "Could not open requirements file"**

**Causa:** O arquivo `requirements.txt` não foi enviado para o GitHub.

**Solução:**
1. Verifique se o arquivo existe no seu computador
2. No GitHub, na página do repositório, procure `requirements.txt`
3. Se não existir, faça upload manualmente:
   - Clique em "Add file" → "Upload files"
   - Arraste o `requirements.txt`
   - Commit

### **Erro: "Module not found"**

**Causa:** Falta alguma dependência no `requirements.txt`.

**Solução:**
1. Verifique os logs do build no Render
2. Adicione a dependência faltante no `requirements.txt`
3. Commit no GitHub
4. Render faz redeploy automático

---

## 🔄 **REFAZER UPLOAD (se necessário):**

### **Método 1 - Adicionar arquivo faltante:**
1. No GitHub, no seu repositório
2. Clique em "Add file" → "Upload files"
3. Arraste o arquivo faltante
4. Commit changes
5. Render detecta e faz redeploy

### **Método 2 - Recriar repositório:**
1. Delete o repositório atual
2. Crie um novo
3. Faça upload de TODOS os arquivos de uma vez
4. Reconecte no Render

---

## 📝 **CONTEÚDO DO requirements.txt:**

Certifique-se que o arquivo contém (no mínimo):

```
pandas>=1.5.0
iqoptionapi>=4.3.0
python-dotenv>=0.19.0
flask>=2.3.0
flask-socketio>=5.3.0
eventlet>=0.33.0
```

---

## ✅ **TESTE LOCAL ANTES:**

Antes de fazer deploy, teste localmente:

```bash
pip install -r requirements.txt
python web_interface.py
```

Se funcionar localmente, funcionará no Render!

---

## 🆘 **AINDA COM PROBLEMAS?**

### Verificar arquivos no GitHub:
1. Acesse seu repositório no GitHub
2. Clique em cada arquivo para confirmar que existe
3. Especialmente: `requirements.txt`, `web_interface.py`, `Procfile`

### Verificar configuração no Render:
1. Dashboard do Render
2. Seu serviço
3. Settings → Build & Deploy
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python web_interface.py`

---

**Dica:** Faça upload de TODOS os arquivos de uma vez para evitar problemas! 📦

