# Trader Bot - Sinais

Bot de trading que executa operações baseadas em sinais de um arquivo texto.

> 📑 **Novo no projeto?** Comece pelo **[ÍNDICE.md](INDICE.md)** para escolher sua documentação ideal!

---

## 📚 Documentação Completa

| Documento | Descrição | Para Quem |
|-----------|-----------|-----------|
| **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)** | Resumo de 1 página | Visão geral rápida |
| **[APRESENTACAO.md](APRESENTACAO.md)** | Apresentação completa | Novos usuários |
| **[GUIA_COMPLETO.md](GUIA_COMPLETO.md)** | Funcionamento detalhado | Usuários avançados |
| **[SEGURANCA.md](SEGURANCA.md)** | Sistema de segurança | Técnicos |
| **[BUILD.md](BUILD.md)** | Gerar executável | Distribuidores |
| **[QUICK_START.md](QUICK_START.md)** | Início rápido | Iniciantes |
| **README.md** | Este arquivo | Documentação técnica |

**📖 Comece por:** [APRESENTACAO.md](APRESENTACAO.md) ou [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)

---

## 🌐 Interface Web

**Nova funcionalidade!** Controle o bot através de uma interface web moderna e intuitiva.

### 🚀 Início Rápido - Interface Web

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Iniciar interface:**
   ```bash
   python web_interface.py
   ```
   Ou use o arquivo: `INICIAR-INTERFACE-WEB.bat`

3. **Acessar:** http://localhost:3000

### ✨ Recursos da Interface Web

- 🎮 **Controle Visual**: Iniciar/parar bot com botões
- 📊 **Dashboard em Tempo Real**: Saldo, estatísticas, logs
- 📋 **Gerenciamento de Sinais**: Upload de arquivos ou colar texto
- ⚙️ **Configurações**: Stop loss, estratégias, valores de entrada
- 📄 **Logs em Tempo Real**: Acompanhe tudo que acontece
- 🔄 **WebSockets**: Atualizações instantâneas sem refresh

### 📱 Formato Simplificado de Sinais

Na interface web, use o formato simplificado:
```
M1;ATIVO;HH:MM;PUT/CALL
M5;EURUSD-OTC;19:00;CALL
M1;GBPUSD-OTC;19:05;PUT
```

Os valores de entrada são definidos globalmente nas configurações.

## 💿 Executável Windows

Prefere não instalar Python? **[Baixe o executável Windows aqui!](BUILD.md)**

- ✅ Não precisa instalar Python
- ✅ Funciona em qualquer Windows 7/8/10/11
- ✅ Arquivo único (.exe) ou pasta portável
- ✅ Instruções completas em [BUILD.md](BUILD.md)

## Formato do Arquivo de Sinais

O arquivo de sinais deve seguir o formato:
```
M1;AUDCAD-OTC;14:00;PUT;2.0;4.0;8.0
M5;EURUSD;14:30;CALL;5.0;10.0;20.0
M15;GBPUSD;15:00;PUT;3.0;6.0;12.0
M30;USDJPY;16:00;CALL;10.0
```

Onde:
- **M1/M5/M15/M30**: Tempo de execução da ordem em minutos (1, 5, 15 ou 30 minutos)
- **ATIVO**: Nome do ativo (ex: AUDCAD-OTC, EURUSD, etc.)
- **HH:MM**: Hora de entrada no formato 24h (00:00 a 23:59)
- **PUT/CALL**: Tipo de ordem (PUT = venda, CALL = compra)
- **VALOR_ENTRADA**: Valor da entrada principal > 0 (obrigatório)
- **PROTECAO1**: Valor da 1ª proteção > 0 (opcional)
- **PROTECAO2**: Valor da 2ª proteção > 0 (opcional)

## ✅ Validação Automática de Sinais

O bot **valida todos os sinais antes de iniciar**, garantindo que não haja erros:

### Validações Realizadas:
- ✅ Arquivo de sinais existe
- ✅ Formato correto de cada linha
- ✅ Tempo válido (M1, M5, M15 ou M30)
- ✅ Hora no formato HH:MM (00:00 a 23:59)
- ✅ Tipo válido (PUT ou CALL)
- ✅ Valores numéricos e positivos
- ✅ Pelo menos um sinal válido no arquivo

### Em Caso de Erro:
Se houver **qualquer problema** nos sinais, o bot:
1. ❌ Mostra todos os erros encontrados com número da linha
2. 🔊 Emite alerta sonoro (3 beeps longos)
3. 🛑 **Encerra automaticamente** sem executar nenhuma operação
4. 📝 Você corrige os erros e reinicia

**Exemplo de mensagem de erro:**
```
!!! ERROS NO ARQUIVO DE SINAIS !!!
Linha 5: tempo inválido 'M2' (deve ser M1, M5, M15 ou M30)
Linha 8: hora inválida '25:00' (deve ser HH:MM no formato 24h)
Linha 12: valor de entrada deve ser maior que zero ($-2.00)
Corrija os erros acima e reinicie o bot
```

## Sistema de Proteções (Martingale)

O bot suporta até **2 proteções** que são executadas **apenas em caso de LOSS**:

1. **Entrada Principal**: Primeira operação executada com o valor especificado
2. **Proteção 1**: Se a entrada principal der LOSS, executa automaticamente com o valor da proteção 1
3. **Proteção 2**: Se a proteção 1 também der LOSS, executa automaticamente com o valor da proteção 2

## 📋 Lista de Sinais ao Iniciar

Ao iniciar, o bot exibe **todos os sinais programados** para revisão:

```
=== SINAIS PROGRAMADOS (28) ===
 1. 19:52 | EURUSD-OTC      | CALL | M 1 | Entrada: $  41.25 | P1: $70.08   | P2: $111.62 
 2. 19:58 | EURJPY-OTC      | PUT  | M 1 | Entrada: $  41.25 | P1: $70.08   | P2: $111.62 
 3. 20:04 | EURUSD-OTC      | CALL | M 1 | Entrada: $  41.25 | P1: $70.08   | P2: $111.62 
...
28. 23:59 | EURJPY-OTC      | PUT  | M 1 | Entrada: $  41.25 | P1: $70.08   | P2: $111.62 
====================================================================================================
```

Isso permite verificar:
- ✅ Horários programados
- ✅ Ativos e direções
- ✅ Valores de entrada e proteções
- ✅ Quantidade total de sinais

## 🛡️ Sistema de Proteção Inteligente

O bot possui **proteções automáticas sofisticadas** para proteger sua banca:

### 1. Pausa após 6 LOSS Consecutivos
- **Regra**: Após **6 LOSS consecutivos**, o bot **pausa por 2 sinais**
- **Ação**: Pula os próximos 2 sinais sem operar
- **Retorno**: Após a pausa, **zera todos os contadores** e volta a operar normalmente
- **Exemplo**:
  ```
  LOSS 1, LOSS 2, LOSS 3, LOSS 4, LOSS 5, LOSS 6
  → PAUSA: Pula sinal 7 e 8
  → Sinal 9: Volta a operar (contadores zerados)
  ```

### 2. Pausa após 2 Conjuntos de 3 LOSS
- **Regra**: Após **2 conjuntos de 3 LOSS consecutivos**, o bot **pausa por 2 sinais**
- **Conjunto**: Cada vez que atinge 3 LOSS seguidos = 1 conjunto
- **Ação**: Pula os próximos 2 sinais sem operar
- **Retorno**: Após a pausa, **zera todos os contadores** e volta a operar
- **Exemplo**:
  ```
  LOSS 1, LOSS 2, LOSS 3 [Conjunto 1]
  WIN (reseta tudo)
  LOSS 1, LOSS 2, LOSS 3 [Conjunto 1 novamente]
  LOSS 4, LOSS 5, LOSS 6 [Conjunto 2]
  → PAUSA: Pula próximos 2 sinais
  → Volta a operar (contadores zerados)
  ```

### 3. Stop Loss Dinâmico (PRIORITÁRIO)
- **Regra**: **Para permanentemente** se o saldo cair mais que X% da banca inicial
- **Configurável**: Você escolhe entre **1% e 10%** (padrão 10%)
- **Dinâmico**: Recalcula o limite baseado no **saldo ATUAL**, não fixo
- **Cálculo**: `percentual_perda = ((saldo_inicial - saldo_atual) / saldo_inicial) * 100`
- **Exemplo 1**: Banca $1000, stop 10% → Para se saldo < $900
- **Exemplo 2**: Banca $1000, stop 5% → Para se saldo < $950
- **Proteção inteligente**: À medida que banca cresce, limite em reais também cresce
- **Ação**: **Encerra o bot** definitivamente quando atinge o limite

### 🚨 PRÉ-STOP LOSS Dinâmico (Segurança Máxima)

**PROTEÇÃO CRÍTICA**: O bot verifica **ANTES** de cada operação se o valor arriscado excede X% do saldo ATUAL.

**Como funciona (DINÂMICO):**
1. **Antes da Entrada Principal**: 
   - Obtém saldo atual da conta
   - Verifica: `valor_entrada <= (saldo_atual * X%)`
   - Se SIM → Executa | Se NÃO → **Encerra**

2. **Antes da Proteção 1**: 
   - Obtém saldo atual após entrada
   - Verifica: `protecao1 <= (saldo_atual * X%)`
   - Se SIM → Executa P1 | Se NÃO → **Pula P1**

3. **Antes da Proteção 2**: 
   - Obtém saldo atual após P1
   - Verifica: `protecao2 <= (saldo_atual * X%)`
   - Se SIM → Executa P2 | Se NÃO → **Pula P2**

**Exemplo de log:**
```
>>> ENTRADA PRINCIPAL: $50.00 [Saldo: $1000.00 | Max: $100.00 | Margem: $50.00]
>>> PROTECAO 1: $80.00 [Saldo: $950.00 | Max: $95.00 | Margem: $15.00]

!!! PRE-STOP LOSS ATIVADO NA PROTECAO 2 !!!
Protecao 2 de $150.00 excede limite de 10% do saldo atual
Saldo atual: $870.00 | Limite maximo: $87.00
Pulando protecao 2 por seguranca.
```

**Vantagem do Dinâmico:**
- 📈 **Banca cresce** → Pode arriscar mais (em reais)
- 📉 **Banca diminui** → Arrisca menos automaticamente
- 🎯 **Sempre proporcional** ao saldo atual

### 4. Proteção contra Erros Técnicos
O bot diferencia **LOSS de operação** de **erro técnico**:

**LOSS (conta para stop loss):**
- Operação executada e finalizada com prejuízo

**ERRO TÉCNICO (NÃO conta para stop loss):**
- Ativo não disponível na corretora
- Falha na conexão durante a execução
- Ordem rejeitada pela corretora
- Qualquer erro que impeça a execução da ordem

**Exemplo de log:**
```
>>> ENTRADA PRINCIPAL: $17.66
Saldo antes: $2976.22
Erro ao executar operacao: 'USDSEK-OTC'
[!] ERRO TECNICO - Nao conta como LOSS
[Protecao] LOSS consecutivos: 3 | Conjuntos de 3 LOSS: 1 | Perda acumulada: $150.00
```

### Logs de Proteção
O bot mostra em tempo real o status das proteções:
```
[Protecao] LOSS consecutivos: 3 | Conjuntos de 3 LOSS: 1 | Perda acumulada: $50.25
[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: 1
[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos 2 sinais...
[PAUSA] Pulando sinal por seguranca. Sinais restantes para pular: 2
[PAUSA] Fim da pausa. Zerando contadores e voltando a operar...
```

### 📊 Resumo das Proteções

| Situação | Ação | Contadores |
|----------|------|-----------|
| **WIN** | Continua operando | Zera LOSS e Conjuntos |
| **ERRO TÉCNICO** | Continua operando | Mantém contadores |
| **3 LOSS** | Continua operando | Marca 1 conjunto |
| **6 LOSS** | Pausa 2 sinais | Zera após pausa |
| **2 Conjuntos de 3 LOSS** | Pausa 2 sinais | Zera após pausa |
| **Perda > 10%** | **PARA O BOT** | - |

### 🔊 Sistema de Sons

O bot possui **sons personalizados** para cada evento:

#### Sons Durante Operação:
- **🔵 Entrada** (ao executar ordem): Beep curto agudo (800Hz, 100ms)
- **✅ WIN**: Som de caixa registradora (Dó→Mi→Sol ascendente)
- **❌ LOSS**: Som de perda (descendente 800→600→400Hz)

#### Sons de Alerta (Encerramento):
- **🔴 Erro nos Sinais**: 3 beeps longos (1000ms cada)
- **🛑 Stop Loss Atingido**: 5 beeps longos (800ms cada)
- **✅ Todos os Sinais Executados**: 3 beeps médios (400ms cada)
- **✋ Parada Manual**: 2 beeps curtos (300ms cada)

#### Sons Personalizados:
O bot pode tocar arquivos `.wav` customizados se estiverem na pasta `sounds/`:
- `sounds/entrada.wav` - Som ao executar entrada
- `sounds/win.wav` - Som de vitória/ganho
- `sounds/loss.wav` - Som de perda

**Para criar os sons padrão:**
```bash
python criar_sons_simples.py
```

**Para usar sons personalizados:**
1. Crie a pasta `sounds/`
2. Adicione seus arquivos `.wav` (mono, 16-bit, 44.1kHz recomendado)
3. Nomeie como: `entrada.wav`, `win.wav`, `loss.wav`
4. O bot usará automaticamente

**Compatibilidade:**
- ✅ Windows: `.wav` ou `winsound.Beep()`
- ✅ Linux/Mac: beep do terminal (`\a`)
- ✅ Funciona em ambos os modos (DEMO e REAL)

## ⏱️ Término Automático

O bot **encerra automaticamente** após executar todos os sinais programados:

- ✅ Verifica a cada minuto se ainda há sinais pendentes
- ✅ Considera um sinal como "executado" quando a hora atual passa do horário programado
- ✅ Ao finalizar todos os sinais, mostra o resultado final e emite alerta sonoro
- ✅ Evita que o bot fique rodando indefinidamente

**Exemplo de log:**
```
=== TODOS OS SINAIS FORAM EXECUTADOS ===
Bot DEMO finalizado. Resultado final: $125.50
[EMITE 3 BEEPS MÉDIOS] 🔊🔊🔊
```

### Exemplos:

**Sem proteção:**
```
M1;AUDCAD-OTC;14:00;PUT;2.0
```

**Com 1 proteção:**
```
M5;EURUSD;14:30;CALL;2.0;4.0
```
- Se entrada principal (R$ 2,00) der WIN → para aqui
- Se entrada principal der LOSS → executa proteção 1 (R$ 4,00)

**Com 2 proteções:**
```
M1;GBPUSD;15:00;PUT;2.0;4.0;8.0
```
- Se entrada principal (R$ 2,00) der WIN → para aqui
- Se entrada principal der LOSS → executa proteção 1 (R$ 4,00)
- Se proteção 1 der WIN → para aqui
- Se proteção 1 der LOSS → executa proteção 2 (R$ 8,00)

## Uso

### Modo Demo
```bash
python -m bot.main --mode demo --sinais data/sinais.txt
# Irá solicitar:
# 1. Stop Loss (1-10%) - se não informado via --stop-loss
# 2. Email e senha da IQ Option
```

### Modo Real
```bash
python -m bot.main --mode real --sinais data/sinais.txt
# Irá solicitar:
# 1. Stop Loss (1-10%) - se não informado via --stop-loss
# 2. Email e senha da IQ Option
```

### Com Stop Loss Pré-definido
```bash
# Stop loss de 5%
python -m bot.main --mode demo --sinais data/sinais.txt --stop-loss 5

# Stop loss de 10%
python -m bot.main --mode real --sinais data/sinais.txt --stop-loss 10
```

**Notas de Segurança:**
- ✅ Credenciais solicitadas via input (nunca armazenadas)
- ✅ Stop loss configurável entre 1% e 10%
- ✅ Limite recalculado dinamicamente conforme saldo muda

### Como Parar o Bot

O bot possui um sistema interativo de parada que funciona em background sem interromper as operações:

**Opção 1 - Prompt Interativo (Recomendado):**

Durante a execução, o bot exibirá periodicamente o prompt:
```
Para parar o bot? (S/N):
```

Digite `S` (Sim) para parar ou `N` (Não) para continuar. O bot encerrará após a operação atual.

**Opção 2 - Atalho de Teclado:**

Pressione `Ctrl+C` a qualquer momento para encerrar imediatamente.

## Parâmetros

- `--mode`: Modo de execução (demo ou real) - **obrigatório**
- `--sinais`: Caminho para o arquivo de sinais - **obrigatório**
- `--stop-loss`: Percentual de stop loss (1 a 10%) - **opcional** (se não informado, será solicitado via input)

## Configuração

### Credenciais (Segurança Aprimorada)

**O bot solicita suas credenciais a cada execução via input:**

```
============================================================
  CREDENCIAIS IQ OPTION - Conta DEMO
============================================================

IMPORTANTE: Suas credenciais NAO serao armazenadas.
Digite suas credenciais da IQ Option:

Email: seu_email@exemplo.com
Senha: ******** (oculta enquanto digita)

[OK] Credenciais recebidas
```

**Benefícios:**
- ✅ Credenciais **NUNCA** ficam armazenadas em arquivo
- ✅ Senha **oculta** durante digitação
- ✅ Segurança máxima - sem riscos de exposição
- ✅ Cada execução requer autenticação

## Exemplo de Arquivo de Sinais

Veja `data/sinais.txt` para um exemplo completo.

## Logs

Os logs são salvos em `logs/bot.log` e os resultados das operações em `data/sinais.csv`.
