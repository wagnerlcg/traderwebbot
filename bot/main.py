import argparse
import logging
import asyncio
from bot.iqoption_bot import executar_real, executar_demo
from bot.utils import setup_logger, solicitar_credenciais
from bot.estrategias import solicitar_estrategia, exibir_resumo_estrategia

def main():
    parser = argparse.ArgumentParser(description="Robô Trader - Demo ou Real com arquivo de sinais")
    parser.add_argument("--mode", choices=["demo", "real"], required=True,
                        help="Escolha o modo de execução")
    parser.add_argument("--sinais", default="data/sinais.txt", help="Arquivo de sinais (formato: M1/M5/M15/M30;ATIVO;HH:MM;PUT/CALL;VALOR;[PROTECAO1];[PROTECAO2])")
    parser.add_argument("--stop-loss", type=float, default=None,
                        help="Percentual de stop loss (1 a 50%%). Se nao informado, sera solicitado.")
    parser.add_argument("--sons", action="store_true", default=True,
                        help="Habilitar sons e alertas (padrao: habilitado)")
    parser.add_argument("--sem-sons", action="store_true", default=False,
                        help="Desabilitar sons e alertas")
    args = parser.parse_args()

    logger = setup_logger("bot", "logs/bot.log")
    
    # PASSO 1: Solicitar credenciais PRIMEIRO
    print()
    print("="*60)
    print("  CREDENCIAIS IQ OPTION")
    print("="*60)
    print()
    print("Informe suas credenciais para conectar primeiro.")
    print("Apos conectar, voce configurara as estrategias.")
    print()
    
    conta_tipo = "REAL" if args.mode == "real" else "DEMO"
    email, senha = solicitar_credenciais(conta=conta_tipo)
    
    if not email or not senha:
        print()
        print("[ERRO] Credenciais nao fornecidas. Encerrando...")
        return
    
    # PASSO 2: Determinar configuração de sons
    sons_habilitados = args.sons and not args.sem_sons
    
    # PASSO 3: Passar credenciais e o bot conecta primeiro
    # Depois solicita as configurações dentro de executar_real/executar_demo

    if args.mode == "real":
        asyncio.run(executar_real(args.sinais, logger, email, senha, args.stop_loss, sons_habilitados))
    elif args.mode == "demo":
        asyncio.run(executar_demo(args.sinais, logger, email, senha, args.stop_loss, sons_habilitados))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("="*60)
        print("  BOT INTERROMPIDO PELO USUARIO")
        print("="*60)
        print()
        print("O bot foi encerrado com seguranca.")
        print("Nenhuma operacao em andamento foi perdida.")
        print()
        print("Ate a proxima! :)")
        print()
    except Exception as e:
        print()
        print()
        print("="*60)
        print("  ERRO INESPERADO")
        print("="*60)
        print()
        print(f"Erro: {e}")
        print()
        print("Consulte os logs para mais detalhes: logs/bot.log")
        print()
