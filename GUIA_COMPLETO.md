# 📘 Trading Bot - Guia Completo de Funcionamento

## 🎯 Visão Geral

O **Trading Bot** é um sistema automatizado de operações em opções binárias desenvolvido para a plataforma IQ Option. Ele executa operações baseadas em sinais programados, com sistema completo de proteções financeiras e gerenciamento de risco.

---

## 🚀 Principais Características

### ✅ O que o Bot FAZ:

1. **Executa operações automaticamente** nos horários programados
2. **Sistema de Martingale** com até 2 proteções por operação
3. **Proteção financeira rigorosa** - impossível perder mais de 10% da banca
4. **Validação completa** dos sinais antes de iniciar
5. **Pausas estratégicas** após sequências de perdas
6. **Sons personalizados** para cada evento (entrada, win, loss)
7. **Alertas sonoros** quando o bot para
8. **Término automático** após executar todos os sinais
9. **Logs detalhados** de todas as operações
10. **Executável Windows** - não precisa instalar Python

---

## 📋 Como Funciona - Passo a Passo

### 1️⃣ Preparação

**Você cria um arquivo de sinais** no formato:
```
M5;EURUSD-OTC;19:30;CALL;2.0;4.0;8.0
```

Onde cada campo significa:
- **M5** = Tempo da operação (1, 5, 15 ou 30 minutos)
- **EURUSD-OTC** = Ativo/par de moedas
- **19:30** = Horário de entrada (formato 24h)
- **CALL** = Direção (CALL=compra, PUT=venda)
- **2.0** = Valor da entrada principal (obrigatório)
- **4.0** = Valor da 1ª proteção - opcional
- **8.0** = Valor da 2ª proteção - opcional

### 2️⃣ Validação Automática

**ANTES de iniciar**, o bot valida **TODOS os sinais**:

✅ Arquivo existe  
✅ Formato correto  
✅ Tempos válidos (M1, M5, M15, M30)  
✅ Horários válidos (00:00 a 23:59)  
✅ Tipos válidos (PUT ou CALL)  
✅ Valores positivos  
✅ Pelo menos um sinal válido  

**Se encontrar QUALQUER erro:**
- ❌ Mostra todos os erros com número da linha
- 🔊 Emite alerta sonoro
- 🛑 **NÃO INICIA** o bot
- 📝 Você corrige e reinicia

### 3️⃣ Inicialização

Ao iniciar, o bot:

1. **Conecta na IQ Option** (conta DEMO ou REAL)
2. **Captura o saldo inicial** da conta
3. **Calcula o limite de 10%** (ex: $1000 → limite de $100)
4. **Exibe todas as proteções ativas**:
   ```
   === PROTECOES ATIVADAS ===
   Pausa apos 6 LOSS consecutivos: Pula 2 sinais
   Pausa apos 2 conjuntos de 3 LOSS: Pula 2 sinais
   Stop Loss Percentual: 10.0% da banca ($100.00)
   ==========================
   ```
5. **Lista TODOS os sinais** que serão executados:
   ```
   === SINAIS PROGRAMADOS (28) ===
    1. 19:52 | EURUSD-OTC | CALL | M1 | Entrada: $41.25 | P1: $70.08 | P2: $111.62
    2. 19:58 | EURJPY-OTC | PUT  | M1 | Entrada: $41.25 | P1: $70.08 | P2: $111.62
   ...
   ```

### 4️⃣ Execução de Operações

Para cada sinal programado:

#### **Passo 1: Pré-Verificação de Segurança (CRÍTICO)**

```
PRE-CHECK: Posso arriscar este valor sem ultrapassar 10%?
├─ SIM → Prossegue
└─ NÃO → BLOQUEIA (encerra ou pula)
```

**Exemplo:**
```
>>> ENTRADA PRINCIPAL: $50.00 [Limite disponivel: $75.50]
```
- Mostra quanto ainda pode perder

#### **Passo 2: Execução da Entrada Principal**

1. 🔊 Emite **beep de entrada** (curto e agudo)
2. 📊 Captura saldo antes da ordem
3. 🎯 Envia ordem para a corretora
4. ⏱️ Aguarda o tempo da operação (M1 = 1 min, M5 = 5 min, etc)
5. 💰 Captura saldo após a ordem
6. 📈 Calcula resultado (diferença de saldo)

#### **Passo 3: Resultado da Entrada**

**Se der WIN:**
- ✅ Som de vitória (caixa registradora: Dó→Mi→Sol)
- 📊 Mostra lucro
- 🔄 Zera todos os contadores
- ✔️ **Operação finalizada** (não executa proteções)

**Se der ERRO TÉCNICO:**
- ⚠️ Identifica o erro (ex: ativo não disponível)
- 📝 Loga: "[!] ERRO TECNICO - Nao conta como LOSS"
- 🔄 **Mantém contadores** (não incrementa)
- ✔️ **Operação finalizada** (não executa proteções)

**Se der LOSS:**
- ❌ Som de perda (notas descendentes)
- 📊 Mostra prejuízo
- ⏭️ **Executa Proteção 1** (se configurada)

#### **Passo 4: Proteção 1 (se necessária)**

1. 🔍 **PRÉ-VERIFICAÇÃO**: Pode executar P1 sem ultrapassar 10%?
   - **NÃO** → Pula P1, contabiliza só a entrada
   - **SIM** → Continua

2. 🔊 Beep de entrada
3. 📊 Executa P1 com valor configurado
4. ⏱️ Aguarda resultado

**Resultado P1:**
- **WIN** → 🎉 Som de vitória, zera contadores, **finaliza**
- **ERROR** → ⚠️ Não conta, mantém contadores, **finaliza**
- **LOSS** → ❌ Som de perda, **executa P2**

#### **Passo 5: Proteção 2 (se necessária)**

1. 🔍 **PRÉ-VERIFICAÇÃO**: Pode executar P2 sem ultrapassar 10%?
   - **NÃO** → Pula P2, contabiliza entrada + P1
   - **SIM** → Continua

2. 🔊 Beep de entrada
3. 📊 Executa P2 com valor configurado
4. ⏱️ Aguarda resultado

**Resultado P2:**
- **WIN** → 🎉 Som de vitória, zera contadores
- **ERROR** → ⚠️ Não conta, mantém contadores
- **LOSS** → ❌ Som de perda, contabiliza tudo

#### **Passo 6: Contabilização Final**

Após finalizar a operação completa (com ou sem proteções):

```python
if RESULTADO_FINAL == "LOSS":
    loss_consecutivos += 1
    perda_acumulada += prejuízo_total
    
    # Verificar conjunto de 3
    if loss_consecutivos % 3 == 0:
        conjuntos_3_loss += 1
    
    # Verificar se precisa pausar
    if loss_consecutivos >= 6:
        PAUSA 2 sinais
    elif conjuntos_3_loss >= 2:
        PAUSA 2 sinais
```

---

## 🛡️ Sistema de Proteções (Resumo Completo)

### Nível 1: Proteção por Operação (Martingale)

**Objetivo:** Recuperar perdas individuais

- Entrada Principal: $X
- Se LOSS → Proteção 1: $Y (geralmente 2X)
- Se LOSS → Proteção 2: $Z (geralmente 4X)

**Exemplo:**
```
Entrada: $2.00 → LOSS
Proteção 1: $4.00 → WIN (recupera $2 perdidos + lucro)
```

### Nível 2: Pausa Estratégica

**Objetivo:** Evitar operar em momentos ruins

**Regra A: 6 LOSS consecutivos**
```
LOSS → LOSS → LOSS → LOSS → LOSS → LOSS
→ PAUSA: Pula próximos 2 sinais
→ Ao voltar: Zera contadores
```

**Regra B: 2 Conjuntos de 3 LOSS**
```
LOSS → LOSS → LOSS [Conjunto 1]
LOSS → LOSS → LOSS [Conjunto 2]
→ PAUSA: Pula próximos 2 sinais
→ Ao voltar: Zera contadores
```

Durante a pausa:
```
[PAUSA] Pulando sinal por seguranca. Sinais restantes: 2
[PAUSA] Pulando sinal por seguranca. Sinais restantes: 1
[PAUSA] Fim da pausa. Zerando contadores e voltando a operar...
```

### Nível 3: PRÉ-STOP LOSS (Segurança Máxima)

**Objetivo:** NUNCA ultrapassar 10%

**Verifica ANTES de CADA entrada:**

```
Pode arriscar sem ultrapassar 10%?
├─ SIM → Executa
└─ NÃO → BLOQUEIA
```

**Ações de bloqueio:**
- **Entrada Principal** perigosa → Encerra bot
- **Proteção 1** perigosa → Pula P1, contabiliza entrada
- **Proteção 2** perigosa → Pula P2, contabiliza entrada+P1

### Nível 4: STOP LOSS Final (Barreira Final)

**Objetivo:** Garantia absoluta

**Verifica DEPOIS de cada operação:**
```
if perda_acumulada >= 10% do saldo inicial:
    → ENCERRA BOT PERMANENTEMENTE
    → Alerta sonoro (5 beeps longos)
```

### Nível 5: Proteção contra Erros Técnicos

**Não conta como LOSS:**
- Ativo não disponível
- Falha de conexão
- Ordem rejeitada
- Qualquer erro que impeça execução

**Conta como LOSS:**
- Operação executada e finalizada com prejuízo

---

## 🔊 Sistema de Sons

### Durante Operações:

| Evento | Som | Descrição |
|--------|-----|-----------|
| **Entrada** | Beep curto | 800Hz, 100ms |
| **WIN** | Caixa registradora | Dó→Mi→Sol (ascendente) |
| **LOSS** | Perda | 800→600→400Hz (descendente) |

### Alertas de Encerramento:

| Situação | Beeps | Duração |
|----------|-------|---------|
| **Erro nos sinais** | 3 | 1000ms (muito longos) |
| **Stop Loss atingido** | 5 | 800ms (longos) |
| **Sinais concluídos** | 3 | 400ms (médios) |
| **Parada manual** | 2 | 300ms (curtos) |

**Sons Personalizados:**
- Coloque seus arquivos `.wav` em `sounds/`
- Use: `python criar_sons_simples.py` para gerar sons padrão

---

## 📊 Logs e Rastreamento

### Durante Execução:

```
[INFO] SINAL DEMO encontrado: CALL em EURUSD-OTC por 1 min
[INFO] Entrada: $41.25 | Protecao 1: $70.08 | Protecao 2: $111.62

[INFO] >>> ENTRADA PRINCIPAL: $41.25 [Limite disponivel: $175.50]
[INFO] Saldo antes: $1000.00
[INFO] Ordem CALL executada: (True, 12345678)
[INFO] Aguardando resultado da ordem ID: 12345678
[INFO] Aguardando 70s para expiracao...
[INFO] Saldo depois: $1075.25 | Diferenca: $75.25
[INFO] >>> WIN! Lucro: $75.25
[INFO] === OPERACAO FINALIZADA COM WIN! Lucro total: $75.25
[INFO] [Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: $0.00
```

### Em Caso de LOSS:

```
[INFO] >>> LOSS! Prejuizo: $41.25
[INFO] >>> PROTECAO 1: $70.08 [Limite disponivel: $135.25]
[INFO] Saldo antes: $958.75
[INFO] Ordem CALL executada: (True, 12345679)
[INFO] >>> LOSS! Prejuizo: $70.08
[INFO] >>> PROTECAO 2: $111.62 [Limite disponivel: $65.17]
[INFO] Saldo antes: $888.67
[INFO] >>> WIN! Lucro: $200.00
[INFO] === PROTECAO 2 WIN! Lucro total: $88.67
[INFO] [Protecao] LOSS consecutivos: 0 | Perda acumulada: $0.00
```

### Quando Atinge Pausa:

```
[WARNING] XXX TODAS PROTECOES PERDIDAS! Prejuizo total: $222.95
[WARNING] [ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total: 2
[WARNING] [PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos 2 sinais...
[WARNING] [Protecao] LOSS: 6 | Conjuntos: 2 | Perda: $445.90

[SINAL SEGUINTE]
[WARNING] [PAUSA] Pulando sinal por seguranca. Sinais restantes para pular: 2

[SINAL SEGUINTE]
[WARNING] [PAUSA] Pulando sinal por seguranca. Sinais restantes para pular: 1

[SINAL SEGUINTE]
[INFO] [PAUSA] Fim da pausa. Zerando contadores e voltando a operar...
[INFO] SINAL DEMO encontrado: CALL em EURUSD-OTC...
```

### Quando Atinge Stop Loss:

```
[ERROR] !!! STOP LOSS ATINGIDO: Perda de 10.5% da banca !!!
[ERROR] Perda acumulada: $105.00 de $1000.00
[EMITE 5 BEEPS LONGOS] 🔊🔊🔊🔊🔊
[BOT ENCERRA]
```

---

## 🎮 Como Usar

### Instalação (Com Python):

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Preparar sinais
# Edite data/sinais_exemplo.txt

# 3. Executar
python -m bot.main --mode demo --sinais data/sinais_exemplo.txt

# 4. Digitar credenciais quando solicitado
# Email: seu_email@exemplo.com
# Senha: ******** (oculta)
```

**Segurança Aprimorada:** Credenciais são solicitadas via input e NUNCA armazenadas.

### Executável Windows (Sem Python):

```bash
# 1. Gerar executável
python build_exe.py

# 2. Ir para pasta dist/
cd dist

# 3. Preparar sinais
# Edite data/sinais_exemplo.txt

# 4. Executar
INICIAR-DEMO.bat  (clique duplo)

# 5. Digitar credenciais
# O bot solicitará email e senha
```

---

## 🛑 Como Parar o Bot

### Opção 1: Prompt Interativo (Recomendado)

Durante a execução, o bot exibirá o prompt:
```
Para parar o bot? (S/N):
```
Digite `S` para parar ou `N` para continuar.

### Opção 2: Forçar
```
Ctrl + C
```

**Ao parar manualmente:**
- 🔊 2 beeps curtos
- 📝 Log: "Comando de parada recebido. Encerrando bot..."
- ✅ Bot encerra após operação atual

---

## 🎯 Cenários de Uso Reais

### Cenário 1: Dia Perfeito

```
Banca inicial: $1000.00
Sinais: 20 operações

Resultado:
- 15 WIN na entrada principal
- 3 WIN na proteção 1
- 2 WIN na proteção 2

Lucro final: +$250.00
LOSS consecutivos: Máximo 2 (resetou com WIN)
Status: Bot finalizou todos os sinais
```

### Cenário 2: Dia com Pausas

```
Banca inicial: $1000.00
Sinais: 30 operações

Sequência:
1-3: WIN, WIN, WIN
4-9: LOSS, LOSS, LOSS [Conjunto 1], LOSS, LOSS, LOSS [Conjunto 2]
→ PAUSA: Pula sinais 10 e 11
12-15: WIN, WIN, LOSS, WIN
16-21: LOSS, LOSS, LOSS [Conjunto 1], LOSS, LOSS, LOSS [Conjunto 2]
→ PAUSA: Pula sinais 22 e 23
24-30: Operações normais

Resultado final: -$85.00 (8.5% da banca)
Status: Bot finalizou todos os sinais
```

### Cenário 3: Stop Loss Atingido

```
Banca inicial: $500.00
Limite: $50.00 (10%)
Sinais: 15 operações

Sequência:
1-8: Várias perdas acumulando
Perda acumulada: $95.00

Sinal 9:
- Entrada: $10.00
- PRE-CHECK: $95 + $10 = $105 > $50 ❌

LOG:
!!! PRE-STOP LOSS ATIVADO !!!
Entrada de $10.00 ultrapassaria limite de 10%
Perda atual: $95.00 | Potencial: $105.00 (21%)
Bot encerrado por seguranca preventiva

[5 BEEPS LONGOS]
Status: Bot encerrado em segurança
Perda final: $95.00 (NÃO ultrapassou!)
```

### Cenário 4: Proteção Bloqueada

```
Banca: $1000.00
Perda acumulada: $85.00

Operação:
- Entrada: $5.00 → LOSS
- Perda temporária: $90.00

Proteção 1:
- Valor: $15.00
- PRE-CHECK: $90 + $15 = $105 > $100 ❌
- AÇÃO: PULA P1

LOG:
!!! PRE-STOP LOSS ATIVADO NA PROTECAO 1 !!!
Protecao 1 de $15.00 ultrapassaria limite de 10%
Pulando protecao 1 por seguranca.

Resultado: Contabiliza apenas $5 da entrada
Perda final da operação: $5.00
Perda acumulada total: $90.00
Status: Continua operando (ainda tem $10 de margem)
```

---

## 📈 Estatísticas e Rastreamento

### Arquivos Gerados:

**logs/bot.log:**
```
2025-10-18 19:30:15 [INFO] Iniciando modo DEMO...
2025-10-18 19:30:18 [INFO] Conectado na conta demo
2025-10-18 19:30:18 [INFO] Saldo conta PRÁTICA: $10580.64
...
```

**data/sinais.csv:**
```csv
Ativo,HoraEntrada,Resultado,Ganho,Perda
EURUSD-OTC,2025-10-18 19:52:00,WIN,75.25,
EURJPY-OTC,2025-10-18 19:58:00,LOSS,,41.25
EURUSD-OTC,2025-10-18 19:58:00,WIN_P1,125.50,
```

---

## 🔧 Configurações Avançadas

### Modificar Limites de Proteção:

**Arquivo:** `bot/iqoption_bot.py`

```python
# Linha ~100 (DEMO) e ~425 (REAL)
STOP_LOSS_PERCENTUAL = 10.0  # Altere para 5.0, 15.0, etc
PAUSA_APOS_6_LOSS = 6        # Altere para 4, 8, etc
PAUSA_APOS_2_CONJUNTOS_3_LOSS = 2  # Altere conforme necessário
SINAIS_PARA_PULAR = 2        # Quantos sinais pular na pausa
```

### Personalizar Sons:

1. **Criar sons padrão:**
   ```bash
   python criar_sons_simples.py
   ```

2. **Usar sons personalizados:**
   - Coloque arquivos .wav em `sounds/`
   - Nomes: `entrada.wav`, `win.wav`, `loss.wav`
   - Formato recomendado: Mono, 16-bit, 44.1kHz

---

## ⚠️ Avisos Importantes

### ⛔ O que o Bot NÃO FAZ:

- ❌ Não analisa gráficos
- ❌ Não gera sinais próprios
- ❌ Não garante lucro
- ❌ Não substitui análise humana
- ❌ Não opera sem sinais programados

### ✅ O que o Bot FAZ:

- ✅ Executa sinais nos horários programados
- ✅ Aplica martingale automaticamente
- ✅ Protege sua banca (máximo 10% de perda)
- ✅ Registra todas as operações
- ✅ Emite alertas sonoros
- ✅ Gerencia risco automaticamente

### 🎯 Recomendações:

1. **SEMPRE teste no modo DEMO primeiro**
2. **Configure valores de martingale calculados** (não aleatórios)
3. **Use stop loss adequado ao seu capital**
4. **Monitore os logs regularmente**
5. **Não deixe rodando sem supervisão inicial**
6. **Tenha sinais de qualidade** (análise técnica sólida)
7. **Entenda os riscos** de opções binárias

---

## 📞 Suporte e Documentação

### Documentos Disponíveis:

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | Documentação principal |
| `GUIA_COMPLETO.md` | Este documento |
| `SEGURANCA.md` | Detalhes técnicos de segurança |
| `BUILD.md` | Como gerar executável |
| `QUICK_START.md` | Início rápido |

### Scripts Úteis:

| Script | Função |
|--------|--------|
| `build_exe.py` | Gerar executável Windows |
| `criar_sons_simples.py` | Criar arquivos de som |
| `testar_seguranca.py` | Validar pré-stop loss |
| `stop_bot.bat` | Parar o bot |

---

## 🏆 Conclusão

O **Trading Bot** é uma ferramenta **completa e segura** para automação de operações em opções binárias, com:

✅ **Proteções em múltiplas camadas**  
✅ **Impossível ultrapassar limite de perda**  
✅ **Gerenciamento inteligente de risco**  
✅ **Feedback sonoro e visual constante**  
✅ **Logs detalhados de tudo**  
✅ **Fácil de usar** (executável ou Python)  

**Lembre-se:** O bot é uma **ferramenta de execução**, não um gerador de sinais. Sua qualidade depende da qualidade dos sinais fornecidos.

**⚠️ Opções binárias envolvem risco. Opere com responsabilidade.**

---

## 📅 Versão

- **Data:** Outubro 2025
- **Plataforma:** IQ Option
- **Compatibilidade:** Windows 7/8/10/11, Linux, Mac
- **Python:** 3.8+

---

**Desenvolvido com foco em segurança financeira e automação inteligente.**

🛡️ **PROTEÇÃO DA BANCA É PRIORIDADE #1** 🛡️

