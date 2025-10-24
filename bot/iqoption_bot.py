import asyncio
import time
import os
import json
import threading
import warnings
import sys
from datetime import datetime
from bot.utils import salvar_sinal, solicitar_credenciais, salvar_resultado_operacao, carregar_sinais, verificar_sinal_agendado
from iqoptionapi.stable_api import IQ_Option

# Suprimir warnings desnecessários da biblioteca iqoptionapi
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', module='iqoptionapi')
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Suprimir erros de threading do iqoptionapi (KeyError: 'underlying' em __get_digital_open)
# Estes erros são internos da biblioteca e não afetam operações binárias
import logging
logging.getLogger('iqoptionapi').setLevel(logging.CRITICAL)

# Suprimir exceções de threads não tratadas (threading exceptions)
def suprimir_threading_exception(args):
    """Suprime exceções de threads do iqoptionapi que não afetam o bot"""
    if 'underlying' in str(args.exc_value) or '__get_digital_open' in str(args.thread):
        # Ignorar erros de opções digitais (não usamos)
        return
    # Para outros erros, usar comportamento padrão
    sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

# Instalar hook personalizado para threads (Python 3.8+)
try:
    threading.excepthook = suprimir_threading_exception
except AttributeError:
    # Python < 3.8 não tem threading.excepthook
    pass

# Flag global para controlar parada do bot
parar_bot = False

def aguardar_comando_parada():
    """
    Função que roda em thread separada aguardando comando do usuário para parar o bot.
    Não bloqueia a execução principal do robô.
    """
    global parar_bot
    while not parar_bot:
        try:
            resposta = input("\nPara parar o bot? (S/N): ").strip().upper()
            if resposta == 'S':
                print("\n✓ Comando de parada recebido. Encerrando bot após operação atual...")
                parar_bot = True
                break
            elif resposta == 'N':
                print("✓ Bot continuará executando. Digite novamente quando quiser parar.")
            else:
                print("⚠ Resposta inválida. Digite 'S' para parar ou 'N' para continuar.")
        except (EOFError, KeyboardInterrupt):
            # Se houver Ctrl+C ou fim de arquivo, também para
            parar_bot = True
            break

def normalizar_ativo(par):
    """
    Normaliza o nome do ativo para a API da IQ Option.
    - Remove espaços extras
    - Converte para formato esperado pela API
    - Suporta ativos OTC
    """
    if not par:
        return par
    
    # Remove espaços extras e converte para maiúsculo
    par_normalizado = par.strip().upper()
    
    # Mapeamento de ativos com espaços para formato da API
    mapeamento_ativos = {
        "USD CURRENCY INDEX": "USD_INDEX",
        "EUR CURRENCY INDEX": "EUR_INDEX", 
        "GBP CURRENCY INDEX": "GBP_INDEX",
        "JPY CURRENCY INDEX": "JPY_INDEX",
        "AUD CURRENCY INDEX": "AUD_INDEX",
        "CAD CURRENCY INDEX": "CAD_INDEX",
        "CHF CURRENCY INDEX": "CHF_INDEX",
        "NZD CURRENCY INDEX": "NZD_INDEX",
        # Adicione outros mapeamentos conforme necessário
    }
    
    # Verifica se existe mapeamento específico
    if par_normalizado in mapeamento_ativos:
        return mapeamento_ativos[par_normalizado]
    
    # Para ativos OTC, mantém o nome original
    # A API da IQ Option geralmente aceita nomes com espaços
    return par_normalizado

async def executar_demo(arquivo_sinais, logger, email, senha, stop_loss_percentual_arg=None, sons_habilitados=True, balance_callback=None, stop_callback=None):
    logger.info(f"Iniciando modo DEMO com arquivo de sinais: {arquivo_sinais}")
    
    # VERIFICAR BLOQUEIO POR STOP WIN
    from bot.utils import verificar_bloqueio_stop_win
    bloqueado, horas_restantes, lucro_anterior = verificar_bloqueio_stop_win(email)
    
    if bloqueado:
        logger.error("="*60)
        logger.error("STOP WIN ATIVO - BOT BLOQUEADO!")
        logger.error("="*60)
        logger.error(f"Voce atingiu o Stop Win anteriormente e ganhou ${lucro_anterior:.2f}")
        logger.error(f"O bot esta bloqueado por mais {horas_restantes:.1f} horas")
        logger.error(f"para proteger seus lucros e evitar operacoes emocionais.")
        logger.error("")
        logger.error("Volte apos o periodo de bloqueio para operar novamente.")
        logger.error("="*60)
        print("\n" + "="*60)
        print("🚫 STOP WIN ATIVO - BOT BLOQUEADO!")
        print("="*60)
        print(f"✅ Voce atingiu o Stop Win e ganhou ${lucro_anterior:.2f}")
        print(f"🕐 Bloqueio restante: {horas_restantes:.1f} horas")
        print("")
        print("Este bloqueio protege seus lucros!")
        print("Volte apos o periodo para operar novamente.")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=500)
        return
    
    if not email or not senha:
        logger.error("Credenciais nao fornecidas. Encerrando...")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return

    logger.info("Criando sessão IQ_Option (DEMO) e conectando...")
    logger.info("Aguardando 3 segundos para estabilizar conexao...")
    await asyncio.sleep(3)
    
    Iq = IQ_Option(email, senha)
    
    try:
        logger.info("Tentando conectar...")
        Iq.connect()
        logger.info("Conexao estabelecida com sucesso!")
    except ConnectionError as e:
        logger.error("="*60)
        logger.error("ERRO DE CONEXAO COM IQ OPTION")
        logger.error("="*60)
        logger.error(f"Mensagem: {e}")
        logger.error("")
        logger.error("Possíveis causas:")
        logger.error("1. Problema de internet/firewall")
        logger.error("2. Servidores da IQ Option instáveis")
        logger.error("3. Muitas tentativas de conexão seguidas")
        logger.error("")
        logger.error("Solucoes:")
        logger.error("- Verifique sua conexao com a internet")
        logger.error("- Aguarde 1-2 minutos e tente novamente")
        logger.error("- Reinicie seu modem/roteador se necessário")
        logger.error("="*60)
        print("\n" + "="*60)
        print("❌ ERRO DE CONEXAO COM IQ OPTION")
        print("="*60)
        print("\nPossíveis causas:")
        print("  1. Problema de internet/firewall")
        print("  2. Servidores da IQ Option instáveis")
        print("  3. Muitas tentativas de conexão seguidas")
        print("\nSolucoes:")
        print("  ✓ Verifique sua conexao com a internet")
        print("  ✓ Aguarde 1-2 minutos e tente novamente")
        print("  ✓ Reinicie seu modem/roteador se necessário")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except json.decoder.JSONDecodeError as e:
        logger.error("="*60)
        logger.error("ERRO DE AUTENTICACAO NA IQ OPTION")
        logger.error("="*60)
        logger.error("Possíveis causas:")
        logger.error("1. Email ou senha incorretos")
        logger.error("2. Conta bloqueada ou com verificação pendente")
        logger.error("3. IQ Option mudou o processo de autenticação")
        logger.error("4. Problema temporário nos servidores da IQ Option")
        logger.error("")
        logger.error("Solucoes:")
        logger.error("- Verifique suas credenciais no site da IQ Option")
        logger.error("- Acesse sua conta pelo navegador para verificar se há algum aviso")
        logger.error("- Tente novamente em alguns minutos")
        logger.error("="*60)
        print("\n" + "="*60)
        print("❌ ERRO DE AUTENTICACAO NA IQ OPTION")
        print("="*60)
        print("\nPossíveis causas:")
        print("  1. Email ou senha incorretos")
        print("  2. Conta bloqueada ou com verificação pendente")
        print("  3. IQ Option mudou o processo de autenticação")
        print("  4. Problema temporário nos servidores da IQ Option")
        print("\nSolucoes:")
        print("  ✓ Verifique suas credenciais no site da IQ Option")
        print("  ✓ Acesse sua conta pelo navegador para verificar se há algum aviso")
        print("  ✓ Tente novamente em alguns minutos")
        print("  ✓ Se o problema persistir, contate o suporte da IQ Option")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except Exception as e:
        erro_msg = str(e)
        logger.error(f"Erro inesperado ao conectar: {erro_msg}")
        
        # Tratamento específico para "Connection already closed"
        if "Connection is already closed" in erro_msg or "already closed" in erro_msg.lower():
            logger.error("")
            logger.error("="*60)
            logger.error("ERRO: CONEXAO JA FECHADA")
            logger.error("="*60)
            logger.error("Este erro ocorre quando a biblioteca tenta usar")
            logger.error("uma conexao que ja foi encerrada.")
            logger.error("")
            logger.error("SOLUCOES:")
            logger.error("1. AGUARDE 2-3 MINUTOS antes de tentar novamente")
            logger.error("2. Feche TODOS os terminais/janelas do bot")
            logger.error("3. Abra uma NOVA janela e execute novamente")
            logger.error("4. Se persistir, reinicie seu computador")
            logger.error("="*60)
            print("\n" + "="*60)
            print("⚠️  ERRO: CONEXAO JA FECHADA")
            print("="*60)
            print("\nEste erro ocorre por tentativas muito rapidas.")
            print("")
            print("SOLUCOES:")
            print("  1. AGUARDE 2-3 MINUTOS")
            print("  2. Feche TODAS as janelas do bot")
            print("  3. Abra uma NOVA janela")
            print("  4. Execute novamente")
            print("")
            print("IMPORTANTE: Nao tente reconectar imediatamente!")
            print("="*60 + "\n")
        
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    
    try:
        Iq.change_balance("PRACTICE")
    except Exception:
        pass

    # Reconnect automático
    tentativas_reconexao = 0
    max_tentativas = 3
    while not Iq.check_connect() and tentativas_reconexao < max_tentativas:
        logger.warning(f"Tentando reconectar na IQ Option... (tentativa {tentativas_reconexao + 1}/{max_tentativas})")
        try:
            Iq.connect()
        except json.decoder.JSONDecodeError:
            logger.error("Erro ao reconectar. Verifique suas credenciais.")
            from bot.utils import emitir_alerta_sonoro
            emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
            return
        tentativas_reconexao += 1
        await asyncio.sleep(5)
    
    if not Iq.check_connect():
        logger.error("Não foi possível conectar após várias tentativas. Encerrando...")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return

    logger.info("Conectado na conta demo")
    logger.info("")
    logger.info("NOTA: Podem aparecer erros de threading da biblioteca iqoptionapi")
    logger.info("      Estes erros nao afetam as operacoes binarias - ignore-os")
    logger.info("")
    
    # Obter saldo inicial
    saldo_inicial = 0
    try:
        saldo_inicial = Iq.get_balance()
        logger.info(f"Saldo conta PRÁTICA: ${saldo_inicial:.2f}")
        
        # Chamar callback de balance se fornecido
        if balance_callback:
            balance_callback(saldo_inicial, is_initial=True)
    except Exception as e:
        logger.warning(f"Não foi possível obter saldo da PRÁTICA: {e}")
    
    print()
    print("="*60)
    print(f"✅ CONECTADO COM SUCESSO!")
    print(f"   Saldo: ${saldo_inicial:.2f}")
    print("="*60)
    print()
    print("Agora vamos configurar as estratégias e proteções...")
    print()
    
    # SOLICITAR CONFIGURAÇÕES APÓS CONECTAR
    from bot.utils import solicitar_stop_win
    from bot.estrategias import solicitar_estrategia, solicitar_valor_entrada
    
    # Stop Loss
    if stop_loss_percentual_arg is None:
        try:
            print()
            print("="*60)
            print("  CONFIGURACAO DE STOP LOSS")
            print("="*60)
            print()
            print("Defina o percentual maximo de perda permitido.")
            print("Valor deve estar entre 1% e 10% da banca.")
            print()
            stop_loss_input = input("Stop Loss (%): ").strip()
            stop_loss_percentual = float(stop_loss_input)
        except (ValueError, KeyboardInterrupt):
            print()
            print("[ERRO] Valor invalido. Usando padrao de 10%")
            stop_loss_percentual = 10.0
        
        if stop_loss_percentual < 1 or stop_loss_percentual > 50:
            print()
            print(f"[ERRO] Stop loss de {stop_loss_percentual}% invalido!")
            print("Deve estar entre 1% e 50%. Usando padrao de 10%")
            stop_loss_percentual = 10.0
    else:
        stop_loss_percentual = stop_loss_percentual_arg
    
    # Stop Win
    stop_win_percentual = solicitar_stop_win()
    
    # Estratégia
    estrategia, parametros_estrategia = solicitar_estrategia()
    
    # Valor de entrada
    config_entrada = solicitar_valor_entrada(estrategia_escolhida=estrategia)
    
    # Carregar e validar sinais DEPOIS de configurar
    try:
        sinais = carregar_sinais(arquivo_sinais)
        logger.info(f"=== VALIDACAO CONCLUIDA ===")
        logger.info(f"Carregados {len(sinais)} sinais validos do arquivo")
        logger.info(f"===========================")
    except FileNotFoundError as e:
        logger.error(f"!!! ERRO CRITICO !!!")
        logger.error(f"{e}")
        logger.error(f"Verifique se o arquivo existe e o caminho esta correto")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except ValueError as e:
        logger.error(f"!!! ERROS NO ARQUIVO DE SINAIS !!!")
        logger.error(f"{e}")
        logger.error(f"Corrija os erros acima e reinicie o bot")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except Exception as e:
        logger.error(f"!!! ERRO DESCONHECIDO !!!")
        logger.error(f"{e}")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    
    # Calcular valor de entrada base (fixo ou % da banca)
    from bot.estrategias import calcular_valor_entrada_base, exibir_resumo_estrategia, aplicar_estrategia_ao_sinal
    if config_entrada is None:
        config_entrada = {"tipo": "fixo", "valor": 10.0}
    
    valor_entrada_base = calcular_valor_entrada_base(config_entrada, saldo_inicial)
    logger.info(f"")
    logger.info(f"=== VALOR DE ENTRADA CONFIGURADO ===")
    if config_entrada["tipo"] == "percentual":
        logger.info(f"Tipo: {config_entrada['valor']}% da banca")
        logger.info(f"Valor atual: ${valor_entrada_base:.2f} (banca: ${saldo_inicial:.2f})")
        logger.info(f"IMPORTANTE: Valor sera recalculado conforme banca muda")
    else:
        logger.info(f"Tipo: Valor fixo")
        logger.info(f"Valor: ${valor_entrada_base:.2f}")
    logger.info(f"====================================")
    logger.info(f"")
    
    # Exibir resumo da estratégia com saldo real
    if parametros_estrategia is None:
        parametros_estrategia = {"nivel": 2, "multiplicador": 2.0}
    exibir_resumo_estrategia(estrategia, parametros_estrategia, saldo_inicial)
    logger.info(f"Estrategia selecionada: {estrategia}")
    
    # Aplicar estratégia aos sinais (se necessário)
    indice_ciclo_masaniello = 0
    gerenciador_soros = None
    
    if estrategia == "Soros":
        # Criar gerenciador Soros para controle dinâmico usando valor_entrada_base
        from bot.estrategias import GerenciadorSoros
        gerenciador_soros = GerenciadorSoros(
            valor_entrada_base,  # Usa o valor calculado (fixo ou %)
            parametros_estrategia.get("payout", 0.87)
        )
        logger.info(f"Gerenciador Soros inicializado:")
        logger.info(f"  Valor base: ${gerenciador_soros.valor_base:.2f}")
        logger.info(f"  Payout: 87%")
        logger.info(f"  Max sequencia: 3 entradas")
        logger.info(f"IMPORTANTE: Valores crescem com WINs, voltam ao base com LOSS")
    
    elif estrategia == "Masaniello":
        logger.info(f"Aplicando estrategia Masaniello aos sinais...")
        for idx, sinal in enumerate(sinais):
            # Masaniello calcula seus próprios valores baseado no valor de entrada
            sinal["valor_entrada"] = valor_entrada_base  # Define valor base
            sinais[idx] = aplicar_estrategia_ao_sinal(
                sinal, estrategia, parametros_estrategia, saldo_inicial, indice_ciclo_masaniello
            )
            indice_ciclo_masaniello = (indice_ciclo_masaniello + 1) % parametros_estrategia["quantidade_entradas"]
    
    elif estrategia == "Martingale":
        # Martingale: aplicar valor base e calcular proteções
        logger.info(f"Aplicando estrategia Martingale aos sinais...")
        for idx, sinal in enumerate(sinais):
            sinal["valor_entrada"] = valor_entrada_base
            sinais[idx] = aplicar_estrategia_ao_sinal(
                sinal, estrategia, parametros_estrategia, saldo_inicial, 0
            )

    # Configurações de proteção
    STOP_LOSS_PERCENTUAL = stop_loss_percentual  # Percentual configurável (1-50%)
    LIMITE_MAXIMO_POR_OPERACAO = 50.0  # Maximo 50% do saldo atual por operacao
    PAUSA_APOS_6_LOSS = 6  # Pausar 2 sinais após 6 LOSS consecutivos
    PAUSA_APOS_2_CONJUNTOS_3_LOSS = 2  # Pausar após 2 conjuntos de 3 LOSS
    SINAIS_PARA_PULAR = 2  # Quantidade de sinais a pular na pausa
    
    loss_consecutivos = 0
    conjuntos_3_loss = 0  # Contador de vezes que teve 3 LOSS seguidos
    sinais_pausados = 0  # Contador de sinais que ainda precisa pular
    perda_acumulada = 0.0
    
    logger.info(f"=== PROTECOES ATIVADAS ===")
    logger.info(f"Pausa apos 6 LOSS consecutivos: Pula {SINAIS_PARA_PULAR} sinais")
    logger.info(f"Pausa apos 2 conjuntos de 3 LOSS: Pula {SINAIS_PARA_PULAR} sinais")
    logger.info(f"Stop Loss: {STOP_LOSS_PERCENTUAL}% da banca (DINAMICO)")
    logger.info(f"Limite por operacao: {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
    logger.info(f"Banca inicial: ${saldo_inicial:.2f} | Limite inicial: ${saldo_inicial * STOP_LOSS_PERCENTUAL / 100:.2f}")
    logger.info(f"IMPORTANTE: Limites sao recalculados conforme saldo atual muda")
    logger.info(f"==========================")
    
    # Exibir lista de sinais
    logger.info(f"")
    logger.info(f"=== SINAIS PROGRAMADOS ({len(sinais)}) ===")
    for idx, sinal in enumerate(sinais, 1):
        p1 = f"${sinal['protecao1']:.2f}" if sinal.get('protecao1') else "N/A"
        p2 = f"${sinal['protecao2']:.2f}" if sinal.get('protecao2') else "N/A"
        logger.info(f"{idx:2d}. {sinal['hora']:02d}:{sinal['minuto']:02d} | {sinal['ativo']:15s} | {sinal['tipo']:4s} | M{sinal['tempo_minutos']:2d} | Entrada: ${sinal['valor_entrada']:7.2f} | P1: {p1:8s} | P2: {p2:8s}")
    logger.info(f"{'='*100}")
    logger.info(f"")

    # Importar funções auxiliares
    from bot.utils import executar_operacao_com_resultado, emitir_alerta_sonoro, verificar_sinais_pendentes, verificar_seguranca_operacao

    # Resetar flag global e iniciar thread de comando de parada
    global parar_bot
    parar_bot = False
    thread_parada = threading.Thread(target=aguardar_comando_parada, daemon=True)
    thread_parada.start()
    
    logger.info("="*60)
    logger.info("Bot iniciado! Aguardando sinais...")
    logger.info("Para parar o bot a qualquer momento, digite 'S' quando solicitado")
    logger.info("="*60)
    print("\n" + "="*60)
    print("🤖 BOT DEMO INICIADO!")
    print("="*60)
    print("Para parar o bot a qualquer momento, digite 'S' quando solicitado")
    print("="*60 + "\n")

    while True:
        try:
            # Verificar flag de parada
            if parar_bot or (stop_callback and stop_callback()):
                logger.info("Comando de parada recebido. Encerrando bot DEMO...")
                emitir_alerta_sonoro(repeticoes=2, duracao_ms=300)
                break
            
            # Verificar conexão
            if not Iq.check_connect():
                logger.warning("Conexão perdida, tentando reconectar...")
                Iq.connect()
                await asyncio.sleep(5)
                continue
            
            # Obter hora atual
            agora = datetime.now()
            hora_atual = agora.hour
            minuto_atual = agora.minute
            
            # Obter saldo atual para recalcular stop loss dinamicamente
            try:
                saldo_atual = Iq.get_balance()
            except:
                saldo_atual = saldo_inicial  # Fallback se falhar
            
            # Chamar callback de balance se fornecido
            if balance_callback:
                balance_callback(saldo_atual, is_initial=False)

            # VERIFICAR STOP WIN
            from bot.utils import verificar_stop_win_atingido, registrar_stop_win
            atingiu_stop_win, lucro_atual, percentual_lucro = verificar_stop_win_atingido(
                saldo_atual, saldo_inicial, stop_win_percentual
            )
            
            if atingiu_stop_win:
                logger.info("="*60)
                logger.info("STOP WIN ATINGIDO!")
                logger.info("="*60)
                logger.info(f"Banca Inicial: ${saldo_inicial:.2f}")
                logger.info(f"Banca Atual: ${saldo_atual:.2f}")
                logger.info(f"Lucro: ${lucro_atual:.2f} ({percentual_lucro:.2f}%)")
                logger.info(f"Meta: {stop_win_percentual}%")
                logger.info("")
                logger.info("Parabens! Voce atingiu seu objetivo de lucro!")
                logger.info("O bot sera encerrado e bloqueado por 24 horas")
                logger.info("para proteger seus ganhos.")
                logger.info("="*60)
                
                print("\n" + "="*60)
                print("PARABENS! STOP WIN ATINGIDO!")
                print("="*60)
                print(f"Banca Inicial: ${saldo_inicial:.2f}")
                print(f"Banca Final: ${saldo_atual:.2f}")
                print(f"Lucro: ${lucro_atual:.2f} ({percentual_lucro:.2f}%)")
                print(f"Meta: {stop_win_percentual}%")
                print("")
                print("IMPORTANTE:")
                print("   - Bot sera bloqueado por 24 horas")
                print("   - Isto protege seus lucros contra operacoes emocionais")
                print("   - Aproveite seu lucro com sabedoria!")
                print("="*60 + "\n")
                
                # Registrar bloqueio
                registrar_stop_win(email, lucro_atual, stop_win_percentual, saldo_inicial)
                
                # Alerta sonoro de vitória
                emitir_alerta_sonoro(repeticoes=5, duracao_ms=200)
                break
            
            
            # Verificar proteção de stop loss por percentual DINAMICO
            if saldo_inicial > 0 and saldo_atual > 0:
                percentual_perda = ((saldo_inicial - saldo_atual) / saldo_inicial) * 100
                
                # Mostrar status periodicamente
                if minuto_atual % 10 == 0:
                    logger.info(f"[Status] Saldo: ${saldo_atual:.2f} | Variacao: {percentual_perda:+.2f}% | Perda contabilizada: ${perda_acumulada:.2f}")
                
                # Verificar se ultrapassou limite percentual
                if percentual_perda >= STOP_LOSS_PERCENTUAL:
                    perda_real = saldo_inicial - saldo_atual
                    logger.error(f"!!! STOP LOSS DINAMICO ATINGIDO: Perda de {percentual_perda:.2f}% da banca !!!")
                    logger.error(f"Banca inicial: ${saldo_inicial:.2f} | Saldo atual: ${saldo_atual:.2f} | Perda: ${perda_real:.2f}")
                    emitir_alerta_sonoro(repeticoes=5, duracao_ms=800)
                    break
            
            # Verificar se ainda há sinais pendentes
            if not verificar_sinais_pendentes(sinais, hora_atual, minuto_atual):
                logger.info("=== TODOS OS SINAIS FORAM EXECUTADOS ===")
                logger.info(f"Bot DEMO finalizado. Resultado final: ${-perda_acumulada:.2f}")
                emitir_alerta_sonoro(repeticoes=3, duracao_ms=400)
                break
            
            # Verificar se há sinal agendado para agora
            sinal = verificar_sinal_agendado(sinais, hora_atual, minuto_atual)
            
            if sinal:
                # Marcar sinal como sendo processado
                sinal["executado"] = True
                
                # Verificar se está em pausa (pulando sinais)
                if sinais_pausados > 0:
                    logger.warning(f"[PAUSA] Pulando sinal por seguranca. Sinais restantes para pular: {sinais_pausados}")
                    sinais_pausados -= 1
                    if sinais_pausados == 0:
                        logger.info(f"[PAUSA] Fim da pausa. Zerando contadores e voltando a operar...")
                        loss_consecutivos = 0
                        conjuntos_3_loss = 0
                    continue
                
                ativo = sinal["ativo"]
                tipo = sinal["tipo"]
                tempo_minutos = sinal["tempo_minutos"]
                
                # SOROS: Obter valor dinâmico do gerenciador
                if gerenciador_soros:
                    valor_entrada = gerenciador_soros.calcular_proximo_valor()
                    protecao1 = None  # Soros não usa proteções
                    protecao2 = None
                    logger.info(f"[SOROS] {gerenciador_soros.get_info()}")
                else:
                    valor_entrada = sinal["valor_entrada"]
                    protecao1 = sinal.get("protecao1")
                    protecao2 = sinal.get("protecao2")
                
                # Normalizar nome do ativo
                ativo_normalizado = normalizar_ativo(ativo)
                logger.info(f"SINAL DEMO encontrado: {tipo} em {ativo} ({ativo_normalizado}) por {tempo_minutos} min")
                from bot.utils import print_info_user
                print_info_user(f"Sinal encontrado: {tipo} em {ativo} por {tempo_minutos} minuto(s)")
                p1_str = f"${protecao1:.2f}" if protecao1 else "N/A"
                p2_str = f"${protecao2:.2f}" if protecao2 else "N/A"
                logger.info(f"Entrada: ${valor_entrada:.2f} | Protecao 1: {p1_str} | Protecao 2: {p2_str}")
                
                # Executar entrada principal
                try:
                    # Obter saldo atual para verificação dinâmica
                    try:
                        saldo_atual = Iq.get_balance()
                    except:
                        saldo_atual = saldo_inicial
                    
                    # PRE-VERIFICACAO DE SEGURANCA: Verificar se pode arriscar este valor
                    seguro, limite_valor, margem_disponivel = verificar_seguranca_operacao(
                        valor_entrada, saldo_atual, LIMITE_MAXIMO_POR_OPERACAO
                    )
                    
                    if not seguro:
                        logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO !!!")
                        logger.error(f"Entrada de ${valor_entrada:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                        logger.error(f"Saldo atual: ${saldo_atual:.2f} | Limite maximo por operacao: ${limite_valor:.2f}")
                        logger.error(f"Valor solicitado ({valor_entrada:.2f}) > Limite ({limite_valor:.2f})")
                        logger.error(f"Bot encerrado por seguranca preventiva")
                        emitir_alerta_sonoro(repeticoes=5, duracao_ms=800)
                        return
                    
                    logger.info(f">>> ENTRADA PRINCIPAL: ${valor_entrada:.2f} [Saldo: ${saldo_atual:.2f} | Max: ${limite_valor:.2f} | Margem: ${margem_disponivel:.2f}]")
                    resultado, diferenca = await executar_operacao_com_resultado(
                        Iq, valor_entrada, ativo_normalizado, tipo, tempo_minutos, logger, asyncio, sons_habilitados
                    )
                    
                    try:
                        salvar_resultado_operacao(ativo_normalizado, time.time(), resultado, 
                                                 ganho=diferenca if diferenca > 0 else None, 
                                                 perda=abs(diferenca) if diferenca < 0 else None)
                    except Exception:
                        pass
                    
                    # Processar resultado da entrada principal
                    from bot.utils import processar_resultado_operacao
                    
                    if resultado == "ERROR":
                        #logger.warning(f"[!] ERRO TECNICO - Operacao nao executada, nao conta como LOSS")
                        logger.warning(f"[!] ATIVO FECHADO")
                        logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                        continue
                    
                    if resultado == "WIN":
                        logger.info(f"=== OPERACAO FINALIZADA COM WIN! Lucro total: ${diferenca:.2f}")
                        from bot.utils import print_success_user
                        print_success_user(f"Operação WIN! Lucro: ${diferenca:.2f}")
                        loss_consecutivos = 0
                        
                        # SOROS: Registrar WIN e calcular próximo valor
                        if gerenciador_soros:
                            gerenciador_soros.registrar_win(valor_entrada)
                            logger.info(f"[SOROS] Proximo valor: ${gerenciador_soros.calcular_proximo_valor():.2f}")
                        
                        logger.info(f"[Protecao] LOSS consecutivos: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                        continue
                    
                    # Se perdeu e tem proteção 1, executar
                    if resultado == "LOSS" and protecao1:
                        # Obter saldo atual após entrada principal
                        try:
                            saldo_atual_p1 = Iq.get_balance()
                        except:
                            saldo_atual_p1 = saldo_inicial
                        
                        # PRE-VERIFICACAO: Verificar proteção 1 com saldo atual
                        seguro_p1, limite_valor_p1, margem_disp_p1 = verificar_seguranca_operacao(
                            protecao1, saldo_atual_p1, LIMITE_MAXIMO_POR_OPERACAO
                        )
                        
                        if not seguro_p1:
                            logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO NA PROTECAO 1 !!!")
                            logger.error(f"Protecao 1 de ${protecao1:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                            logger.error(f"Saldo atual: ${saldo_atual_p1:.2f} | Limite maximo: ${limite_valor_p1:.2f}")
                            logger.error(f"Pulando protecao 1 por seguranca. Contabilizando LOSS da entrada principal.")
                            # Contabilizar apenas a perda da entrada principal
                            loss_consecutivos += 1
                            perda_acumulada += abs(diferenca)
                            logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        logger.info(f">>> PROTECAO 1: ${protecao1:.2f} [Saldo: ${saldo_atual_p1:.2f} | Max: ${limite_valor_p1:.2f}]")
                        resultado_p1, diferenca_p1 = await executar_operacao_com_resultado(
                            Iq, protecao1, ativo_normalizado, tipo, tempo_minutos, logger, asyncio
                        )
                        
                        try:
                            salvar_resultado_operacao(ativo_normalizado, time.time(), resultado_p1 + "_P1", 
                                                     ganho=diferenca_p1 if diferenca_p1 > 0 else None, 
                                                     perda=abs(diferenca_p1) if diferenca_p1 < 0 else None)
                        except Exception:
                            pass
                        
                        # Se proteção 1 deu erro técnico
                        if resultado_p1 == "ERROR":
                            #logger.warning(f"[!] ERRO TECNICO na Protecao 1 - nao conta como LOSS")
                            logger.warning(f"[!] ATIVO FECHADO")
                            logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        # Se proteção 1 ganhou
                        if resultado_p1 == "WIN":
                            lucro_total = diferenca + diferenca_p1
                            logger.info(f"=== PROTECAO 1 WIN! Lucro total: ${lucro_total:.2f}")
                            # Resetar todos os contadores
                            loss_consecutivos = 0
                            conjuntos_3_loss = 0
                            logger.info(f"[Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        # Se proteção 1 perdeu e tem proteção 2, executar
                        if resultado_p1 == "LOSS" and protecao2:
                            # Obter saldo atual após proteção 1
                            try:
                                saldo_atual_p2 = Iq.get_balance()
                            except:
                                saldo_atual_p2 = saldo_inicial
                            
                            # PRE-VERIFICACAO: Verificar proteção 2 com saldo atual
                            seguro_p2, limite_valor_p2, margem_disp_p2 = verificar_seguranca_operacao(
                                protecao2, saldo_atual_p2, LIMITE_MAXIMO_POR_OPERACAO
                            )
                            
                            if not seguro_p2:
                                logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO NA PROTECAO 2 !!!")
                                logger.error(f"Protecao 2 de ${protecao2:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                                logger.error(f"Saldo atual: ${saldo_atual_p2:.2f} | Limite maximo: ${limite_valor_p2:.2f}")
                                logger.error(f"Pulando protecao 2 por seguranca. Contabilizando LOSS acumulado ate P1.")
                                # Contabilizar perda da entrada + P1
                                prejuizo_total = abs(diferenca + diferenca_p1)
                                loss_consecutivos += 1
                                perda_acumulada += prejuizo_total
                                
                                if loss_consecutivos % 3 == 0:
                                    conjuntos_3_loss += 1
                                    logger.warning(f"[ALERTA] Conjunto de 3 LOSS detectado! Total: {conjuntos_3_loss}")
                                
                                if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                    logger.warning(f"[PAUSA] 6 LOSS atingidos! Pausando {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                    logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS! Pausando {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                
                                logger.warning(f"[Protecao] LOSS: {loss_consecutivos} | Conjuntos: {conjuntos_3_loss} | Perda: ${perda_acumulada:.2f}")
                                continue
                            
                            logger.info(f">>> PROTECAO 2: ${protecao2:.2f} [Saldo: ${saldo_atual_p2:.2f} | Max: ${limite_valor_p2:.2f}]")
                            resultado_p2, diferenca_p2 = await executar_operacao_com_resultado(
                                Iq, protecao2, ativo_normalizado, tipo, tempo_minutos, logger, asyncio
                            )
                            
                            try:
                                salvar_resultado_operacao(ativo_normalizado, time.time(), resultado_p2 + "_P2", 
                                                         ganho=diferenca_p2 if diferenca_p2 > 0 else None, 
                                                         perda=abs(diferenca_p2) if diferenca_p2 < 0 else None)
                            except Exception:
                                pass
                            
                            # Se proteção 2 deu erro técnico
                            if resultado_p2 == "ERROR":
                               #logger.warning(f"[!] ERRO TECNICO na Protecao 2 - nao conta como LOSS")
                                logger.warning(f"[!] ATIVO FECHADO")
                                logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                                continue
                            
                            lucro_total = diferenca + diferenca_p1 + diferenca_p2
                            if resultado_p2 == "WIN":
                                logger.info(f"=== PROTECAO 2 WIN! Lucro total: ${lucro_total:.2f}")
                                # Resetar todos os contadores
                                loss_consecutivos = 0
                                conjuntos_3_loss = 0
                                logger.info(f"[Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                            else:
                                logger.info(f"XXX TODAS PROTECOES PERDIDAS! Prejuizo total: ${abs(lucro_total):.2f}")
                                
                                # SOROS: Registrar LOSS e voltar ao valor base
                                if gerenciador_soros:
                                    gerenciador_soros.registrar_loss()
                                    logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                                
                                # Incrementar LOSS consecutivos e perda acumulada
                                loss_consecutivos += 1
                                perda_acumulada += abs(lucro_total)
                                
                                # Verificar se completou conjunto de 3 LOSS
                                if loss_consecutivos % 3 == 0:
                                    conjuntos_3_loss += 1
                                    logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                                
                                # Verificar se precisa pausar
                                if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                    logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                    logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                
                                logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                        else:
                            # Sem proteção 2 ou não definida
                            prejuizo_total = abs(diferenca + diferenca_p1)
                            logger.info(f"XXX PROTECAO 1 PERDIDA! Prejuizo total: ${prejuizo_total:.2f}")
                            
                            # SOROS: Registrar LOSS e voltar ao valor base
                            if gerenciador_soros:
                                gerenciador_soros.registrar_loss()
                                logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                            
                            # Incrementar LOSS consecutivos e perda acumulada
                            loss_consecutivos += 1
                            perda_acumulada += prejuizo_total
                            
                            # Verificar se completou conjunto de 3 LOSS
                            if loss_consecutivos % 3 == 0:
                                conjuntos_3_loss += 1
                                logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                            
                            # Verificar se precisa pausar
                            if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                sinais_pausados = SINAIS_PARA_PULAR
                            elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                sinais_pausados = SINAIS_PARA_PULAR
                            
                            logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                    else:
                        # Sem proteção 1 ou não definida
                        logger.info(f"XXX OPERACAO FINALIZADA COM LOSS! Prejuizo total: ${abs(diferenca):.2f}")
                        
                        # SOROS: Registrar LOSS e voltar ao valor base
                        if gerenciador_soros:
                            gerenciador_soros.registrar_loss()
                            logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                        
                        # Incrementar LOSS consecutivos e perda acumulada
                        loss_consecutivos += 1
                        perda_acumulada += abs(diferenca)
                        
                        # Verificar se completou conjunto de 3 LOSS
                        if loss_consecutivos % 3 == 0:
                            conjuntos_3_loss += 1
                            logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                        
                        # Verificar se precisa pausar
                        if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                            logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                            sinais_pausados = SINAIS_PARA_PULAR
                        elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                            logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                            sinais_pausados = SINAIS_PARA_PULAR
                        
                        logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")

                except Exception as e:
                    logger.error(f"Erro ao executar operacao DEMO: {e}")
            else:
                # Log apenas a cada 5 minutos para não poluir
                if minuto_atual % 5 == 0:
                    logger.info(f"Aguardando sinais... Hora atual: {hora_atual:02d}:{minuto_atual:02d}")
                    from bot.utils import print_user
                    print_user(f"⏰ Aguardando sinais... {hora_atual:02d}:{minuto_atual:02d}")

            # Aguardar 1 minuto antes da próxima verificação
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Erro no loop DEMO: {e}")
            logger.warning("Tentando reconectar...")
            try:
                Iq.connect()
            except Exception as reconnect_error:
                logger.error(f"Erro na reconexão: {reconnect_error}")
            await asyncio.sleep(10)


async def executar_real(arquivo_sinais, logger, email, senha, stop_loss_percentual_arg=None, sons_habilitados=True, balance_callback=None, stop_callback=None):
    logger.info(f"Iniciando modo REAL com arquivo de sinais: {arquivo_sinais}")
    
    # VERIFICAR BLOQUEIO POR STOP WIN
    from bot.utils import verificar_bloqueio_stop_win
    bloqueado, horas_restantes, lucro_anterior = verificar_bloqueio_stop_win(email)
    
    if bloqueado:
        logger.error("="*60)
        logger.error("STOP WIN ATIVO - BOT BLOQUEADO!")
        logger.error("="*60)
        logger.error(f"Voce atingiu o Stop Win anteriormente e ganhou ${lucro_anterior:.2f}")
        logger.error(f"O bot esta bloqueado por mais {horas_restantes:.1f} horas")
        logger.error(f"para proteger seus lucros e evitar operacoes emocionais.")
        logger.error("")
        logger.error("Volte apos o periodo de bloqueio para operar novamente.")
        logger.error("="*60)
        print("\n" + "="*60)
        print("STOP WIN ATIVO - BOT BLOQUEADO!")
        print("="*60)
        print(f"Voce atingiu o Stop Win e ganhou ${lucro_anterior:.2f}")
        print(f"Bloqueio restante: {horas_restantes:.1f} horas")
        print("")
        print("Este bloqueio protege seus lucros!")
        print("Volte apos o periodo para operar novamente.")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=500)
        return
    
    if not email or not senha:
        logger.error("Credenciais nao fornecidas. Encerrando...")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return

    logger.info("Criando sessão IQ_Option (REAL) e conectando...")
    logger.info("Aguardando 3 segundos para estabilizar conexao...")
    await asyncio.sleep(3)
    
    Iq = IQ_Option(email, senha)
    
    try:
        logger.info("Tentando conectar...")
        Iq.connect()
        logger.info("Conexao estabelecida com sucesso!")
    except ConnectionError as e:
        logger.error("="*60)
        logger.error("ERRO DE CONEXAO COM IQ OPTION")
        logger.error("="*60)
        logger.error(f"Mensagem: {e}")
        logger.error("")
        logger.error("Possíveis causas:")
        logger.error("1. Problema de internet/firewall")
        logger.error("2. Servidores da IQ Option instáveis")
        logger.error("3. Muitas tentativas de conexão seguidas")
        logger.error("")
        logger.error("Solucoes:")
        logger.error("- Verifique sua conexao com a internet")
        logger.error("- Aguarde 1-2 minutos e tente novamente")
        logger.error("- Reinicie seu modem/roteador se necessário")
        logger.error("="*60)
        print("\n" + "="*60)
        print("❌ ERRO DE CONEXAO COM IQ OPTION")
        print("="*60)
        print("\nPossíveis causas:")
        print("  1. Problema de internet/firewall")
        print("  2. Servidores da IQ Option instáveis")
        print("  3. Muitas tentativas de conexão seguidas")
        print("\nSolucoes:")
        print("  ✓ Verifique sua conexao com a internet")
        print("  ✓ Aguarde 1-2 minutos e tente novamente")
        print("  ✓ Reinicie seu modem/roteador se necessário")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except json.decoder.JSONDecodeError as e:
        logger.error("="*60)
        logger.error("ERRO DE AUTENTICACAO NA IQ OPTION")
        logger.error("="*60)
        logger.error("Possíveis causas:")
        logger.error("1. Email ou senha incorretos")
        logger.error("2. Conta bloqueada ou com verificação pendente")
        logger.error("3. IQ Option mudou o processo de autenticação")
        logger.error("4. Problema temporário nos servidores da IQ Option")
        logger.error("")
        logger.error("Solucoes:")
        logger.error("- Verifique suas credenciais no site da IQ Option")
        logger.error("- Acesse sua conta pelo navegador para verificar se há algum aviso")
        logger.error("- Tente novamente em alguns minutos")
        logger.error("="*60)
        print("\n" + "="*60)
        print("❌ ERRO DE AUTENTICACAO NA IQ OPTION")
        print("="*60)
        print("\nPossíveis causas:")
        print("  1. Email ou senha incorretos")
        print("  2. Conta bloqueada ou com verificação pendente")
        print("  3. IQ Option mudou o processo de autenticação")
        print("  4. Problema temporário nos servidores da IQ Option")
        print("\nSolucoes:")
        print("  ✓ Verifique suas credenciais no site da IQ Option")
        print("  ✓ Acesse sua conta pelo navegador para verificar se há algum aviso")
        print("  ✓ Tente novamente em alguns minutos")
        print("  ✓ Se o problema persistir, contate o suporte da IQ Option")
        print("="*60 + "\n")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except Exception as e:
        erro_msg = str(e)
        logger.error(f"Erro inesperado ao conectar: {erro_msg}")
        
        # Tratamento específico para "Connection already closed"
        if "Connection is already closed" in erro_msg or "already closed" in erro_msg.lower():
            logger.error("")
            logger.error("="*60)
            logger.error("ERRO: CONEXAO JA FECHADA")
            logger.error("="*60)
            logger.error("Este erro ocorre quando a biblioteca tenta usar")
            logger.error("uma conexao que ja foi encerrada.")
            logger.error("")
            logger.error("SOLUCOES:")
            logger.error("1. AGUARDE 2-3 MINUTOS antes de tentar novamente")
            logger.error("2. Feche TODOS os terminais/janelas do bot")
            logger.error("3. Abra uma NOVA janela e execute novamente")
            logger.error("4. Se persistir, reinicie seu computador")
            logger.error("="*60)
            print("\n" + "="*60)
            print("⚠️  ERRO: CONEXAO JA FECHADA")
            print("="*60)
            print("\nEste erro ocorre por tentativas muito rapidas.")
            print("")
            print("SOLUCOES:")
            print("  1. AGUARDE 2-3 MINUTOS")
            print("  2. Feche TODAS as janelas do bot")
            print("  3. Abra uma NOVA janela")
            print("  4. Execute novamente")
            print("")
            print("IMPORTANTE: Nao tente reconectar imediatamente!")
            print("="*60 + "\n")
        
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    
    try:
        Iq.change_balance("REAL")
    except Exception:
        pass

    # Reconnect automático
    tentativas_reconexao = 0
    max_tentativas = 3
    while not Iq.check_connect() and tentativas_reconexao < max_tentativas:
        logger.warning(f"Tentando reconectar na IQ Option... (tentativa {tentativas_reconexao + 1}/{max_tentativas})")
        try:
            Iq.connect()
        except json.decoder.JSONDecodeError:
            logger.error("Erro ao reconectar. Verifique suas credenciais.")
            from bot.utils import emitir_alerta_sonoro
            emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
            return
        tentativas_reconexao += 1
        await asyncio.sleep(5)
    
    if not Iq.check_connect():
        logger.error("Não foi possível conectar após várias tentativas. Encerrando...")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return

    logger.info("Conectado na conta REAL")
    logger.info("")
    logger.info("NOTA: Podem aparecer erros de threading da biblioteca iqoptionapi")
    logger.info("      Estes erros nao afetam as operacoes binarias - ignore-os")
    logger.info("")
    
    # Obter saldo inicial
    saldo_inicial = 0
    try:
        saldo_inicial = Iq.get_balance()
        logger.info(f"Saldo conta REAL: ${saldo_inicial:.2f}")
        
        # Chamar callback de balance se fornecido
        if balance_callback:
            balance_callback(saldo_inicial, is_initial=True)
    except Exception as e:
        logger.warning(f"Não foi possível obter saldo da REAL: {e}")
    
    print()
    print("="*60)
    print(f"✅ CONECTADO COM SUCESSO!")
    print(f"   Saldo REAL: ${saldo_inicial:.2f}")
    print("="*60)
    print()
    print("⚠️  ATENCAO: Voce esta operando com DINHEIRO REAL!")
    print()
    print("Agora vamos configurar as estrategias e protecoes...")
    print()
    
    # SOLICITAR CONFIGURAÇÕES APÓS CONECTAR
    from bot.utils import solicitar_stop_win
    from bot.estrategias import solicitar_estrategia, solicitar_valor_entrada
    
    # Stop Loss
    if stop_loss_percentual_arg is None:
        try:
            print()
            print("="*60)
            print("  CONFIGURACAO DE STOP LOSS")
            print("="*60)
            print()
            print("Defina o percentual maximo de perda permitido.")
            print("Valor deve estar entre 1% e 10% da banca.")
            print()
            stop_loss_input = input("Stop Loss (%): ").strip()
            stop_loss_percentual = float(stop_loss_input)
        except (ValueError, KeyboardInterrupt):
            print()
            print("[ERRO] Valor invalido. Usando padrao de 10%")
            stop_loss_percentual = 10.0
        
        if stop_loss_percentual < 1 or stop_loss_percentual > 50:
            print()
            print(f"[ERRO] Stop loss de {stop_loss_percentual}% invalido!")
            print("Deve estar entre 1% e 50%. Usando padrao de 10%")
            stop_loss_percentual = 10.0
    else:
        stop_loss_percentual = stop_loss_percentual_arg
    
    # Stop Win
    stop_win_percentual = solicitar_stop_win()
    
    # Estratégia
    estrategia, parametros_estrategia = solicitar_estrategia()
    
    # Valor de entrada
    config_entrada = solicitar_valor_entrada(estrategia_escolhida=estrategia)
    
    # Carregar e validar sinais DEPOIS de configurar
    try:
        sinais = carregar_sinais(arquivo_sinais)
        logger.info(f"=== VALIDACAO CONCLUIDA ===")
        logger.info(f"Carregados {len(sinais)} sinais validos do arquivo")
        logger.info(f"===========================")
    except FileNotFoundError as e:
        logger.error(f"!!! ERRO CRITICO !!!")
        logger.error(f"{e}")
        logger.error(f"Verifique se o arquivo existe e o caminho esta correto")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except ValueError as e:
        logger.error(f"!!! ERROS NO ARQUIVO DE SINAIS !!!")
        logger.error(f"{e}")
        logger.error(f"Corrija os erros acima e reinicie o bot")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    except Exception as e:
        logger.error(f"!!! ERRO DESCONHECIDO !!!")
        logger.error(f"{e}")
        from bot.utils import emitir_alerta_sonoro
        emitir_alerta_sonoro(repeticoes=3, duracao_ms=1000)
        return
    
    # Calcular valor de entrada base (fixo ou % da banca)
    from bot.estrategias import calcular_valor_entrada_base, exibir_resumo_estrategia, aplicar_estrategia_ao_sinal
    if config_entrada is None:
        config_entrada = {"tipo": "fixo", "valor": 10.0}
    
    valor_entrada_base = calcular_valor_entrada_base(config_entrada, saldo_inicial)
    logger.info(f"")
    logger.info(f"=== VALOR DE ENTRADA CONFIGURADO ===")
    if config_entrada["tipo"] == "percentual":
        logger.info(f"Tipo: {config_entrada['valor']}% da banca")
        logger.info(f"Valor atual: ${valor_entrada_base:.2f} (banca: ${saldo_inicial:.2f})")
        logger.info(f"IMPORTANTE: Valor sera recalculado conforme banca muda")
    else:
        logger.info(f"Tipo: Valor fixo")
        logger.info(f"Valor: ${valor_entrada_base:.2f}")
    logger.info(f"====================================")
    logger.info(f"")
    
    # Exibir resumo da estratégia com saldo real
    if parametros_estrategia is None:
        parametros_estrategia = {"nivel": 2, "multiplicador": 2.0}
    exibir_resumo_estrategia(estrategia, parametros_estrategia, saldo_inicial)
    logger.info(f"Estrategia selecionada: {estrategia}")
    
    # Aplicar estratégia aos sinais (se necessário)
    indice_ciclo_masaniello = 0
    gerenciador_soros = None
    
    if estrategia == "Soros":
        # Criar gerenciador Soros para controle dinâmico usando valor_entrada_base
        from bot.estrategias import GerenciadorSoros
        gerenciador_soros = GerenciadorSoros(
            valor_entrada_base,  # Usa o valor calculado (fixo ou %)
            parametros_estrategia.get("payout", 0.87)
        )
        logger.info(f"Gerenciador Soros inicializado:")
        logger.info(f"  Valor base: ${gerenciador_soros.valor_base:.2f}")
        logger.info(f"  Payout: 87%")
        logger.info(f"  Max sequencia: 3 entradas")
        logger.info(f"IMPORTANTE: Valores crescem com WINs, voltam ao base com LOSS")
    
    elif estrategia == "Masaniello":
        logger.info(f"Aplicando estrategia Masaniello aos sinais...")
        for idx, sinal in enumerate(sinais):
            # Masaniello calcula seus próprios valores baseado no valor de entrada
            sinal["valor_entrada"] = valor_entrada_base  # Define valor base
            sinais[idx] = aplicar_estrategia_ao_sinal(
                sinal, estrategia, parametros_estrategia, saldo_inicial, indice_ciclo_masaniello
            )
            indice_ciclo_masaniello = (indice_ciclo_masaniello + 1) % parametros_estrategia["quantidade_entradas"]
    
    elif estrategia == "Martingale":
        # Martingale: aplicar valor base e calcular proteções
        logger.info(f"Aplicando estrategia Martingale aos sinais...")
        for idx, sinal in enumerate(sinais):
            sinal["valor_entrada"] = valor_entrada_base
            sinais[idx] = aplicar_estrategia_ao_sinal(
                sinal, estrategia, parametros_estrategia, saldo_inicial, 0
            )

    # Configurações de proteção
    STOP_LOSS_PERCENTUAL = stop_loss_percentual  # Percentual configurável (1-50%)
    LIMITE_MAXIMO_POR_OPERACAO = 50.0  # Maximo 50% do saldo atual por operacao
    PAUSA_APOS_6_LOSS = 6  # Pausar 2 sinais após 6 LOSS consecutivos
    PAUSA_APOS_2_CONJUNTOS_3_LOSS = 2  # Pausar após 2 conjuntos de 3 LOSS
    SINAIS_PARA_PULAR = 2  # Quantidade de sinais a pular na pausa
    
    loss_consecutivos = 0
    conjuntos_3_loss = 0  # Contador de vezes que teve 3 LOSS seguidos
    sinais_pausados = 0  # Contador de sinais que ainda precisa pular
    perda_acumulada = 0.0
    
    logger.info(f"=== PROTECOES ATIVADAS ===")
    logger.info(f"Pausa apos 6 LOSS consecutivos: Pula {SINAIS_PARA_PULAR} sinais")
    logger.info(f"Pausa apos 2 conjuntos de 3 LOSS: Pula {SINAIS_PARA_PULAR} sinais")
    logger.info(f"Stop Loss: {STOP_LOSS_PERCENTUAL}% da banca (DINAMICO)")
    logger.info(f"Limite por operacao: {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
    logger.info(f"Banca inicial: ${saldo_inicial:.2f} | Limite inicial: ${saldo_inicial * STOP_LOSS_PERCENTUAL / 100:.2f}")
    logger.info(f"IMPORTANTE: Limites sao recalculados conforme saldo atual muda")
    logger.info(f"==========================")
    
    # Exibir lista de sinais
    logger.info(f"")
    logger.info(f"=== SINAIS PROGRAMADOS ({len(sinais)}) ===")
    for idx, sinal in enumerate(sinais, 1):
        p1 = f"${sinal['protecao1']:.2f}" if sinal.get('protecao1') else "N/A"
        p2 = f"${sinal['protecao2']:.2f}" if sinal.get('protecao2') else "N/A"
        logger.info(f"{idx:2d}. {sinal['hora']:02d}:{sinal['minuto']:02d} | {sinal['ativo']:15s} | {sinal['tipo']:4s} | M{sinal['tempo_minutos']:2d} | Entrada: ${sinal['valor_entrada']:7.2f} | P1: {p1:8s} | P2: {p2:8s}")
    logger.info(f"{'='*100}")
    logger.info(f"")

    # Importar funções auxiliares
    from bot.utils import executar_operacao_com_resultado, emitir_alerta_sonoro, verificar_sinais_pendentes, verificar_seguranca_operacao

    # Resetar flag global e iniciar thread de comando de parada
    global parar_bot
    parar_bot = False
    thread_parada = threading.Thread(target=aguardar_comando_parada, daemon=True)
    thread_parada.start()
    
    logger.info("="*60)
    logger.info("Bot iniciado! Aguardando sinais...")
    logger.info("Para parar o bot a qualquer momento, digite 'S' quando solicitado")
    logger.info("="*60)
    print("\n" + "="*60)
    print("🤖 BOT REAL INICIADO!")
    print("="*60)
    print("⚠️  ATENÇÃO: Você está operando com DINHEIRO REAL!")
    print("Para parar o bot a qualquer momento, digite 'S' quando solicitado")
    print("="*60 + "\n")

    while True:
        try:
            # Verificar flag de parada
            if parar_bot:
                logger.info("Comando de parada recebido. Encerrando bot REAL...")
                emitir_alerta_sonoro(repeticoes=2, duracao_ms=300)
                break
            
            # Verificar conexão
            if not Iq.check_connect():
                logger.warning("Conexão perdida, tentando reconectar...")
                Iq.connect()
                await asyncio.sleep(5)
                continue
            
            # Obter hora atual
            agora = datetime.now()
            hora_atual = agora.hour
            minuto_atual = agora.minute
            
            # Obter saldo atual para recalcular stop loss dinamicamente
            try:
                saldo_atual = Iq.get_balance()
            except:
                saldo_atual = saldo_inicial  # Fallback se falhar
            
            # Chamar callback de balance se fornecido
            if balance_callback:
                balance_callback(saldo_atual, is_initial=False)

            # VERIFICAR STOP WIN
            from bot.utils import verificar_stop_win_atingido, registrar_stop_win
            atingiu_stop_win, lucro_atual, percentual_lucro = verificar_stop_win_atingido(
                saldo_atual, saldo_inicial, stop_win_percentual
            )
            
            if atingiu_stop_win:
                logger.info("="*60)
                logger.info("STOP WIN ATINGIDO!")
                logger.info("="*60)
                logger.info(f"Banca Inicial: ${saldo_inicial:.2f}")
                logger.info(f"Banca Atual: ${saldo_atual:.2f}")
                logger.info(f"Lucro: ${lucro_atual:.2f} ({percentual_lucro:.2f}%)")
                logger.info(f"Meta: {stop_win_percentual}%")
                logger.info("")
                logger.info("Parabens! Voce atingiu seu objetivo de lucro!")
                logger.info("O bot sera encerrado e bloqueado por 24 horas")
                logger.info("para proteger seus ganhos.")
                logger.info("="*60)
                
                print("\n" + "="*60)
                print("PARABENS! STOP WIN ATINGIDO!")
                print("="*60)
                print(f"Banca Inicial: ${saldo_inicial:.2f}")
                print(f"Banca Final: ${saldo_atual:.2f}")
                print(f"Lucro: ${lucro_atual:.2f} ({percentual_lucro:.2f}%)")
                print(f"Meta: {stop_win_percentual}%")
                print("")
                print("IMPORTANTE:")
                print("   - Bot sera bloqueado por 24 horas")
                print("   - Isto protege seus lucros contra operacoes emocionais")
                print("   - Aproveite seu lucro com sabedoria!")
                print("="*60 + "\n")
                
                # Registrar bloqueio
                registrar_stop_win(email, lucro_atual, stop_win_percentual, saldo_inicial)
                
                # Alerta sonoro de vitória
                emitir_alerta_sonoro(repeticoes=5, duracao_ms=200)
                break
            
            
            # Verificar proteção de stop loss por percentual DINAMICO
            if saldo_inicial > 0 and saldo_atual > 0:
                percentual_perda = ((saldo_inicial - saldo_atual) / saldo_inicial) * 100
                
                # Mostrar status periodicamente
                if minuto_atual % 10 == 0:
                    logger.info(f"[Status] Saldo: ${saldo_atual:.2f} | Variacao: {percentual_perda:+.2f}% | Perda contabilizada: ${perda_acumulada:.2f}")
                
                # Verificar se ultrapassou limite percentual
                if percentual_perda >= STOP_LOSS_PERCENTUAL:
                    perda_real = saldo_inicial - saldo_atual
                    logger.error(f"!!! STOP LOSS DINAMICO ATINGIDO: Perda de {percentual_perda:.2f}% da banca !!!")
                    logger.error(f"Banca inicial: ${saldo_inicial:.2f} | Saldo atual: ${saldo_atual:.2f} | Perda: ${perda_real:.2f}")
                    emitir_alerta_sonoro(repeticoes=5, duracao_ms=800)
                    break
            
            # Verificar se ainda há sinais pendentes
            if not verificar_sinais_pendentes(sinais, hora_atual, minuto_atual):
                logger.info("=== TODOS OS SINAIS FORAM EXECUTADOS ===")
                logger.info(f"Bot REAL finalizado. Resultado final: ${-perda_acumulada:.2f}")
                emitir_alerta_sonoro(repeticoes=3, duracao_ms=400)
                break
            
            # Verificar se há sinal agendado para agora
            sinal = verificar_sinal_agendado(sinais, hora_atual, minuto_atual)
            
            if sinal:
                # Marcar sinal como sendo processado
                sinal["executado"] = True
                
                # Verificar se está em pausa (pulando sinais)
                if sinais_pausados > 0:
                    logger.warning(f"[PAUSA] Pulando sinal por seguranca. Sinais restantes para pular: {sinais_pausados}")
                    sinais_pausados -= 1
                    if sinais_pausados == 0:
                        logger.info(f"[PAUSA] Fim da pausa. Zerando contadores e voltando a operar...")
                        loss_consecutivos = 0
                        conjuntos_3_loss = 0
                    continue
                
                ativo = sinal["ativo"]
                tipo = sinal["tipo"]
                tempo_minutos = sinal["tempo_minutos"]
                
                # SOROS: Obter valor dinâmico do gerenciador
                if gerenciador_soros:
                    valor_entrada = gerenciador_soros.calcular_proximo_valor()
                    protecao1 = None  # Soros não usa proteções
                    protecao2 = None
                    logger.info(f"[SOROS] {gerenciador_soros.get_info()}")
                else:
                    valor_entrada = sinal["valor_entrada"]
                    protecao1 = sinal.get("protecao1")
                    protecao2 = sinal.get("protecao2")
                
                # Normalizar nome do ativo
                ativo_normalizado = normalizar_ativo(ativo)
                logger.info(f"SINAL REAL encontrado: {tipo} em {ativo} ({ativo_normalizado}) por {tempo_minutos} min")
                from bot.utils import print_info_user
                print_info_user(f"Sinal encontrado: {tipo} em {ativo} por {tempo_minutos} minuto(s)")
                p1_str = f"${protecao1:.2f}" if protecao1 else "N/A"
                p2_str = f"${protecao2:.2f}" if protecao2 else "N/A"
                logger.info(f"Entrada: ${valor_entrada:.2f} | Protecao 1: {p1_str} | Protecao 2: {p2_str}")
                
                # Executar entrada principal
                try:
                    # Obter saldo atual para verificação dinâmica
                    try:
                        saldo_atual = Iq.get_balance()
                    except:
                        saldo_atual = saldo_inicial
                    
                    # PRE-VERIFICACAO DE SEGURANCA: Verificar se pode arriscar este valor
                    seguro, limite_valor, margem_disponivel = verificar_seguranca_operacao(
                        valor_entrada, saldo_atual, LIMITE_MAXIMO_POR_OPERACAO
                    )
                    
                    if not seguro:
                        logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO !!!")
                        logger.error(f"Entrada de ${valor_entrada:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                        logger.error(f"Saldo atual: ${saldo_atual:.2f} | Limite maximo por operacao: ${limite_valor:.2f}")
                        logger.error(f"Valor solicitado ({valor_entrada:.2f}) > Limite ({limite_valor:.2f})")
                        logger.error(f"Bot encerrado por seguranca preventiva")
                        emitir_alerta_sonoro(repeticoes=5, duracao_ms=800)
                        return
                    
                    logger.info(f">>> ENTRADA PRINCIPAL: ${valor_entrada:.2f} [Saldo: ${saldo_atual:.2f} | Max: ${limite_valor:.2f} | Margem: ${margem_disponivel:.2f}]")
                    resultado, diferenca = await executar_operacao_com_resultado(
                        Iq, valor_entrada, ativo_normalizado, tipo, tempo_minutos, logger, asyncio, sons_habilitados
                    )
                    
                    try:
                        salvar_resultado_operacao(ativo_normalizado, time.time(), resultado, 
                                                 ganho=diferenca if diferenca > 0 else None, 
                                                 perda=abs(diferenca) if diferenca < 0 else None)
                    except Exception:
                        pass
                    
                    # Se deu erro técnico (não conta como LOSS)
                    if resultado == "ERROR":
                        #logger.warning(f"[!] ERRO TECNICO - Operacao nao executada, nao conta como LOSS")
                        logger.warning(f"[!] ATIVO FECHADO")
                        logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                        continue
                    
                    # Se ganhou, não executa proteções
                    if resultado == "WIN":
                        logger.info(f"=== OPERACAO FINALIZADA COM WIN! Lucro total: ${diferenca:.2f}")
                        from bot.utils import print_success_user
                        print_success_user(f"Operação WIN! Lucro: ${diferenca:.2f}")
                        # Resetar todos os contadores
                        loss_consecutivos = 0
                        conjuntos_3_loss = 0
                        
                        # SOROS: Registrar WIN e calcular próximo valor
                        if gerenciador_soros:
                            gerenciador_soros.registrar_win(valor_entrada)
                            logger.info(f"[SOROS] Proximo valor: ${gerenciador_soros.calcular_proximo_valor():.2f}")
                        
                        logger.info(f"[Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                        continue
                    
                    # Se perdeu e tem proteção 1, executar
                    if resultado == "LOSS" and protecao1:
                        # Obter saldo atual após entrada principal
                        try:
                            saldo_atual_p1 = Iq.get_balance()
                        except:
                            saldo_atual_p1 = saldo_inicial
                        
                        # PRE-VERIFICACAO: Verificar proteção 1 com saldo atual
                        seguro_p1, limite_valor_p1, margem_disp_p1 = verificar_seguranca_operacao(
                            protecao1, saldo_atual_p1, LIMITE_MAXIMO_POR_OPERACAO
                        )
                        
                        if not seguro_p1:
                            logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO NA PROTECAO 1 !!!")
                            logger.error(f"Protecao 1 de ${protecao1:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                            logger.error(f"Saldo atual: ${saldo_atual_p1:.2f} | Limite maximo: ${limite_valor_p1:.2f}")
                            logger.error(f"Pulando protecao 1 por seguranca. Contabilizando LOSS da entrada principal.")
                            # Contabilizar apenas a perda da entrada principal
                            loss_consecutivos += 1
                            perda_acumulada += abs(diferenca)
                            logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        logger.info(f">>> PROTECAO 1: ${protecao1:.2f} [Saldo: ${saldo_atual_p1:.2f} | Max: ${limite_valor_p1:.2f}]")
                        resultado_p1, diferenca_p1 = await executar_operacao_com_resultado(
                            Iq, protecao1, ativo_normalizado, tipo, tempo_minutos, logger, asyncio
                        )
                        
                        try:
                            salvar_resultado_operacao(ativo_normalizado, time.time(), resultado_p1 + "_P1", 
                                                     ganho=diferenca_p1 if diferenca_p1 > 0 else None, 
                                                     perda=abs(diferenca_p1) if diferenca_p1 < 0 else None)
                        except Exception:
                            pass
                        
                        # Se proteção 1 deu erro técnico
                        if resultado_p1 == "ERROR":
                            #logger.warning(f"[!] ERRO TECNICO na Protecao 1 - nao conta como LOSS")
                            logger.warning(f"[!] ATIVO FECHADO")
                            logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        # Se proteção 1 ganhou
                        if resultado_p1 == "WIN":
                            lucro_total = diferenca + diferenca_p1
                            logger.info(f"=== PROTECAO 1 WIN! Lucro total: ${lucro_total:.2f}")
                            # Resetar todos os contadores
                            loss_consecutivos = 0
                            conjuntos_3_loss = 0
                            logger.info(f"[Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                            continue
                        
                        # Se proteção 1 perdeu e tem proteção 2, executar
                        if resultado_p1 == "LOSS" and protecao2:
                            # Obter saldo atual após proteção 1
                            try:
                                saldo_atual_p2 = Iq.get_balance()
                            except:
                                saldo_atual_p2 = saldo_inicial
                            
                            # PRE-VERIFICACAO: Verificar proteção 2 com saldo atual
                            seguro_p2, limite_valor_p2, margem_disp_p2 = verificar_seguranca_operacao(
                                protecao2, saldo_atual_p2, LIMITE_MAXIMO_POR_OPERACAO
                            )
                            
                            if not seguro_p2:
                                logger.error(f"!!! LIMITE DE OPERACAO EXCEDIDO NA PROTECAO 2 !!!")
                                logger.error(f"Protecao 2 de ${protecao2:.2f} excede limite de {LIMITE_MAXIMO_POR_OPERACAO}% do saldo atual")
                                logger.error(f"Saldo atual: ${saldo_atual_p2:.2f} | Limite maximo: ${limite_valor_p2:.2f}")
                                logger.error(f"Pulando protecao 2 por seguranca. Contabilizando LOSS acumulado ate P1.")
                                # Contabilizar perda da entrada + P1
                                prejuizo_total = abs(diferenca + diferenca_p1)
                                loss_consecutivos += 1
                                perda_acumulada += prejuizo_total
                                
                                if loss_consecutivos % 3 == 0:
                                    conjuntos_3_loss += 1
                                    logger.warning(f"[ALERTA] Conjunto de 3 LOSS detectado! Total: {conjuntos_3_loss}")
                                
                                if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                    logger.warning(f"[PAUSA] 6 LOSS atingidos! Pausando {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                    logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS! Pausando {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                
                                logger.warning(f"[Protecao] LOSS: {loss_consecutivos} | Conjuntos: {conjuntos_3_loss} | Perda: ${perda_acumulada:.2f}")
                                continue
                            
                            logger.info(f">>> PROTECAO 2: ${protecao2:.2f} [Saldo: ${saldo_atual_p2:.2f} | Max: ${limite_valor_p2:.2f}]")
                            resultado_p2, diferenca_p2 = await executar_operacao_com_resultado(
                                Iq, protecao2, ativo_normalizado, tipo, tempo_minutos, logger, asyncio
                            )
                            
                            try:
                                salvar_resultado_operacao(ativo_normalizado, time.time(), resultado_p2 + "_P2", 
                                                         ganho=diferenca_p2 if diferenca_p2 > 0 else None, 
                                                         perda=abs(diferenca_p2) if diferenca_p2 < 0 else None)
                            except Exception:
                                pass
                            
                            # Se proteção 2 deu erro técnico
                            if resultado_p2 == "ERROR":
                                #logger.warning(f"[!] ERRO TECNICO na Protecao 2 - nao conta como LOSS")
                                logger.warning(f"[!] ATIVO FECHADO")
                                logger.info(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                                continue
                            
                            lucro_total = diferenca + diferenca_p1 + diferenca_p2
                            if resultado_p2 == "WIN":
                                logger.info(f"=== PROTECAO 2 WIN! Lucro total: ${lucro_total:.2f}")
                                # Resetar todos os contadores
                                loss_consecutivos = 0
                                conjuntos_3_loss = 0
                                logger.info(f"[Protecao] LOSS consecutivos: 0 | Conjuntos de 3 LOSS: 0 | Perda acumulada: ${perda_acumulada:.2f}")
                            else:
                                logger.info(f"XXX TODAS PROTECOES PERDIDAS! Prejuizo total: ${abs(lucro_total):.2f}")
                                
                                # SOROS: Registrar LOSS e voltar ao valor base
                                if gerenciador_soros:
                                    gerenciador_soros.registrar_loss()
                                    logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                                
                                # Incrementar LOSS consecutivos e perda acumulada
                                loss_consecutivos += 1
                                perda_acumulada += abs(lucro_total)
                                
                                # Verificar se completou conjunto de 3 LOSS
                                if loss_consecutivos % 3 == 0:
                                    conjuntos_3_loss += 1
                                    logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                                
                                # Verificar se precisa pausar
                                if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                    logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                    logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                    sinais_pausados = SINAIS_PARA_PULAR
                                
                                logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                        else:
                            # Sem proteção 2 ou não definida
                            prejuizo_total = abs(diferenca + diferenca_p1)
                            logger.info(f"XXX PROTECAO 1 PERDIDA! Prejuizo total: ${prejuizo_total:.2f}")
                            
                            # SOROS: Registrar LOSS e voltar ao valor base
                            if gerenciador_soros:
                                gerenciador_soros.registrar_loss()
                                logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                            
                            # Incrementar LOSS consecutivos e perda acumulada
                            loss_consecutivos += 1
                            perda_acumulada += prejuizo_total
                            
                            # Verificar se completou conjunto de 3 LOSS
                            if loss_consecutivos % 3 == 0:
                                conjuntos_3_loss += 1
                                logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                            
                            # Verificar se precisa pausar
                            if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                                logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                sinais_pausados = SINAIS_PARA_PULAR
                            elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                                logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                                sinais_pausados = SINAIS_PARA_PULAR
                            
                            logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")
                    else:
                        # Sem proteção 1 ou não definida
                        logger.info(f"XXX OPERACAO FINALIZADA COM LOSS! Prejuizo total: ${abs(diferenca):.2f}")
                        
                        # SOROS: Registrar LOSS e voltar ao valor base
                        if gerenciador_soros:
                            gerenciador_soros.registrar_loss()
                            logger.info(f"[SOROS] Voltou para valor base: ${gerenciador_soros.valor_base:.2f}")
                        
                        # Incrementar LOSS consecutivos e perda acumulada
                        loss_consecutivos += 1
                        perda_acumulada += abs(diferenca)
                        
                        # Verificar se completou conjunto de 3 LOSS
                        if loss_consecutivos % 3 == 0:
                            conjuntos_3_loss += 1
                            logger.warning(f"[ALERTA] Conjunto de 3 LOSS consecutivos detectado! Total de conjuntos: {conjuntos_3_loss}")
                        
                        # Verificar se precisa pausar
                        if loss_consecutivos >= PAUSA_APOS_6_LOSS:
                            logger.warning(f"[PAUSA] 6 LOSS consecutivos atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                            sinais_pausados = SINAIS_PARA_PULAR
                        elif conjuntos_3_loss >= PAUSA_APOS_2_CONJUNTOS_3_LOSS:
                            logger.warning(f"[PAUSA] 2 conjuntos de 3 LOSS atingidos! Pausando proximos {SINAIS_PARA_PULAR} sinais...")
                            sinais_pausados = SINAIS_PARA_PULAR
                        
                        logger.warning(f"[Protecao] LOSS consecutivos: {loss_consecutivos} | Conjuntos de 3 LOSS: {conjuntos_3_loss} | Perda acumulada: ${perda_acumulada:.2f}")

                except Exception as e:
                    logger.error(f"Erro ao executar operacao REAL: {e}")
            else:
                # Log apenas a cada 5 minutos para não poluir
                if minuto_atual % 5 == 0:
                    logger.info(f"Aguardando sinais... Hora atual: {hora_atual:02d}:{minuto_atual:02d}")
                    from bot.utils import print_user
                    print_user(f"⏰ Aguardando sinais... {hora_atual:02d}:{minuto_atual:02d}")

            # Aguardar 1 minuto antes da próxima verificação
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Erro no loop REAL: {e}")
            logger.warning("Tentando reconectar...")
            try:
                Iq.connect()
            except Exception as reconnect_error:
                logger.error(f"Erro na reconexão: {reconnect_error}")
            await asyncio.sleep(10)
