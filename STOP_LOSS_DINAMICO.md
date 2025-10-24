# 📊 Stop Loss Dinâmico - Explicação Completa

## 🎯 O Que Mudou?

### Antes (Stop Loss Fixo):
```
Banca inicial: $1000
Stop loss: 10% = $100 fixo
Podia perder: $100 no total
```

### Agora (Stop Loss Dinâmico):
```
Você escolhe: 1% a 10%
Recalcula: A cada operação baseado no saldo ATUAL
Limite: Sempre X% do saldo atual
```

---

## 💡 Como Funciona o Dinâmico

### Conceito:

**O bot limita cada operação individual a X% do saldo ATUAL**, não a perda total acumulada.

**Isso significa:**
- ✅ Você pode arriscar até X% por operação
- ✅ Limite se ajusta conforme banca muda
- ✅ Proteção cresce quando você lucra
- ✅ Proteção diminui quando você perde

---

## 📈 Exemplo Prático - Banca Crescente

### Configuração:
- Stop Loss: 10%
- Banca inicial: $1000

### Operações:

```
Operação 1:
Saldo atual: $1000
Limite por operação: $100 (10% de $1000)
Entrada: $50 ✅ (dentro do limite)
Resultado: WIN +$90
Novo saldo: $1090

Operação 2:
Saldo atual: $1090 ← AUMENTOU!
Limite por operação: $109 (10% de $1090) ← CRESCEU!
Entrada: $55 ✅
Resultado: WIN +$100
Novo saldo: $1190

Operação 3:
Saldo atual: $1190
Limite por operação: $119 (10% de $1190) ← CRESCEU MAIS!
Entrada: $60 ✅
```

**Vantagem:** Conforme você LUCRA, pode arriscar MAIS (em reais)!

---

## 📉 Exemplo Prático - Banca Decrescente

### Configuração:
- Stop Loss: 10%
- Banca inicial: $1000

### Operações:

```
Operação 1:
Saldo atual: $1000
Limite por operação: $100 (10% de $1000)
Entrada: $80, P1: $160 ✅
Resultado: LOSS total -$240
Novo saldo: $760

Operação 2:
Saldo atual: $760 ← DIMINUIU!
Limite por operação: $76 (10% de $760) ← REDUZIU!
Entrada programada: $80 ❌
PRE-STOP: $80 > $76 → BLOQUEADO!

Bot para antes de operar!
Perda total: $240 (24% da inicial)
Mas última operação RESPEITOU os 10% do saldo atual ($760)
```

**Proteção:** Conforme você PERDE, arrisca MENOS automaticamente!

---

## 🎯 Comparação Detalhada

### Stop Loss FIXO (antigo):

| Banca | Perda Acum. | Limite | Pode Arriscar |
|-------|-------------|--------|---------------|
| $1000 | $0 | $100 | $100 |
| $1000 | $50 | $100 | $50 |
| $1000 | $90 | $100 | $10 |
| $1000 | $99 | $100 | $1 |

Problema: Não considera que já perdeu, mas limite é fixo.

### Stop Loss DINÂMICO (atual):

| Banca Inicial | Saldo Atual | Limite (10%) | Pode Arriscar |
|---------------|-------------|--------------|---------------|
| $1000 | $1000 | $100 | $100 |
| $1000 | $1200 | $120 | $120 ⬆️ AUMENTOU! |
| $1000 | $800 | $80 | $80 ⬇️ DIMINUIU! |
| $1000 | $500 | $50 | $50 ⬇️ PROTEÇÃO! |

Vantagem: Se ajusta automaticamente!

---

## 🔄 Recalculo Automático

### A cada operação:

```python
# 1. Obtém saldo atual
saldo_atual = Iq.get_balance()

# 2. Calcula limite dinâmico
limite = saldo_atual * (stop_loss_percentual / 100)

# 3. Verifica antes de operar
if valor_operacao > limite:
    BLOQUEIA
else:
    EXECUTA
```

### Status periódico (a cada 10 minutos):

```
[Status] Saldo: $1150.00 | Variacao: +15.00% | Perda contabilizada: $0.00
[Status] Saldo: $950.00 | Variacao: -5.00% | Perda contabilizada: $50.00
```

---

## ⚙️ Configuração do Stop Loss

### Opção 1: Via Parâmetro
```bash
python -m bot.main --mode demo --sinais data.txt --stop-loss 5
```
- Define 5% de stop loss
- Não solicita input

### Opção 2: Via Input (Padrão)
```bash
python -m bot.main --mode demo --sinais data.txt
```

O bot solicita:
```
============================================================
  CONFIGURACAO DE STOP LOSS
============================================================

Defina o percentual maximo de perda permitido.
Valor deve estar entre 1% e 10% da banca.

Stop Loss (%): 7

[OK] Stop loss configurado: 7%
```

### Validação Automática:
```
Stop Loss (%): 15
[ERRO] Stop loss de 15% invalido!
Deve estar entre 1% e 10%. Usando padrao de 10%
```

---

## 💎 Exemplos de Estratégias

### Conservador (1-3%):
```
--stop-loss 2

Banca: $10,000
Limite por operação: $200
Proteção máxima
Ideal para: Iniciantes, contas grandes
```

### Moderado (5-7%):
```
--stop-loss 5

Banca: $1,000
Limite por operação: $50
Equilíbrio risco/retorno
Ideal para: Traders intermediários
```

### Agressivo (8-10%):
```
--stop-loss 10

Banca: $500
Limite por operação: $50
Maior risco, maior recuperação
Ideal para: Experts, contas pequenas
```

---

## 🛡️ Dupla Proteção

### 1. PRÉ-STOP (Por Operação):
```
Pode arriscar este valor AGORA?
valor <= (saldo_atual * X%)
```

### 2. STOP LOSS (Global):
```
Já perdi X% do total?
((saldo_inicial - saldo_atual) / saldo_inicial) >= X%
```

**Ambos trabalham juntos!**

---

## 📊 Cenário Completo

### Configuração:
- Banca inicial: $1000
- Stop loss: 10%
- Sinais com martingale

### Evolução:

```
Início:
Saldo: $1000 | Limite: $100/operação

Operação 1: $50 → WIN +$90
Saldo: $1090 | Limite: $109/operação ⬆️

Operação 2: $60 → WIN +$108
Saldo: $1198 | Limite: $119.80/operação ⬆️

Operação 3: $70, P1: $140 → LOSS total -$210
Saldo: $988 | Limite: $98.80/operação ⬇️

Operação 4: Programada $100
PRE-CHECK: $100 > $98.80 ❌
BLOQUEADO! Bot encerra.

Perda global: 1.2% da inicial ($12)
Mas operação individual respeitou 10% do saldo atual!
```

---

## 🎯 Resumo das Vantagens

| Aspecto | Fixo | Dinâmico |
|---------|------|----------|
| **Limite em $** | Não muda | Muda com saldo |
| **Quando cresce** | Fixo | Aumenta limite |
| **Quando diminui** | Fixo | Diminui limite |
| **Proteção** | Absoluta | Proporcional |
| **Flexibilidade** | Baixa | Alta |
| **Segurança** | Boa | Excelente |

---

## ⚠️ Importante Entender

### O stop loss dinâmico protege:
✅ Cada operação individualmente (máximo X% do saldo atual)  
✅ Perda global (para se cair X% do inicial)  

### Não confundir:
❌ Não é "perda acumulada máxima"  
❌ Não é "quanto pode perder no total"  
✅ É "quanto pode arriscar POR OPERAÇÃO baseado no saldo ATUAL"  

---

## 📚 Documentação Relacionada

- [SEGURANCA.md](SEGURANCA.md) - Detalhes técnicos
- [GUIA_COMPLETO.md](GUIA_COMPLETO.md) - Funcionamento geral
- [README.md](README.md) - Documentação completa

---

**🔄 Stop loss que cresce quando você ganha e protege quando você perde!**

**🛡️ Inteligente. Dinâmico. Seguro.**

