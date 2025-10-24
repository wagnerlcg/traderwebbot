# 📋 Formato dos Sinais

## ✅ Formato CORRETO (Novo)

O arquivo de sinais deve ter **4 campos** separados por ponto e vírgula (`;`):

```
M1;ATIVO;HH:MM;PUT/CALL
```

### Exemplo:
```
M1;EURUSD-OTC;19:00;CALL
M1;EURJPY-OTC;19:05;PUT
M5;GBPUSD;19:30;CALL
M15;AUDCAD-OTC;20:00;PUT
```

## 📖 Campos Explicados

### 1. Tempo de Execução (M1/M5/M15/M30)
- `M1` = 1 minuto
- `M5` = 5 minutos
- `M15` = 15 minutos
- `M30` = 30 minutos

### 2. Ativo
Nome do par de moedas ou ativo:
- Com OTC: `EURUSD-OTC`, `GBPUSD-OTC`, `AUDCAD-OTC`
- Sem OTC: `EURUSD`, `GBPUSD`, `AUDCAD`

### 3. Horário (HH:MM)
Hora de entrada no formato 24 horas:
- `09:30` = 9h30 da manhã
- `14:00` = 2h00 da tarde
- `23:45` = 11h45 da noite

### 4. Tipo de Ordem
- `CALL` = Compra (você aposta que vai subir)
- `PUT` = Venda (você aposta que vai cair)

## 🆕 Mudança Importante

### ❌ Formato ANTIGO (não usar mais):
```
M1;EURUSD-OTC;19:00;CALL;10.0;20.0;40.0
```
*Tinha 7 campos com valores de entrada e proteções*

### ✅ Formato NOVO (usar agora):
```
M1;EURUSD-OTC;19:00;CALL
```
*Apenas 4 campos*

### Por quê mudou?

**Antes:** Os valores de entrada eram definidos linha por linha no arquivo.

**Agora:** Você define os valores **globalmente** ao iniciar o bot!

**Vantagens:**
- ✅ Arquivo mais simples
- ✅ Valores calculados automaticamente pelas estratégias
- ✅ Fácil ajustar valor sem editar 100 linhas
- ✅ Estratégias (Martingale, Soros) controlam os valores

## 💰 Onde definir os valores agora?

### Na Interface Web:
1. Vá para **⚙️ Configurações**
2. Seção **Valor de Entrada**
3. Escolha:
   - **Valor Fixo**: Ex: $10 (sempre usa esse valor)
   - **Percentual da Banca**: Ex: 2% (usa 2% do saldo atual)
4. Salve as configurações

### No Terminal (CLI):
O bot perguntará ao iniciar:
```
Escolha o tipo de valor de entrada:
1. Valor fixo (em $)
2. Percentual da banca (%)
```

## 📝 Exemplos Completos

### Exemplo 1: Sinais simples
```
M1;EURUSD-OTC;10:00;CALL
M1;EURJPY-OTC;10:05;PUT
M1;GBPUSD-OTC;10:10;CALL
```

### Exemplo 2: Sinais ao longo do dia
```
M1;EURUSD-OTC;09:00;CALL
M1;EURJPY-OTC;09:30;PUT
M5;GBPUSD;12:00;CALL
M5;AUDCAD-OTC;12:30;PUT
M15;USDJPY;18:00;CALL
```

### Exemplo 3: Com comentários
```
# Sinais da manhã
M1;EURUSD-OTC;09:00;CALL
M1;EURJPY-OTC;09:30;PUT

# Sinais da tarde
M5;GBPUSD;14:00;CALL
M5;AUDCAD-OTC;14:30;PUT
```

## 🔍 Validação

O bot valida automaticamente:
- ✅ Formato correto (4 campos)
- ✅ Tempo válido (M1, M5, M15, M30)
- ✅ Horário válido (00:00 a 23:59)
- ✅ Tipo válido (PUT ou CALL)

### Se houver erro, você verá:
```
Linha 5 inválida (formato incorreto): M1;EURUSD-OTC;19:00;CALL;10.0
  Formato esperado: M1;ATIVO;HH:MM;PUT/CALL
  NOTA: Valores de entrada agora são definidos globalmente ao iniciar o bot
```

## 🎯 Dicas

### ✅ Faça isso:
- Use sempre 4 campos
- Use ponto e vírgula (`;`) como separador
- Formate horário como HH:MM
- Use MAIÚSCULAS para PUT/CALL (ou minúsculas, o bot converte)
- Adicione comentários com `#` para organizar

### ❌ Evite:
- Não adicione valores de entrada no arquivo
- Não use vírgula (`,`) como separador
- Não use horário no formato 12h (AM/PM)
- Não deixe espaços extras

## 📂 Arquivos de Exemplo

O projeto já tem arquivos de exemplo:
- `data/sinais_exemplo.txt` - Vários sinais de exemplo
- `data/sinais_exemplo_web.txt` - Sinais simples para teste

Você pode copiar e modificar!

## 🆘 Precisa de ajuda?

### Problema: "Linha X inválida (formato incorreto)"
**Solução:** Certifique-se de ter exatamente 4 campos separados por `;`

### Problema: "Tempo inválido 'M2'"
**Solução:** Use apenas M1, M5, M15 ou M30

### Problema: "Hora inválida '25:00'"
**Solução:** Use formato 24h válido (00:00 a 23:59)

### Problema: "Tipo inválido 'BUY'"
**Solução:** Use apenas PUT ou CALL

### Problema: "Nenhum sinal válido encontrado"
**Solução:** 
- Verifique se há linhas sem `#` no arquivo
- Remova linhas vazias
- Certifique-se do formato correto

## 🔄 Migrando do Formato Antigo

Se você tem arquivos no formato antigo com 7 campos:

### Antes:
```
M1;EURUSD-OTC;19:00;CALL;10.0;20.0;40.0
M1;EURJPY-OTC;19:05;PUT;15.0;30.0;60.0
```

### Depois:
```
M1;EURUSD-OTC;19:00;CALL
M1;EURJPY-OTC;19:05;PUT
```

**Dica:** Use editor de texto com "Buscar e Substituir":
1. Busque: `;[0-9.]+;[0-9.]+;[0-9.]+$`
2. Substitua por: (vazio)
3. Ou simplesmente apague as últimas 3 colunas manualmente

## 📖 Mais Informações

- [GUIA_RAPIDO_WEB.md](GUIA_RAPIDO_WEB.md) - Como usar a interface web
- [INTERFACE_WEB.md](INTERFACE_WEB.md) - Documentação completa
- [GUIA_COMPLETO.md](GUIA_COMPLETO.md) - Tudo sobre o bot

---

**✅ Agora você sabe o formato correto dos sinais!**

Para testar:
1. Crie um arquivo .txt com alguns sinais
2. Carregue na interface web (Aba Sinais)
3. Configure valor de entrada (Aba Configurações)
4. Inicie o bot!

