# 📚 Sobre a API da IQ Option

## ⚠️ IMPORTANTE: Versão Correta da Biblioteca

A biblioteca `iqoptionapi` possui **duas versões diferentes**:

### ❌ Versão INCORRETA (PyPI Oficial)
- **Fonte**: https://pypi.org/project/iqoptionapi/
- **Última versão**: 0.5 (muito antiga)
- **Status**: Desatualizada, não funciona corretamente
- **Problema**: Se você instalar com `pip install iqoptionapi`, receberá esta versão antiga

### ✅ Versão CORRETA (GitHub)
- **Fonte**: https://github.com/Lu-Yi-Hsun/iqoptionapi
- **Versão atual**: 6.8.9.1
- **Status**: Mantida e funcional
- **Instalação**: `pip install git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git`

---

## 🔧 Como Atualizar a API

### Método 1: Script Automático (RECOMENDADO)
Execute o arquivo `ATUALIZAR_API.bat` que está na raiz do projeto ou na pasta `dist/`

### Método 2: Manual
```bash
# 1. Desinstalar versão antiga
pip uninstall -y iqoptionapi

# 2. Instalar versão correta do GitHub
pip install git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git
```

---

## 🔍 Como Verificar a Versão Instalada

```bash
pip show iqoptionapi
```

**Saída correta:**
```
Name: iqoptionapi
Version: 6.8.9.1
Home-page: https://github.com/Lu-Yi-Hsun/iqoptionapi
```

**Se aparecer versão 0.5 ou 0.3, você está com a versão ERRADA!**

---

## 📋 Requirements.txt

O arquivo `requirements.txt` está configurado corretamente:

```
pandas
git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git
python-dotenv
```

**Nota:** A linha com `git+` garante que a versão do GitHub seja instalada.

---

## 🐛 Problemas Comuns

### Erro: "No matching distribution found for iqoptionapi>=5.0.0"
- **Causa**: Tentou instalar do PyPI, que só tem versão 0.5
- **Solução**: Use o script `ATUALIZAR_API.bat` ou instale do GitHub

### Erro: "Connection is already closed"
- **Causa**: Pode ser devido a versão antiga da API
- **Solução**: Atualize para a versão do GitHub

### Bot não conecta na IQ Option
- **Causa**: Versão incorreta da API
- **Solução**: Verifique a versão com `pip show iqoptionapi` e atualize se necessário

---

## 📞 Suporte

Se após atualizar a API os problemas persistirem:

1. Feche **todas** as instâncias do bot
2. Execute `ATUALIZAR_API.bat`
3. Aguarde 1-2 minutos
4. Teste novamente

---

**Última atualização:** Outubro 2025  
**Versão da API recomendada:** 6.8.9.1 (GitHub)

