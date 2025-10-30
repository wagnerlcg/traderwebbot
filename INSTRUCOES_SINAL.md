# 🤖 INSTRUÇÕES - POR QUE OS SINAIS NÃO ESTÃO SENDO EXECUTADOS

## ⚠️ **PROBLEMA IDENTIFICADO**

Os sinais não estão sendo enviados para a corretora porque:

### 1. **Horário Passado**
- Os sinais que você tentou foram para horários que **já passaram**
- O bot só executa em **horário futuro** (próximos minutos)
- Exemplo: Se agora são 06:50, um sinal para 06:43 **não será executado**

### 2. **Bot Já Iniciado**
- Se você alterar o arquivo `data/sinais.txt` **depois** que o bot iniciou
- O bot **não vai recarregar** os sinais automaticamente
- Ele lê os sinais **apenas na inicialização**

---

## ✅ **SOLUÇÃO - COMO FAZER FUNCIONAR**

### **NOVO SINAL CRIADO:**
```
M1;GBPAUD-OTC;06:52;CALL
```

### **PASSOS PARA EXECUTAR:**

#### **1. Interface Web (RECOMENDADO)**
1. Acesse: **http://localhost:3000**
2. Vá na aba **"Sinais"**
3. Clique em **"Ou cole o conteúdo aqui"**
4. Cole este conteúdo:
   ```
   M1;GBPAUD-OTC;06:52;CALL
   ```
5. Clique em **"Carregar Sinais"**
6. Clique em **"Iniciar Bot"** (se não estiver rodando)
7. Aguarde até **06:52**

#### **2. Reiniciar Bot**
Se o bot já está rodando:
1. **PARE** o bot na interface web
2. **INICIE** o bot novamente
3. O arquivo `data/sinais.txt` já está atualizado
4. Aguarde até **06:52**

---

## 📊 **FORMATO DOS SINAIS**

### **Formato Correto:**
```
M1;ATIVO;HH:MM;TIPO
```

### **Exemplo:**
```
M1;GBPAUD-OTC;06:52;CALL
```

### **Campos:**
- **M1**: Tempo em minutos (M1, M5, M15, M30)
- **GBPAUD-OTC**: Nome do ativo
- **06:52**: Horário (HH:MM em formato 24h)
- **CALL**: Tipo de ordem (CALL ou PUT)

---

## ⏰ **REGRAS IMPORTANTES**

1. **Hora Futura**: O sinal deve ser para um horário futuro
2. **Formato Correto**: Use exatamente o formato especificado
3. **Recarregar**: Sempre recarregue os sinais ou reinicie o bot
4. **Horário Sistema**: O bot usa o relógio do seu computador

---

## 🔍 **COMO VERIFICAR**

1. **Horário Atual do Sistema:**
   ```powershell
   Get-Date -Format "HH:mm:ss"
   ```

2. **Verificar Arquivo de Sinais:**
   ```powershell
   Get-Content data\sinais.txt
   ```

3. **Verificar Logs do Bot:**
   - Abra o terminal onde o bot está rodando
   - Procure por mensagens como "SINAL DEMO encontrado" ou "SINAL REAL encontrado"

---

## 📝 **CRIAR NOVOS SINAIS**

Para criar sinais para os próximos minutos, use este comando PowerShell:

```powershell
$agora = Get-Date
$proximaHora = $agora.AddMinutes(3)
$hora = $proximaHora.ToString("HH")
$minuto = $proximaHora.ToString("mm")
"M1;EURUSD-OTC;${hora}:${minuto};CALL" | Set-Content -Path "data\sinais.txt"
Write-Host "Sinal criado para ${hora}:${minuto}"
```

---

## ❓ **TROUBLESHOOTING**

### Bot não está executando sinais?
1. Verifique se o horário do sistema está correto
2. Certifique-se de que o sinal é para o futuro
3. Reinicie o bot após alterar o arquivo de sinais
4. Verifique os logs para erros

### Operação não foi executada?
1. Verifique se a hora/minuto correspondem exatamente
2. Verifique se o ativo está aberto (mercado aberto)
3. Verifique se não há proteções ativas (stop loss, pausas)
4. Verifique o saldo disponível

---

**Última atualização**: 28/10/2025 - 06:49
**Próximo sinal**: 06:52

