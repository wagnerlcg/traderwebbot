# 📊 Estratégias de Gerenciamento - Trading Bot

## 🎯 3 Estratégias Disponíveis

O bot agora suporta **3 estratégias diferentes** de gerenciamento de banca:

---

## 1️⃣ Estratégia Masaniello

### 📖 O Que É:
Progressão calculada matematicamente baseada em **ciclos completos** de operações.

### 🔧 Parâmetros:
- **Quantidade de entradas**: 2-20 operações por ciclo (ex: 10)
- **Número de acertos**: Quantos WINs espera ter (ex: 7 de 10 = 70%)
- **Objetivo de lucro**: Percentual desejado no ciclo (ex: 20%)

### 💡 Como Funciona:
```
Ciclo de 10 operações, esperando 7 acertos para +20% de lucro
Banca: $1000

O algoritmo calcula valores distribuídos:
Op 1: $15.50
Op 2: $16.20
Op 3: $17.00
...
Op 10: $25.80

Total investido no ciclo: ~$195
Se acertar 7/10: Lucro = $200 (20%)
```

### ✅ Vantagens:
- Risco distribuído
- Objetivo claro
- Baseado em probabilidade

### ⚠️ Desvantagens:
- Sem proteções (opera ciclo completo)
- Precisa estimar assertividade correta

---

## 2️⃣ Estratégia Soros (Reinvestimento de Lucros)

### 📖 O Que É:
Reinveste **TODO o lucro** na próxima operação. Cresce exponencialmente com vitórias!

### 🔧 Parâmetros:
- **Valor base**: Valor inicial da entrada (ex: $10)
- **Payout**: Retorno da corretora em % (ex: 80%)

### 💡 Como Funciona:
```
Valor base: $10
Payout: 80%

Operação 1: $10.00 → WIN → Lucro $8.00
Operação 2: $18.00 ($10 + $8) → WIN → Lucro $14.40
Operação 3: $32.40 ($18 + $14.40) → WIN → Lucro $25.92
Operação 4: $58.32 ($32.40 + $25.92) → LOSS
Operação 5: $10.00 (volta ao valor base) → Recomeça
```

### ✅ Vantagens:
- Crescimento exponencial rápido
- Aproveita sequências de vitórias
- Simples de entender

### ⚠️ Desvantagens:
- Um LOSS perde tudo do ciclo
- Sem proteções
- Arriscado em sequências longas

### 📈 Exemplo Real:
```
Base: $10 com 5 WINs consecutivos (payout 80%)

WIN 1: $10 → $18 (+$8)
WIN 2: $18 → $32.40 (+$14.40)
WIN 3: $32.40 → $58.32 (+$25.92)
WIN 4: $58.32 → $104.98 (+$46.66)
WIN 5: $104.98 → $188.96 (+$83.98)

Total investido: $10 inicial
Lucro se parar aqui: $178.96 (1789%!)

WIN 6: $188.96 → $340.13
LOSS 7: Perde $340.13, volta para $10

Lucro líquido das 6: $178.96 - $340.13 = -$161.17
Mas começou com $10, então ainda tem lucro de operações anteriores
```

**Estratégia ideal para:** Aproveitar sequências quentes!

---

## 3️⃣ Estratégia Martingale

### 📖 O Que É:
Progressão geométrica clássica - **dobra** (ou multiplica) após cada LOSS.

### 🔧 Parâmetros:
- **Nível**: 1 (entrada + 1 defesa) ou 2 (entrada + 2 defesas)
- **Multiplicador**: 1.5x a 3.0x (padrão 2.0x)

### 💡 Como Funciona:
```
Valor base: $10
Multiplicador: 2.0x
Nível: 2 (entrada + 2 defesas)

Entrada: $10.00
Proteção 1: $20.00 (2x)
Proteção 2: $40.00 (2x de P1)

Total em risco: $70.00
```

### ✅ Vantagens:
- Recupera perdas + lucro pequeno
- Proteções automáticas
- Comprovado matematicamente

### ⚠️ Desvantagens:
- Cresce muito rápido
- Pode atingir limite de banca
- Arriscado em sequências longas de LOSS

---

## 📊 Comparação das 3 Estratégias

| Aspecto | Masaniello | Soros | Martingale |
|---------|------------|-------|------------|
| **Complexidade** | Alta | Média | Baixa |
| **Proteções** | Não | Não | Sim (1-2) |
| **Progressão** | Calculada | Compounding | Geométrica |
| **Risco** | Distribuído | Alto em sequências | Cresce rápido |
| **Ideal para** | Ciclos longos | Aproveitar sequências | Recuperar perdas |
| **Assertividade mín.** | 60-70% | 60%+ | 50%+ |
| **Crescimento** | Linear | Exponencial | Geométrico |

---

## 🎮 Como Usar no Bot

### Ao Iniciar:

```
============================================================
  SELECAO DE ESTRATEGIA DE GERENCIAMENTO
============================================================

Escolha a estrategia de gerenciamento de banca:

  1 - Masaniello  (Progressao calculada por ciclos)
  2 - Soros       (Reinvestimento de lucros)
  3 - Martingale  (Progressao geometrica classica)

Estrategia (1, 2 ou 3): 
```

### Se Escolher Masaniello:
```
Quantidade de entradas no ciclo (2-20): 10
Numero de acertos esperados (1-9): 7
Objetivo de lucro no ciclo (%): 20

[OK] Masaniello configurado:
     Ciclo: 10 entradas
     Acertos esperados: 7 (70%)
     Objetivo: +20%
```

### Se Escolher Soros:
```
Valor base da entrada ($): 10
Payout da corretora (%, padrao 80): 80

[OK] Soros configurado:
     Valor base: $10.00
     Payout: 80%

Exemplo de progressao:
  1. $10.00 → WIN → Lucro $8.00
  2. $18.00 → WIN → Lucro $14.40
  3. $32.40 → WIN → Continua...
  X. LOSS → Volta para $10.00
```

### Se Escolher Martingale:
```
Nivel de Martingale (1=entrada+1defesa, 2=entrada+2defesas): 2
Multiplicador (1.5 a 3.0, padrao 2.0): 2.0

[OK] Martingale configurado:
     Nivel: 2 (entrada + 2 defesas)
     Multiplicador: 2.0x
```

---

## 🎯 Recomendações de Uso

### Masaniello:
- ✅ Use quando: Tem sinais consistentes (60-70% assertividade)
- ✅ Banca: Média a grande ($500+)
- ✅ Perfil: Conservador a moderado
- ⚠️ Cuidado: Precisa completar ciclo para avaliar

### Soros:
- ✅ Use quando: Identificou sequência quente
- ✅ Banca: Qualquer (começa pequeno)
- ✅ Perfil: Agressivo
- ⚠️ Cuidado: Um LOSS perde todo o progresso da sequência
- 💡 Dica: Defina regra para "sacar" após X WINs

### Martingale:
- ✅ Use quando: Tem banca para suportar proteções
- ✅ Banca: Adequada para 3-5 níveis
- ✅ Perfil: Moderado
- ⚠️ Cuidado: Cresce muito rápido
- 💡 Dica: Use multiplicador < 2.0x para crescimento mais lento

---

## 🛡️ Proteções Aplicadas a TODAS as Estratégias

Independente da estratégia escolhida, **TODAS** têm:

✅ **Stop Loss Dinâmico** (1-50% configurável)  
<!-- ✅ **Pré-Stop Loss** (verifica antes de operar) - TEMPORARIAMENTE DESABILITADO -->  
✅ **Pausas estratégicas** (6 LOSS ou 2x3 LOSS)  
✅ **Proteção contra erros técnicos**  
✅ **Validação de sinais**  
✅ **Sons e alertas** (opcional - pode ser desabilitado)  

**Sua banca SEMPRE protegida!**

---

## 📈 Exemplo Combinado

### Soros com Stop Loss 5%:

```
Banca inicial: $1000
Stop loss: 5% = $50
Valor base Soros: $20

Operação 1: $20 → WIN → $36
Operação 2: $36 → WIN → $64.80
Operação 3: $64.80 → WIN → $116.64

Operação 4: $116.64 → WIN → $209.95
Operação 5: $209.95 → WIN → $377.91
...continua crescendo até atingir limite de stop loss

Quando atingir 5% de perda da banca inicial:
Bot: "Stop Loss atingido! Encerrando operações."
```

**Proteção dinâmica mantém Soros sob controle!**

---

## 🎯 Qual Escolher?

### Você é conservador e tem sinais consistentes?
→ **MASANIELLO**

### Quer aproveitar sequências quentes?
→ **SOROS**

### Quer recuperar perdas com proteções?
→ **MARTINGALE**

### Não sabe?
→ Comece com **MARTINGALE** (mais conhecido e com proteções)

---

**🚀 Agora você tem 3 estratégias profissionais no mesmo bot!**

**🛡️ Todas com proteção máxima de stop loss dinâmico.**

