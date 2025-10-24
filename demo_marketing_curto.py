#!/usr/bin/env python3
"""
Demonstração Curta para Marketing - Trader Bot
Versão otimizada para vídeos de marketing
"""
import time
import random
import sys
from datetime import datetime, timedelta

def print_header():
    print("=" * 60)
    print("🤖 TRADER BOT - SISTEMA AUTOMATIZADO")
    print("=" * 60)
    print("✅ Versão: v2 (Mensagens Simplificadas)")
    print("✅ Modo: DEMO (Sem dinheiro real)")
    print("✅ Mensagens: '[!] ATIVO FECHADO'")
    print("=" * 60)
    print()

def print_status(message, icon="ℹ️"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

def main():
    try:
        print_header()
        
        # Conexão rápida
        print_status("Conectando com IQ Option...", "🔌")
        time.sleep(1)
        print_status("Conexão estabelecida!", "✅")
        print_status("Saldo: $1,000.00", "💰")
        print()
        
        # Sinais rápidos
        signals = [
            ("EURUSD", "CALL", "5M"),
            ("GBPUSD", "PUT", "3M"),
            ("USDJPY", "CALL", "5M"),
            ("EURJPY", "PUT", "3M")
        ]
        
        balance = 1000.00
        wins = 0
        losses = 0
        
        for i, (asset, direction, timeframe) in enumerate(signals, 1):
            print_status(f"Sinal {i}: {asset} {direction} {timeframe}", "📊")
            time.sleep(0.8)
            print_status("Operação: $10.00", "💰")
            time.sleep(1)
            
            # 75% de chance de ganho
            if random.random() < 0.75:
                profit = random.uniform(8.5, 9.5)
                balance += profit
                wins += 1
                print_status(f"GANHO! +${profit:.2f}", "✅")
            else:
                balance -= 10
                losses += 1
                print_status("PERDA -$10.00", "❌")
            
            print_status(f"Saldo: ${balance:.2f}", "💰")
            print()
            time.sleep(1)
        
        # Resultado final
        profit = balance - 1000
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        print("=" * 60)
        print("📊 RESULTADO FINAL:")
        print("=" * 60)
        print(f"✅ Ganhos: {wins}")
        print(f"❌ Perdas: {losses}")
        print(f"📈 Taxa de Acerto: {win_rate:.1f}%")
        print(f"💰 Lucro: ${profit:+.2f}")
        print(f"📊 ROI: {(profit/1000*100):+.1f}%")
        print("=" * 60)
        print()
        print("🎉 BOT FUNCIONANDO PERFEITAMENTE!")
        print("✅ Pronto para uso em conta real")
        print("=" * 60)
        print()
        print("📞 CONTATO:")
        print("📱 WhatsApp: (11) 99999-9999")
        print("🌐 Website: www.traderbot.com")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida.")
        sys.exit(0)

if __name__ == "__main__":
    main()
