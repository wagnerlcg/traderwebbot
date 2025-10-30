# 🌐 COMO USAR A INTERFACE WEB

## ✅ **BOT FUNCIONANDO!**

O bot está **100% funcional** e pode ser usado **inteiramente pela interface web**, sem precisar usar o terminal.

---

## 📋 **COMO ADICIONAR SINAIS PELA INTERFACE WEB**

### **Método 1: Colar Sinais**
1. Acesse a aba **"Sinais"** na interface web
2. Cole o conteúdo dos sinais no campo de texto
3. Clique em **"Carregar Sinais"**

### **Método 2: Upload de Arquivo**
1. Acesse a aba **"Sinais"**
2. Clique em **"Enviar Arquivo"**
3. Selecione o arquivo `sinais.txt`
4. Clique em **"Carregar Sinais"**

---

## 🎯 **COMO CRIAR UM SINAL DE TESTE**

### **Formato do Sinal:**
```
M1;ATIVO;HH:MM;TIPO
```

### **Exemplo:**
```
M1;EURUSD-OTC;10:30;CALL
```

### **Campos:**
- **M1/M5/M15/M30**: Timeframe (1, 5, 15 ou 30 minutos)
- **ATIVO**: Par de moedas (EURUSD-OTC, GBPUSD-OTC, etc.)
- **HH:MM**: Hora (ex: 10:30)
- **TIPO**: CALL (compra) ou PUT (venda)

---

## 🚀 **PASSO A PASSO COMPLETO**

### **1. Adicionar Sinais**
1. Abra a interface web: `http://localhost:3000`
2. Faça login
3. Vá na aba **"Sinais"**
4. Cole o sinal no campo de texto:
   ```
   M1;EURUSD-OTC;10:35;CALL
   ```
5. Clique em **"Carregar Sinais"**

### **2. Configurar Bot**
1. Vá na aba **"Configurações"**
2. Defina:
   - Stop Loss: 10%
   - Stop Win: 20%
   - Estratégia: Martingale ou Valor Fixo
   - Valor de Entrada: $10.00
3. Salve as configurações

### **3. Iniciar Bot**
1. Vá na aba **"Dashboard"**
2. Clique em **"Iniciar Bot"**
3. Aguarde o bot executar o sinal na hora configurada

### **4. Parar Bot**
1. Clique em **"Parar Bot"** quando quiser encerrar

---

## 📊 **MONITORAMENTO EM TEMPO REAL**

A interface web atualiza automaticamente:
- ✅ **Saldo** da conta
- ✅ **Quantidade de sinais** executados
- ✅ **WINs** e **LOSSes**
- ✅ **Logs** em tempo real
- ✅ **Status WebSocket** (conexão)

---

## ⚠️ **IMPORTANTE**

### **Horário do Sinal:**
- O sinal deve ser para um horário **FUTURO**
- Se o horário já passou, o bot vai finalizar imediatamente
- Exemplo: Se for 10:30, crie sinal para 10:33 ou depois

### **Ativos Disponíveis:**
- Nem todos os ativos estão sempre disponíveis
- Alguns podem estar **fechados** em determinados horários
- Ativos recomendados:
  - ✅ EURUSD-OTC
  - ✅ GBPUSD-OTC
  - ✅ USDJPY-OTC
  - ❌ GBPAUD-OTC (pode estar fechado)

---

## 🎉 **SUCESSO!**

O bot está **100% funcional** e pode ser controlado **inteiramente pela interface web**!

**Data**: 28/10/2025
**Status**: ✅ FUNCIONANDO

