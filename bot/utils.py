import logging
from logging.handlers import RotatingFileHandler
import csv
from pathlib import Path
from datetime import datetime
import json
import platform
import os

def verificar_modo_web():
    """Verifica se estamos em modo web através da variável global MODO_WEB"""
    try:
        from bot.iqoption_bot import MODO_WEB
        return MODO_WEB
    except ImportError:
        # Se não conseguir importar, verificar sys.stdin.isatty()
        import sys
        return not sys.stdin.isatty()

def setup_logger(name, log_file, level=logging.INFO, callback=None):
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Handler para arquivo (com timestamp completo)
    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(file_formatter)

    # Handler para console (sem timestamp, mais limpo)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Handler customizado para web interface (se fornecido)
    if callback:
        class WebSocketHandler(logging.Handler):
            def __init__(self, callback_func):
                super().__init__()
                self.callback = callback_func
            
            def emit(self, record):
                try:
                    log_message = self.format(record)
                    if self.callback and should_send_to_web(log_message):
                        self.callback(log_message)
                except Exception:
                    pass
        
        web_handler = WebSocketHandler(callback)
        web_handler.setFormatter(logging.Formatter('%(message)s'))
        if not logger.handlers:
            logger.addHandler(web_handler)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False

    return logger

def should_send_to_web(message):
    """Determina se uma mensagem deve ser enviada para a interface web"""
    # Filtrar mensagens técnicas
    ignore_keywords = [
        'tentando conectar',
        'aguardando 3 segundos',
        'conexao estabelecida',
        'nota: podem aparecer erros',
        'debug',
        'erro no loop',
        'status',
        'saldo',
        'stats',
        'ws:'
    ]
    
    message_lower = message.lower()
    for keyword in ignore_keywords:
        if keyword in message_lower:
            return False
    
    return True

def print_user(message):
    """Imprime mensagem limpa para o usuário (sem timestamp)"""
    print(message)

def print_error_user(message):
    """Imprime erro amigável para o usuário"""
    print(f"[ERRO] {message}")

def print_success_user(message):
    """Imprime sucesso amigável para o usuário"""
    print(f"[OK] {message}")

def print_warning_user(message):
    """Imprime aviso amigável para o usuário"""
    print(f"[AVISO] {message}")

def print_info_user(message):
    """Imprime informação amigável para o usuário"""
    print(f"[INFO] {message}")

def salvar_sinal(timestamp, par, tipo, preco, resultado=None, saldo=None):
    Path("data").mkdir(exist_ok=True)
    arquivo = Path("data/sinais.csv")
    novo = not arquivo.exists()
    with open(arquivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if novo:
            writer.writerow(["timestamp", "par", "tipo", "preco", "resultado", "saldo"])
        writer.writerow([timestamp, par, tipo, preco, resultado, saldo])

def salvar_resultado_operacao(ativo, hora_entrada_ts, resultado, ganho=None, perda=None):
    """
    Registra o resultado da operação em data/sinais.csv no formato solicitado:
    Ativo, Hora de entrada (humano), Resultado (WIN/LOSS), Ganho, Perda

    Obs.: Para não quebrar leituras anteriores, escrevemos um bloco de colunas específico
    após as colunas antigas. Se o arquivo não existir, escrevemos um cabeçalho claro.
    """
    try:
        Path("data").mkdir(exist_ok=True)
        arquivo = Path("data/sinais.csv")
        hora_humana = datetime.fromtimestamp(hora_entrada_ts).strftime("%Y-%m-%d %H:%M:%S") if hora_entrada_ts else ""

        # Quando o arquivo não existir, criamos um cabeçalho explícito para resultados
        criar_cabecalho = not arquivo.exists()

        with open(arquivo, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if criar_cabecalho:
                writer.writerow(["Ativo", "HoraEntrada", "Resultado", "Ganho", "Perda"])
            writer.writerow([ativo, hora_humana, resultado, ganho if ganho is not None else "", perda if perda is not None else ""])
    except Exception:
        # Não interromper o fluxo do bot por erro de IO
        pass

def solicitar_credenciais(conta="REAL"):
    """
    Solicita credenciais do usuário via input.
    
    Args:
        conta: Tipo de conta (REAL ou DEMO) - apenas informativo
    
    Retorna (email, senha).
    """
    import getpass
    
    print()
    print("="*60)
    print(f"  CREDENCIAIS IQ OPTION - Conta {conta.upper()}")
    print("="*60)
    print()
    print("IMPORTANTE: Suas credenciais NAO serao armazenadas.")
    print("Digite suas credenciais da IQ Option:")
    print()
    
    try:
        # Verificar se estamos em modo interativo
        import sys
        if verificar_modo_web():
            email = input("Email: ").strip()
            senha = getpass.getpass("Senha: ").strip()
        else:
            # Modo web - retornar valores vazios
            print("[AVISO] Modo web detectado. Credenciais devem ser fornecidas via interface.")
            return "", ""
        
        if not email or not senha:
            print()
            print("[ERRO] Email e senha sao obrigatorios!")
            return "", ""
        
        print()
        print("[OK] Credenciais recebidas")
        print()
        
        return email, senha
        
    except KeyboardInterrupt:
        print()
        print("\n[CANCELADO] Usuario cancelou a entrada de credenciais")
        return "", ""
    except Exception as e:
        print()
        print(f"[ERRO] Erro ao ler credenciais: {e}")
        return "", ""

def carregar_sinais(arquivo_sinais):
    """
    Carrega sinais de um arquivo texto no formato SIMPLIFICADO:
    M1;AUDCAD-OTC;14:00;PUT
    
    Onde:
    - M1/M5/M15/M30: tempo de execução em minutos (1, 5, 15 ou 30 minutos)
    - AUDCAD-OTC: nome do ativo
    - 14:00: hora de entrada (HH:MM)
    - PUT/CALL: tipo de ordem
    
    IMPORTANTE: Os valores de entrada NÃO são mais definidos no arquivo!
    O usuário define globalmente (fixo ou % da banca) ao iniciar o bot.
    
    Retorna lista de dicionários com os sinais processados.
    Levanta exceção se houver erros críticos.
    """
    sinais = []
    erros = []
    
    try:
        path = Path(arquivo_sinais)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de sinais não encontrado: {arquivo_sinais}")
        
        # Tentar diferentes codificações
        codificacoes = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        conteudo_linhas = None
        
        for codificacao in codificacoes:
            try:
                with open(path, "r", encoding=codificacao) as f:
                    conteudo_linhas = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        
        if conteudo_linhas is None:
            raise ValueError(f"Não foi possível ler o arquivo com nenhuma codificação conhecida: {arquivo_sinais}")
        
        for linha_num, linha in enumerate(conteudo_linhas, 1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):  # Ignorar linhas vazias e comentários
                continue
                
            partes = linha.split(";")
            if len(partes) != 4:  # Exatamente 4 campos: tempo, ativo, hora, tipo
                erros.append(f"Linha {linha_num} inválida (formato incorreto): {linha}")
                erros.append(f"  Formato esperado: M1;ATIVO;HH:MM;PUT/CALL")
                erros.append(f"  NOTA: Valores de entrada agora sao definidos globalmente ao iniciar o bot")
                continue
                
            tempo_str = partes[0]
            ativo = partes[1]
            hora_str = partes[2]
            tipo = partes[3]
            
            # Validar tempo (M1, M5, M15, M30)
            tempos_validos = ["M1", "M5", "M15", "M30"]
            if tempo_str not in tempos_validos:
                erros.append(f"Linha {linha_num}: tempo inválido '{tempo_str}' (deve ser M1, M5, M15 ou M30)")
                continue
                
            # Converter tempo para minutos
            tempo_minutos = int(tempo_str[1:])
            
            # Validar hora (HH:MM)
            try:
                hora_parts = hora_str.split(":")
                if len(hora_parts) != 2:
                    raise ValueError()
                hora = int(hora_parts[0])
                minuto = int(hora_parts[1])
                if not (0 <= hora <= 23 and 0 <= minuto <= 59):
                    raise ValueError()
            except ValueError:
                erros.append(f"Linha {linha_num}: hora inválida '{hora_str}' (deve ser HH:MM no formato 24h)")
                continue
                
            # Validar tipo (PUT/CALL)
            if tipo.upper() not in ["PUT", "CALL"]:
                erros.append(f"Linha {linha_num}: tipo inválido '{tipo}' (deve ser PUT ou CALL)")
                continue
                
            sinais.append({
                "tempo_minutos": tempo_minutos,
                "ativo": ativo.strip(),
                "hora": hora,
                "minuto": minuto,
                "tipo": tipo.upper(),
                "valor_entrada": None,  # Será definido pela estratégia
                "protecao1": None,
                "protecao2": None,
                "linha_original": linha
            })
                
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"Erro crítico ao ler arquivo de sinais: {e}")
    
    # Se houver erros, lançar exceção com todos os erros
    if erros:
        mensagem_erro = "\n".join(erros)
        raise ValueError(f"Erros encontrados no arquivo de sinais:\n\n{mensagem_erro}")
    
    # Validar se há pelo menos um sinal
    if not sinais:
        raise ValueError(f"Nenhum sinal válido encontrado no arquivo: {arquivo_sinais}\nVerifique se há linhas sem comentário (#)")
        
    return sinais

def verificar_sinal_agendado(sinais, hora_atual, minuto_atual):
    """
    Verifica se há algum sinal agendado para a hora atual que ainda não foi executado.
    Retorna o sinal se encontrado, None caso contrário.
    """
    for sinal in sinais:
        # Pular sinais já executados
        if sinal.get("executado", False):
            continue
        if sinal["hora"] == hora_atual and sinal["minuto"] == minuto_atual:
            return sinal
    return None

def verificar_seguranca_operacao(valor_operacao, saldo_atual, percentual_limite=10.0):
    """
    Verifica se é seguro executar uma operação sem ultrapassar o limite de perda DINAMICO.
    
    Args:
        valor_operacao: Valor que será arriscado na operação
        saldo_atual: Saldo ATUAL da conta (recalculado)
        percentual_limite: Limite de perda em % (1-50%)
    
    Returns:
        (seguro, limite_valor, margem_disponivel)
        - seguro: True se pode operar, False se arriscaria mais que o limite
        - limite_valor: Valor máximo que pode arriscar (X% do saldo atual)
        - margem_disponivel: Quanto da operação está dentro do limite
    """
    if saldo_atual <= 0:
        return False, 0, 0
    
    # Limite dinâmico baseado no saldo ATUAL
    limite_valor = saldo_atual * (percentual_limite / 100)
    
    # Pode arriscar até X% do saldo atual
    seguro = valor_operacao <= limite_valor
    margem_disponivel = limite_valor - valor_operacao if seguro else 0
    
    return seguro, limite_valor, margem_disponivel

def processar_resultado_operacao(resultado, diferenca, tipo_operacao, loss_consecutivos, perda_acumulada, logger, STOP_LOSS_CONSECUTIVOS):
    """
    Processa o resultado de uma operação (entrada principal ou proteção).
    
    Args:
        resultado: "WIN", "LOSS" ou "ERROR"
        diferenca: Valor do lucro/prejuízo
        tipo_operacao: "PRINCIPAL", "P1" ou "P2"
        loss_consecutivos: Contador atual de losses
        perda_acumulada: Perda total acumulada
        logger: Logger para mensagens
        STOP_LOSS_CONSECUTIVOS: Limite de losses consecutivos
    
    Returns:
        (loss_consecutivos_atualizado, perda_acumulada_atualizada, continuar_protecoes)
        - continuar_protecoes: False se ganhou ou erro, True se perdeu
    """
    if resultado == "ERROR":
        # Erro técnico - não conta como LOSS
        logger.warning(f"[!] ATIVO FECHADO")
        logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos}/{STOP_LOSS_CONSECUTIVOS} | Perda acumulada: ${perda_acumulada:.2f}")
        return loss_consecutivos, perda_acumulada, False
    
    elif resultado == "WIN":
        # Ganhou - resetar contador
        logger.info(f"=== {tipo_operacao} WIN! Lucro: ${diferenca:.2f}")
        logger.info(f"[Protecao] LOSS consecutivos: 0 | Perda acumulada: ${perda_acumulada:.2f}")
        return 0, perda_acumulada, False
    
    else:  # LOSS
        # Perdeu - incrementar contador e acumular perda
        prejuizo = abs(diferenca)
        nova_perda_acumulada = perda_acumulada + prejuizo
        logger.info(f"XXX {tipo_operacao} LOSS! Prejuizo: ${prejuizo:.2f}")
        return loss_consecutivos, nova_perda_acumulada, True

def verificar_sinais_pendentes(sinais, hora_atual, minuto_atual):
    """
    Verifica se ainda há sinais pendentes (futuros ou atuais) para executar.
    
    Args:
        sinais: Lista de sinais
        hora_atual: Hora atual
        minuto_atual: Minuto atual
    
    Returns:
        True se há sinais pendentes, False caso contrário
    """
    hora_minuto_atual = hora_atual * 60 + minuto_atual
    
    for sinal in sinais:
        # Verificar se sinal já foi executado
        if sinal.get("executado", False):
            continue
            
        hora_minuto_sinal = sinal["hora"] * 60 + sinal["minuto"]
        # Se há algum sinal com hora futura ou igual (atual), ainda há sinais pendentes
        if hora_minuto_sinal >= hora_minuto_atual:
            return True
    
    return False

def emitir_alerta_sonoro(repeticoes=3, duracao_ms=500):
    """
    Emite um alerta sonoro multiplataforma.
    
    Args:
        repeticoes: Número de vezes que o beep será emitido
        duracao_ms: Duração de cada beep em milissegundos (apenas Windows)
    """
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            # Windows: usar winsound
            import winsound
            for _ in range(repeticoes):
                # Frequência 1000Hz, duração em ms
                winsound.Beep(1000, duracao_ms)
        else:
            # Linux/Mac: usar beep do terminal
            for _ in range(repeticoes):
                # Beep do terminal (ASCII bell)
                print('\a', flush=True)
                import time
                time.sleep(0.5)
    except Exception as e:
        # Se falhar, pelo menos tentar o beep do terminal
        try:
            for _ in range(repeticoes):
                print('\a', flush=True)
        except:
            pass  # Silenciosamente falha se não conseguir emitir som

def tocar_som(tipo_som, sons_habilitados=True):
    """
    Toca um som específico (.wav ou beep).
    
    Args:
        tipo_som: 'entrada', 'win', 'loss'
        sons_habilitados: Se False, não toca nenhum som
    """
    # Verificar se sons estão habilitados
    if not sons_habilitados:
        return
    
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            import winsound
            
            # Tentar tocar arquivo .wav primeiro
            som_path = Path(f"sounds/{tipo_som}.wav")
            if som_path.exists():
                try:
                    winsound.PlaySound(str(som_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return
                except:
                    pass
            
            # Fallback para beeps com frequências diferentes
            if tipo_som == 'entrada':
                winsound.Beep(800, 100)  # Beep curto e agudo
            elif tipo_som == 'win':
                # Som ascendente (caixa registradora simulada)
                winsound.Beep(523, 80)   # Dó
                winsound.Beep(659, 80)   # Mi
                winsound.Beep(784, 150)  # Sol (mais longo)
            elif tipo_som == 'loss':
                # Som descendente (perda)
                winsound.Beep(800, 80)   # Alto
                winsound.Beep(600, 80)   # Médio
                winsound.Beep(400, 150)  # Baixo (mais longo)
        else:
            # Linux/Mac: beep simples do terminal
            print('\a', flush=True)
    except Exception:
        # Silenciosamente falha se não conseguir
        pass

async def executar_operacao_com_resultado(Iq, valor, ativo, tipo, tempo_minutos, logger, asyncio, sons_habilitados=True):
    """
    Executa uma operação e retorna o resultado (WIN/LOSS/ERROR) e o lucro/prejuízo.
    
    Retorna: (resultado, diferenca)
    - resultado: "WIN", "LOSS" ou "ERROR"
    - diferenca: valor do lucro (positivo) ou prejuízo (negativo), ou 0 em caso de erro
    """
    import time
    
    try:
        # VERIFICAÇÃO DE DISPONIBILIDADE (informativa apenas - não bloqueia)
        # A verificação real será feita pela API da IQ Option ao executar a ordem
        try:
            ativos_abertos = Iq.get_all_open_time()
            if ativos_abertos and 'binary' in ativos_abertos:
                # Verificar se o ativo está na lista
                if ativo in ativos_abertos['binary']:
                    if not ativos_abertos['binary'][ativo].get('open', False):
                        logger.info(f"[AVISO] Ativo '{ativo}' pode estar fechado. Tentando operar mesmo assim...")
                else:
                    logger.debug(f"Ativo '{ativo}' nao encontrado na lista pre-verificacao. Continuando...")
        except Exception as e:
            logger.debug(f"Pre-verificacao de disponibilidade falhou: {e}")
            # Continua normalmente - a API decidirá
        
        # Emitir som de entrada
        tocar_som('entrada', sons_habilitados)
        
        # Capturar saldo antes da ordem
        saldo_antes = Iq.get_balance()
        logger.info(f"Saldo antes: ${saldo_antes:.2f}")
        print_user(f"[SALDO] Saldo atual: ${saldo_antes:.2f}")
        
        # Executar ordem com o ativo EXATAMENTE como informado (sem variações)
        resultado = Iq.buy(valor, ativo, tipo.lower(), tempo_minutos)
        logger.info(f"Ordem {tipo} executada em {ativo}: {resultado}")
        print_user(f"[EXECUTANDO] {tipo} em {ativo} por {tempo_minutos} minuto(s)")
        
        # Extrair order_id
        order_id = None
        if resultado and isinstance(resultado, tuple) and len(resultado) >= 2:
            ok_flag, payload = resultado[0], resultado[1]
            if ok_flag:
                order_id = payload
            else:
                mensagem_erro = str(payload)
                logger.warning(f"Compra rejeitada pela corretora: {mensagem_erro}")
                
                # Se ativo suspenso ou indisponível
                if 'suspended' in mensagem_erro.lower() or 'not available' in mensagem_erro.lower():
                    logger.warning(f"ATIVO REJEITADO: '{ativo}' - {mensagem_erro}")
                    print_error_user(f"Ativo '{ativo}' não disponível no momento")
                else:
                    print_error_user(f"Problema ao executar operação no ativo '{ativo}'")
                
                logger.warning(f"[!] ATIVO FECHADO")
                return "ERROR", 0
        elif resultado and isinstance(resultado, dict) and resultado.get('id'):
            order_id = resultado['id']
        
        if not order_id:
            #logger.warning(f"Nao foi possivel obter order_id - possivel erro tecnico")
            #print_error_user(f"Problema ao executar operação no ativo '{ativo}'")
            logger.warning(f"[!] ATIVO FECHADO")
            return "ERROR", 0
        
        logger.info(f"Aguardando resultado da ordem ID: {order_id}")
        print_user(f"⏳ Aguardando resultado...")
        
        # Aguardar tempo da ordem + margem
        tempo_espera = (tempo_minutos * 60) + 10
        logger.info(f"Aguardando {tempo_espera}s para expiracao...")
        await asyncio.sleep(tempo_espera)
        
        # Aguardar mais um pouco para garantir processamento
        await asyncio.sleep(5)
        
        # Obter saldo após ordem
        saldo_depois = Iq.get_balance()
        diferenca = saldo_depois - saldo_antes
        
        logger.info(f"Saldo depois: ${saldo_depois:.2f} | Diferenca: ${diferenca:.2f}")
        
        # Determinar resultado
        if diferenca > 0.1:  # Margem para evitar erros de precisão
            logger.info(f">>> WIN! Lucro: ${diferenca:.2f}")
            print_success_user(f"WIN! Lucro: ${diferenca:.2f}")
            tocar_som('win', sons_habilitados)
            return "WIN", diferenca
        else:
            logger.info(f">>> LOSS! Prejuizo: ${valor:.2f}")
            print_error_user(f"LOSS! Prejuízo: ${valor:.2f}")
            tocar_som('loss', sons_habilitados)
            return "LOSS", -valor
            
    except Exception as e:
        # Logar erro técnico apenas no arquivo de log (não no console)
        #logger.error(f"Erro ao executar operacao: {e}")
        #logger.error(f"Tipo do erro: {type(e).__name__}")
        #logger.error(f"Ativo: {ativo} | Valor: {valor} | Tipo: {tipo} | Tempo: {tempo_minutos}")
        #logger.error(f"=== TRACEBACK COMPLETO ===")
        
        # Logar cada linha do traceback separadamente
        import traceback
        for linha in traceback.format_exc().split('\n'):
            if linha.strip():
                logger.error("")
        
        #logger.error(f"=== FIM DO TRACEBACK ===")
        #logger.warning(f"[!] ERRO TECNICO - Nao conta como LOSS")
        #logger.warning(f"[!] ATIVO FECHADO")
        # Mensagem simples para o usuário
        print_warning_user("ATIVO FECHADO")
        
        return "ERROR", 0


# ========================================
# FUNCOES DE STOP WIN
# ========================================

def verificar_bloqueio_stop_win(email: str) -> tuple:
    """
    Verifica se o usuário está bloqueado por Stop Win nas últimas 24h.
    
    Args:
        email: Email do usuário
    
    Returns:
        Tupla (bloqueado: bool, horas_restantes: float, lucro: float)
    """
    import hashlib
    from datetime import datetime, timedelta
    
    # EXCECAO: Emails liberados nunca são bloqueados
    EMAILS_LIBERADOS = ["wagnerlcg@gmail.com", "matheus@barqengenharia.com.br"]
    if email.lower().strip() in EMAILS_LIBERADOS:
        return False, 0, 0
    
    # Criar hash do email para privacidade
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
    
    # Arquivo de controle
    Path("data").mkdir(exist_ok=True)
    arquivo_bloqueios = Path("data/.stop_win_locks.json")
    
    # Limpar bloqueios expirados primeiro
    limpar_bloqueios_expirados(arquivo_bloqueios)
    
    # Verificar se há bloqueio ativo
    if not arquivo_bloqueios.exists():
        return False, 0, 0
    
    try:
        with open(arquivo_bloqueios, 'r', encoding='utf-8') as f:
            bloqueios = json.load(f)
        
        if email_hash in bloqueios:
            bloqueio = bloqueios[email_hash]
            data_bloqueio = datetime.fromisoformat(bloqueio['timestamp'])
            data_liberacao = data_bloqueio + timedelta(hours=24)
            agora = datetime.now()
            
            if agora < data_liberacao:
                # Ainda bloqueado
                tempo_restante = data_liberacao - agora
                horas_restantes = tempo_restante.total_seconds() / 3600
                lucro = bloqueio.get('lucro', 0)
                return True, horas_restantes, lucro
            else:
                # Bloqueio expirado
                return False, 0, 0
        
        return False, 0, 0
        
    except Exception as e:
        # Em caso de erro, permitir execução
        return False, 0, 0


def registrar_stop_win(email: str, lucro: float, percentual: float, banca_inicial: float):
    """
    Registra que o Stop Win foi atingido e cria bloqueio de 24h.
    
    Args:
        email: Email do usuário
        lucro: Valor do lucro obtido
        percentual: Percentual de Stop Win configurado
        banca_inicial: Banca inicial do usuário
    """
    import hashlib
    from datetime import datetime
    
    # EXCECAO: Emails liberados nunca são bloqueados
    EMAILS_LIBERADOS = ["wagnerlcg@gmail.com", "matheus@barqengenharia.com.br"]
    if email.lower().strip() in EMAILS_LIBERADOS:
        return  # Não registra bloqueio
    
    # Criar hash do email
    email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
    
    # Arquivo de controle
    Path("data").mkdir(exist_ok=True)
    arquivo_bloqueios = Path("data/.stop_win_locks.json")
    
    # Carregar bloqueios existentes
    bloqueios = {}
    if arquivo_bloqueios.exists():
        try:
            with open(arquivo_bloqueios, 'r', encoding='utf-8') as f:
                bloqueios = json.load(f)
        except:
            bloqueios = {}
    
    # Adicionar novo bloqueio
    bloqueios[email_hash] = {
        'timestamp': datetime.now().isoformat(),
        'lucro': lucro,
        'percentual': percentual,
        'banca_inicial': banca_inicial
    }
    
    # Salvar
    with open(arquivo_bloqueios, 'w', encoding='utf-8') as f:
        json.dump(bloqueios, f, indent=2)


def limpar_bloqueios_expirados(arquivo_bloqueios: Path):
    """Remove bloqueios com mais de 24h do arquivo."""
    from datetime import datetime, timedelta
    
    if not arquivo_bloqueios.exists():
        return
    
    try:
        with open(arquivo_bloqueios, 'r', encoding='utf-8') as f:
            bloqueios = json.load(f)
        
        agora = datetime.now()
        bloqueios_ativos = {}
        
        for email_hash, bloqueio in bloqueios.items():
            data_bloqueio = datetime.fromisoformat(bloqueio['timestamp'])
            data_liberacao = data_bloqueio + timedelta(hours=24)
            
            if agora < data_liberacao:
                # Ainda ativo
                bloqueios_ativos[email_hash] = bloqueio
        
        # Salvar apenas bloqueios ativos
        with open(arquivo_bloqueios, 'w', encoding='utf-8') as f:
            json.dump(bloqueios_ativos, f, indent=2)
            
    except Exception:
        pass


def solicitar_stop_win() -> float:
    """
    Solicita o percentual de Stop Win ao usuário.
    
    Returns:
        Percentual de Stop Win (entre 1 e 20)
    """
    print()
    print("="*60)
    print("  CONFIGURACAO DE STOP WIN")
    print("="*60)
    print()
    print("O Stop Win protege seus lucros parando o bot automaticamente")
    print("quando voce atinge um percentual de ganho desejado.")
    print()
    print("Apos atingir o Stop Win, o bot sera bloqueado por 24 horas")
    print("para evitar que a emocao faca voce perder os ganhos.")
    print()
    print("Valor deve estar entre 1% e 20% da banca.")
    print()
    
    # Verificar se estamos em modo web através da variável global
    try:
        from bot.iqoption_bot import MODO_WEB
        modo_web = MODO_WEB
    except ImportError:
        # Se não conseguir importar, verificar verificar_modo_web()
        import sys
        modo_web = not verificar_modo_web()
    
    if modo_web:
        # Modo web - usar valor padrão
        stop_win_percentual = 20.0
        print(f"Stop Win (%): {stop_win_percentual} (padrão para modo web)")
        print()
        print(f"[OK] Stop Win configurado: {stop_win_percentual}%")
        return stop_win_percentual
    
    # Modo terminal - solicitar input
    while True:
        try:
            import sys
            stop_win_input = input("Stop Win (%): ").strip()
            stop_win_percentual = float(stop_win_input)
            
            if 1 <= stop_win_percentual <= 20:
                print()
                print(f"[OK] Stop Win configurado: {stop_win_percentual}%")
                return stop_win_percentual
            else:
                print()
                print("[ERRO] Valor deve estar entre 1% e 20%. Tente novamente.")
                print()
                
        except (ValueError, KeyboardInterrupt):
            print()
            print("[ERRO] Valor invalido. Usando padrao de 10%")
            return 10.0


def verificar_stop_win_atingido(saldo_atual: float, banca_inicial: float, 
                                stop_win_percentual: float) -> tuple:
    """
    Verifica se o Stop Win foi atingido.
    
    Args:
        saldo_atual: Saldo atual da conta
        banca_inicial: Banca inicial
        stop_win_percentual: Percentual de Stop Win configurado
    
    Returns:
        Tupla (atingido: bool, lucro: float, percentual_atual: float)
    """
    lucro = saldo_atual - banca_inicial
    percentual_atual = (lucro / banca_inicial) * 100 if banca_inicial > 0 else 0
    
    atingido = percentual_atual >= stop_win_percentual
    
    return atingido, lucro, percentual_atual