# 🔨 Como Gerar o Executável Windows (.exe)

Este guia explica como criar um executável standalone do Trading Bot para Windows.

## 📋 Pré-requisitos

1. **Python 3.8 ou superior** instalado
2. **Todas as dependências instaladas:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Gerar o Executável

### Método 1: Script Automático (Recomendado)

Execute o script que faz tudo automaticamente:

```bash
python build_exe.py
```

O script irá:
- ✅ Verificar e instalar PyInstaller se necessário
- ✅ Limpar builds anteriores
- ✅ Gerar o executável `trader-bot.exe`
- ✅ Criar estrutura de pastas necessária
- ✅ Copiar arquivos de configuração e exemplos
- ✅ Criar launchers .bat para facilitar uso

### Método 2: Manual com PyInstaller

Se preferir fazer manualmente:

1. **Instalar PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Gerar o executável:**
   ```bash
   pyinstaller --onefile --name=trader-bot --add-data="config;config" --hidden-import=asyncio --hidden-import=iqoptionapi --console bot/main.py
   ```

3. **Criar estrutura manual:**
   ```bash
   mkdir dist\config
   mkdir dist\data
   mkdir dist\logs
   copy config\credentials.json.example dist\config\
   copy data\sinais_exemplo.txt dist\data\
   copy stop_bot.bat dist\
   ```

## 📦 Resultado

Após a execução, você terá a pasta `dist/` com:

```
dist/
├── trader-bot.exe          # Executável principal
├── INICIAR-DEMO.bat        # Atalho para modo DEMO
├── INICIAR-REAL.bat        # Atalho para modo REAL
├── stop_bot.bat            # Para parar o bot
├── LEIA-ME.txt            # Instruções de uso
├── README.md              # Documentação completa
├── config/
│   └── credentials.json.example
├── data/
│   └── sinais_exemplo.txt
└── logs/
    └── (logs serão criados aqui)
```

## 📤 Distribuir o Executável

Para distribuir para outras pessoas/computadores:

1. **Comprimir a pasta dist/:**
   ```bash
   # Windows PowerShell
   Compress-Archive -Path dist -DestinationPath trader-bot-windows.zip
   ```

2. **Compartilhar o arquivo ZIP**
   - O usuário só precisa extrair e executar
   - Não precisa ter Python instalado
   - Funciona em qualquer Windows 7/8/10/11

## 🎯 Usando o Executável

### Primeira vez:

1. **Prepare os sinais:**
   - Edite `sinais_exemplo.txt` com seus sinais

2. **Execute:**
   - Clique duas vezes em `INICIAR-DEMO.bat` ou `INICIAR-REAL.bat`

3. **Digite suas credenciais:**
   - Email da IQ Option
   - Senha (será oculta durante digitação)
   
**Segurança:** Credenciais são solicitadas a cada execução e NUNCA armazenadas!

### Via linha de comando:

```bash
# Modo DEMO
trader-bot.exe --mode demo --sinais data/sinais_exemplo.txt

# Modo REAL
trader-bot.exe --mode real --sinais data/sinais_exemplo.txt
```

## 🔧 Solução de Problemas

### "Falta algum módulo"
- Reinstale as dependências: `pip install -r requirements.txt`
- Regenere o executável

### "Antivírus bloqueia o executável"
- É normal para executáveis PyInstaller
- Adicione exceção no antivírus
- Ou assine digitalmente o executável (avançado)

### "Erro ao conectar IQ Option"
- Verifique se `credentials.json` está configurado
- Verifique conexão com internet
- Tente primeiro no modo DEMO

### Executável muito grande
- Normal para PyInstaller (40-60MB)
- Inclui Python inteiro + dependências
- Para reduzir, use `--onedir` em vez de `--onefile` (gera pasta em vez de arquivo único)

## 📝 Notas Importantes

- ✅ O executável é **totalmente portável**
- ✅ Funciona em Windows sem Python instalado
- ✅ Inclui **todas as dependências** necessárias
- ⚠️ Tamanho típico: 40-60 MB
- ⚠️ Pode demorar alguns segundos para iniciar (normal para PyInstaller)
- ⚠️ Alguns antivírus podem dar falso positivo (adicione exceção)

## 🔒 Segurança Aprimorada

### ✅ Credenciais Seguras

**O bot NÃO armazena credenciais em arquivo!**

- ✅ Solicita email/senha a cada execução
- ✅ Senha oculta durante digitação (getpass)
- ✅ Credenciais apenas em memória
- ✅ Nunca salvas em disco
- ✅ Seguro para distribuir executável

**Benefícios:**
- Sem risco de exposição de credenciais
- Cada usuário autentica individualmente
- Não precisa configurar arquivos sensíveis
- Distribuição segura do executável

## 📚 Referências

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Python Packaging](https://packaging.python.org/)

