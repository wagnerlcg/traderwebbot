# Melhorias na Interface Web - Configurações de Estratégia

## Data: 28/10/2025

## Objetivo
Melhorar a aba de Configurações na interface web, permitindo que o usuário configure:
- Estratégia Martingale com opções de nível (G1 ou G2)
- Tipo de entrada (Valor Fixo ou Percentual da Banca)
- Parâmetros específicos para cada estratégia

## Alterações Realizadas

### 1. Frontend - Interface Web (`web/templates/index.html` e `web/static/js/app.js`)

#### Estratégia Valor Fixo Adicionada
- Adicionada opção "Valor Fixo" como estratégia padrão na interface web
- Ordem das estratégias: Valor Fixo (padrão), Martingale, Soros, Masaniello

#### Função `updateEstrategia()` Melhorada
- Agora exibe campos específicos para cada estratégia:
  - **Martingale**: Seleção de nível (G1 ou G2)
  - **Masaniello**: Quantidade de entradas e número de acertos necessários
  - **Soros**: Payout percentual
  - **Valor Fixo**: Mensagem explicativa

#### Função `saveConfig()` Atualizada
- Agora captura e envia os parâmetros específicos de cada estratégia:
  - `martingale_nivel` (G1 ou G2)
  - `masaniello_entradas` (quantidade)
  - `masaniello_acertos` (número)
  - `soros_payout` (percentual)

#### Cache Busting
- Versão do JavaScript atualizada para `?v=20251024-3` para forçar atualização do navegador

### 2. Backend - Integração (`web_interface.py`)

#### Passagem de Configurações
- Modificada função `run_bot_async` para passar o objeto `config` completo como parâmetro `web_config`
- Configurações agora incluem:
  - Estratégia selecionada
  - Parâmetros específicos da estratégia
  - Tipo de valor de entrada (fixo ou percentual)
  - Valor de entrada
  - Stop Loss e Stop Win

### 3. Bot - Aplicação das Configurações (`bot/iqoption_bot.py`)

#### Nova Variável Global `WEB_CONFIG`
- Adicionada variável global para armazenar configurações da interface web
- Modificadas funções `executar_demo` e `executar_real` para:
  - Aceitar parâmetro `web_config`
  - Definir variável global `WEB_CONFIG` com as configurações

### 4. Estratégias - Leitura das Configurações (`bot/estrategias.py`)

#### Função `solicitar_estrategia()` Melhorada
- Agora verifica se existe `WEB_CONFIG` com configurações da interface web
- Se encontrado, mapeia o nome da estratégia da web para o formato interno
- Se não encontrado, usa valores padrão (Valor Fixo)

## Como Funciona

1. **Usuário configura na interface web:**
   - Seleciona estratégia (ex: Martingale)
   - Se Martingale, seleciona nível (G1 ou G2)
   - Seleciona tipo de entrada (Fixo ou Percentual)
   - Define valor de entrada
   - Salva as configurações

2. **Ao iniciar o bot:**
   - A interface web envia as configurações para o backend
   - O backend passa as configurações como `web_config` para o bot
   - O bot armazena as configurações em `WEB_CONFIG`
   - As funções de estratégia leem `WEB_CONFIG` e aplicam as configurações

3. **Estratégia Martingale:**
   - Se nível G1: usa multiplicador 2x (entrada + 1 proteção)
   - Se nível G2: usa multiplicador 4x (entrada + 2 proteções)

## Como Testar

1. Reinicie o servidor web
2. Acesse a interface: http://localhost:3000
3. Faça login
4. Vá para a aba "Configurações"
5. Selecione a estratégia "Martingale"
6. Verifique se aparece a opção de escolher nível (G1 ou G2)
7. Configure o tipo de entrada (Fixo ou Percentual)
8. Defina o valor
9. Clique em "Salvar Configurações"
10. Vá para a aba "Início" e inicie o bot
11. Verifique nos logs que as configurações foram aplicadas corretamente

## Benefícios

- ✅ Configuração totalmente pela interface web, sem necessidade de terminal
- ✅ Opções claras e intuitivas para cada estratégia
- ✅ Valores padrão sensatos para usuários iniciantes
- ✅ Flexibilidade para usuários avançados configurarem parâmetros específicos
- ✅ Consistência entre todas as estratégias

## Próximos Passos (Opcional)

- Adicionar validação de valores de entrada no frontend
- Criar tooltips explicativos para cada opção
- Adicionar preview dos valores que serão usados antes de iniciar o bot
- Salvar configurações no localStorage do navegador

