# 🚀 Guia de Início Rápido

## Para Desenvolvedores (Com Python)

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Preparar sinais:**
   ```bash
   # Edite data/sinais.txt com seus sinais
   ```

3. **Executar:**
   ```bash
   # Modo DEMO
   python -m bot.main --mode demo --sinais data/sinais.txt
   
   # O bot solicitará:
   # - Email da IQ Option
   # - Senha (oculta durante digitação)
   
   # Modo REAL
   python -m bot.main --mode real --sinais data/sinais.txt
   ```

**Segurança:** Credenciais são solicitadas a cada execução e **NUNCA** armazenadas.

## Para Usuários (Sem Python - Executável)

### Opção 1: Gerar o Executável Você Mesmo

1. **Instalar Python** (apenas uma vez)
2. **Clonar/baixar este projeto**
3. **Executar:**
   ```bash
   build.bat
   ```
4. **Usar a pasta `dist/` gerada**

### Opção 2: Usar Executável Pronto (se disponível)

1. **Baixar o ZIP** com o executável
2. **Extrair** para uma pasta
3. **Editar sinais** em `data/sinais.txt`
4. **Executar** `INICIAR-DEMO.bat` ou `INICIAR-REAL.bat`
5. **Digitar credenciais** quando solicitado

## 📝 Configurando o Bot

### 1. Credenciais (Input Seguro)

**O bot solicita a cada execução:**
```
Email: seu_email@exemplo.com
Senha: ******** (oculta)
```

**Não é necessário configurar arquivo!**
- ✅ Mais seguro - não fica armazenado
- ✅ Senha oculta ao digitar
- ✅ Solicitado toda vez

### 2. Sinais (`data/sinais.txt`)

Formato:
```
M1;EURUSD-OTC;19:30;CALL;2.0;4.0;8.0
```

Onde:
- `M1` = 1 minuto (M1, M5, M15, M30)
- `EURUSD-OTC` = Ativo
- `19:30` = Hora (24h)
- `CALL` = Direção (CALL ou PUT)
- `2.0` = Entrada principal
- `4.0` = Proteção 1 (opcional)
- `8.0` = Proteção 2 (opcional)

## 🛑 Parar o Bot

### Método 1: Prompt Interativo (Recomendado)

Durante a execução, digite `S` quando aparecer:
```
Para parar o bot? (S/N):
```

### Método 2: Atalho de Teclado
`Ctrl + C` no console

## 📊 Proteções Automáticas

O bot para automaticamente em 3 situações:

1. **2 LOSS consecutivos**
2. **10% da banca perdida**
3. **Todos os sinais executados**

Em todos os casos, emite alerta sonoro! 🔊

## 📁 Onde Encontrar os Logs

- **Logs do bot:** `logs/bot.log`
- **Resultados:** `data/sinais.csv`

## ❓ Problemas Comuns

### "Não conecta na IQ Option"
- Verifique se digitou email/senha corretamente
- Teste primeiro no modo DEMO
- Verifique sua conexão com internet
- Credenciais são solicitadas a cada execução

### "Arquivo de sinais inválido"
- Verifique o formato: `M1;ATIVO;HH:MM;PUT/CALL;VALOR`
- Linhas com `#` são comentários (ignoradas)
- Não pode ter linhas vazias entre sinais

### "Executável não abre"
- Antivírus pode estar bloqueando
- Tente executar como administrador
- Adicione exceção no antivírus

## 📚 Documentação Completa

- **README.md** - Documentação completa do bot
- **BUILD.md** - Como gerar o executável
- Este arquivo - Guia rápido

## 🎯 Dicas

✅ **Sempre teste no modo DEMO primeiro**  
✅ **Configure proteções adequadas ao seu capital**  
✅ **Monitore os logs regularmente**  
✅ **Use valores de martingale calculados (ex: 2x, não valores aleatórios)**  
✅ **Não deixe o bot rodando sem supervisão inicial**

