# 🛡️ Documentação de Segurança - Trading Bot

## ⚠️ GARANTIAS DE SEGURANÇA FINANCEIRA

Este documento detalha **TODAS** as proteções implementadas para garantir que o bot **NUNCA** ultrapasse o limite de 10% de perda.

---

## 🚨 PRIORIDADE MÁXIMA: Stop Loss de 10%

### Sistema de Dupla Verificação:

#### 1. PRÉ-STOP LOSS (Verificação Preventiva)
**Executa ANTES de cada operação**

```python
# Antes de CADA entrada (principal, P1, P2):
seguro = verificar_seguranca_operacao(valor, perda_acumulada, saldo_inicial, 10%)

if not seguro:
    # NÃO EXECUTA A OPERAÇÃO
    # Encerra ou pula a entrada
```

**Quando verifica:**
- ✅ Antes da Entrada Principal
- ✅ Antes da Proteção 1
- ✅ Antes da Proteção 2

**O que verifica:**
```
Se (perda_acumulada + valor_operacao) > (saldo_inicial * 10%):
    → NÃO EXECUTA
```

#### 2. STOP LOSS PÓS-OPERAÇÃO (Verificação Reativa)
**Executa APÓS cada operação**

```python
# Após cada resultado:
if perda_acumulada >= (saldo_inicial * 10%):
    # PARA O BOT IMEDIATAMENTE
```

---

## 📋 Fluxo de Segurança Detalhado

### Entrada Principal:

```
1. [PRE-CHECK] Verifica: (perda_atual + valor_entrada) ≤ 10% ?
   ├─ SIM → Prossegue
   └─ NÃO → ENCERRA BOT (não executa)

2. Executa operação

3. [POST-CHECK] Verifica: perda_acumulada ≥ 10% ?
   ├─ SIM → ENCERRA BOT
   └─ NÃO → Continua
```

### Proteção 1:

```
1. [PRE-CHECK] Verifica: (perda_atual + protecao1) ≤ 10% ?
   ├─ SIM → Prossegue
   └─ NÃO → PULA P1 (contabiliza só entrada principal)

2. Executa proteção 1

3. [POST-CHECK] Verifica: perda_acumulada ≥ 10% ?
   ├─ SIM → ENCERRA BOT
   └─ NÃO → Continua
```

### Proteção 2:

```
1. [PRE-CHECK] Verifica: (perda_atual + entrada + P1 + protecao2) ≤ 10% ?
   ├─ SIM → Prossegue
   └─ NÃO → PULA P2 (contabiliza entrada + P1)

2. Executa proteção 2

3. [POST-CHECK] Verifica: perda_acumulada ≥ 10% ?
   ├─ SIM → ENCERRA BOT
   └─ NÃO → Continua
```

---

## 🔒 Garantias Implementadas

### ✅ IMPOSSÍVEL ultrapassar 10%

**Por quê?**
1. **Verificação dupla**: Antes E depois de cada operação
2. **Cálculo preventivo**: Considera o "pior cenário" antes de arriscar
3. **Bloqueio imediato**: Não permite operações que ultrapassariam
4. **Contadores separados**: Não confunde erro técnico com LOSS

### ✅ Verificações em TODOS os pontos críticos

- Entrada principal (linha ~208)
- Proteção 1 (linha ~242)
- Proteção 2 (linha ~276)
- Loop principal após operação (linha ~156)

### ✅ Logs transparentes

Cada operação mostra o limite disponível:
```
>>> ENTRADA PRINCIPAL: $50.00 [Limite disponivel: $75.50]
```

---

## 📊 Exemplos de Cenários

### Cenário 1: Entrada Principal Segura

```
Banca: $1000
Perda acumulada: $50
Limite de 10%: $100
Entrada: $30

PRE-CHECK: $50 + $30 = $80 ≤ $100 ✅
→ EXECUTA
```

### Cenário 2: Entrada Principal Bloqueada

```
Banca: $1000
Perda acumulada: $95
Limite de 10%: $100
Entrada: $20

PRE-CHECK: $95 + $20 = $115 > $100 ❌
→ NÃO EXECUTA - ENCERRA BOT
LOG: "!!! PRE-STOP LOSS ATIVADO !!!"
```

### Cenário 3: Proteção 1 Bloqueada

```
Banca: $1000
Perda acumulada: $60
Entrada principal: $15 (LOSS)
Proteção 1: $50
Limite: $100

Após entrada LOSS: $60 + $15 = $75
PRE-CHECK P1: $75 + $50 = $125 > $100 ❌
→ PULA P1
→ Contabiliza apenas $15 da entrada
→ Continua operando
```

### Cenário 4: Proteção 2 Bloqueada

```
Banca: $1000
Perda acumulada: $50
Entrada: $20 (LOSS)
P1: $30 (LOSS)
P2: $60
Limite: $100

Após entrada+P1: $50 + $20 + $30 = $100
PRE-CHECK P2: $100 + $60 = $160 > $100 ❌
→ PULA P2
→ Contabiliza $50 (entrada + P1)
→ Perda total: $100 (exatamente no limite)
```

---

## 🎯 Ordem de Prioridade das Proteções

1. **🚨 PRÉ-STOP LOSS** (Mais prioritário)
   - Verifica ANTES de arriscar dinheiro
   - Bloqueia operações perigosas

2. **🛑 STOP LOSS PÓS-OPERAÇÃO**
   - Verifica DEPOIS de cada resultado
   - Encerra se ultrapassar

3. **⏸️ PAUSAS ESTRATÉGICAS**
   - 6 LOSS ou 2 conjuntos de 3 LOSS
   - Pausa 2 sinais, zera contadores

4. **⏹️ OUTROS**
   - Término automático
   - Parada manual

---

## ✅ Checklist de Segurança

- [x] Verificação ANTES de cada operação
- [x] Verificação DEPOIS de cada operação
- [x] Cálculo correto do pior cenário
- [x] Bloqueio de entradas que ultrapassariam limite
- [x] Logs claros com limite disponível
- [x] Erros técnicos NÃO contam como LOSS
- [x] Dupla proteção (pré + pós)
- [x] Implementado em DEMO e REAL
- [x] Alerta sonoro ao atingir limites

---

## 🔍 Onde Está Implementado

### Arquivo: `bot/utils.py`
- Linha ~226: `verificar_seguranca_operacao()` - Função de pré-verificação
- Linha ~370: `tocar_som()` - Som de entrada
- Linha ~417: `tocar_som('win')` - Som de vitória
- Linha ~421: `tocar_som('loss')` - Som de perda

### Arquivo: `bot/iqoption_bot.py`

**Modo DEMO:**
- Linha ~156: Verificação pós-operação (loop principal)
- Linha ~208: Pré-verificação entrada principal
- Linha ~242: Pré-verificação proteção 1
- Linha ~276: Pré-verificação proteção 2

**Modo REAL:**
- Linha ~481: Verificação pós-operação (loop principal)
- Linha ~533: Pré-verificação entrada principal
- Linha ~567: Pré-verificação proteção 1
- Linha ~601: Pré-verificação proteção 2

---

## ⚠️ IMPORTANTE

### O bot NUNCA ultrapassará 10% porque:

1. **Calcula antes**: Verifica o pior cenário ANTES de arriscar
2. **Bloqueia preventivamente**: Não executa operações perigosas
3. **Verifica depois**: Confirma após cada resultado
4. **Dupla camada**: Pré + Pós verificação
5. **Logs transparentes**: Mostra limite disponível em tempo real

### Em caso de dúvida:

**O bot SEMPRE escolhe a segurança:**
- Dúvida se ultrapassaria? **NÃO OPERA**
- Próximo da proteção 1 arriscada? **PULA P1**
- Proteção 2 perigosa? **PULA P2**

**Prioridade: PRESERVAR CAPITAL > Recuperar perdas**

---

## 📞 Contato

Se encontrar qualquer situação onde o bot ultrapassou 10%, documente:
- Logs completos (`logs/bot.log`)
- Arquivo de sinais usado
- Valores exatos de saldo inicial e final

Isso NÃO DEVE acontecer com as proteções implementadas.

