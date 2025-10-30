"""
Módulo de estratégias de gerenciamento de banca
"""
import math
from typing import List, Tuple

def verificar_modo_web():
    """Verifica se estamos em modo web através da variável global MODO_WEB"""
    try:
        from bot.iqoption_bot import MODO_WEB
        return MODO_WEB
    except ImportError:
        # Se não conseguir importar, verificar verificar_modo_web()
        import sys
        return not verificar_modo_web()

def calcular_masaniello_inteligente(banca_inicial: float, quantidade_entradas: int, numero_acertos: int,
                                   payout: float = 0.87) -> Tuple[List[float], dict]:
    """
    Calcula a progressão Masaniello TRADICIONAL com progressão geométrica.
    
    Fórmula original do Masaniello:
    - Progressão geométrica onde cada entrada é um múltiplo da anterior
    - O multiplicador é calculado para equilibrar acertos e perdas
    - Usa 100% da banca disponível no ciclo
    
    Args:
        banca_inicial: Valor da banca inicial
        quantidade_entradas: Número total de operações no ciclo
        numero_acertos: Quantos acertos espera ter
        payout: Retorno da corretora (ex: 0.87 = 87%)
    
    Returns:
        Tupla com:
        - Lista de valores para cada entrada
        - Dicionário com informações do cálculo
    """
    if numero_acertos >= quantidade_entradas:
        raise ValueError("Número de acertos deve ser menor que quantidade de entradas")
    
    if numero_acertos < 1:
        raise ValueError("Número de acertos deve ser pelo menos 1")
    
    numero_perdas = quantidade_entradas - numero_acertos
    
    # VERIFICAR VIABILIDADE MATEMÁTICA
    # Fórmula: Lucro = (acertos × payout) - perdas
    lucro_por_unidade = (numero_acertos * payout) - numero_perdas
    
    info = {
        'lucro_por_unidade': lucro_por_unidade,
        'viavel': lucro_por_unidade > 0,
        'acertos': numero_acertos,
        'perdas': numero_perdas,
        'taxa_acerto': (numero_acertos / quantidade_entradas) * 100,
        'payout': payout * 100
    }
    
    # Usar 100% da banca (Masaniello tradicional)
    investimento_total = banca_inicial
    percentual_banca = 100.0
    
    if lucro_por_unidade > 0:
        # VIÁVEL: Calcular lucro esperado
        lucro_esperado = investimento_total * (lucro_por_unidade / quantidade_entradas)
        objetivo_lucro_percentual = (lucro_esperado / banca_inicial) * 100
        
        info['status'] = 'VIAVEL'
        info['investimento_total'] = investimento_total
        info['percentual_banca'] = percentual_banca
        info['lucro_esperado'] = lucro_esperado
        info['objetivo_percentual'] = objetivo_lucro_percentual
        info['mensagem'] = f"Matematicamente VIAVEL! Lucro esperado: {objetivo_lucro_percentual:.1f}%"
        
    else:
        # INVIÁVEL: Vai dar prejuízo
        prejuizo_esperado = investimento_total * (abs(lucro_por_unidade) / quantidade_entradas)
        prejuizo_percentual = (prejuizo_esperado / banca_inicial) * 100
        
        # Calcular quantos acertos seriam necessários
        acertos_necessarios = math.ceil((numero_perdas) / payout) + 1
        
        info['status'] = 'INVIAVEL'
        info['investimento_total'] = investimento_total
        info['percentual_banca'] = percentual_banca
        info['prejuizo_esperado'] = prejuizo_esperado
        info['prejuizo_percentual'] = prejuizo_percentual
        info['acertos_necessarios'] = min(acertos_necessarios, quantidade_entradas)
        info['mensagem'] = f"AVISO: Matematicamente INVIAVEL! Prejuizo esperado: -{prejuizo_percentual:.1f}%"
        info['sugestao'] = f"Aumente para {info['acertos_necessarios']} acertos ({info['acertos_necessarios']/quantidade_entradas*100:.0f}%) ou use outra estrategia"
    
    # CALCULAR MASANIELLO VERDADEIRO
    # Fórmula: Lucro deve ser IGUAL independente de qual entrada acertar
    # 
    # Conceito: Se acertar entrada k, o lucro deve ser:
    # V[k] × P = Soma(V[1]...V[k-1]) + L
    # 
    # Onde:
    # - V[k] = valor da entrada k
    # - P = payout (ex: 0.89)
    # - L = lucro desejado (fixo para todas as entradas)
    
    n = quantidade_entradas
    k = numero_acertos
    p = payout
    
    # MÉTODO 1: Calcular usando busca iterativa para encontrar L ideal
    # que use toda a banca disponível
    
    def calcular_valores_masaniello(lucro_alvo):
        """Calcula valores do Masaniello para um lucro alvo específico"""
        vals = []
        soma_anterior = 0
        
        for i in range(n):
            # Fórmula: V[i] × P = soma_anterior + L
            # V[i] = (soma_anterior + L) / P
            valor = (soma_anterior + lucro_alvo) / p
            vals.append(valor)
            soma_anterior += valor
        
        return vals, soma_anterior
    
    # Buscar lucro alvo que use toda a banca
    lucro_min, lucro_max = 0.01, investimento_total * 0.5
    melhor_lucro = 0
    melhores_valores = []
    
    for _ in range(100):  # 100 iterações de busca binária
        lucro_teste = (lucro_min + lucro_max) / 2
        vals, total = calcular_valores_masaniello(lucro_teste)
        
        if total < investimento_total:
            lucro_min = lucro_teste
            melhor_lucro = lucro_teste
            melhores_valores = vals
        else:
            lucro_max = lucro_teste
        
        # Se chegou muito perto, pode parar
        if abs(total - investimento_total) < 0.01:
            melhor_lucro = lucro_teste
            melhores_valores = vals
            break
    
    # Arredondar valores
    valores = [round(v, 2) for v in melhores_valores]
    
    # Ajustar para bater exatamente o total
    soma_atual = sum(valores)
    if soma_atual != investimento_total:
        # Ajustar proporcionalmente
        fator = investimento_total / soma_atual
        valores = [round(v * fator, 2) for v in valores]
        
        # Ajuste final no último valor
        soma_atual = sum(valores)
        if soma_atual != investimento_total:
            diferenca = investimento_total - soma_atual
            valores[-1] = round(valores[-1] + diferenca, 2)
    
    # Calcular multiplicador médio (para informação)
    q_medio = 0
    if len(valores) > 1:
        multiplicadores = [valores[i+1] / valores[i] for i in range(len(valores)-1)]
        q_medio = sum(multiplicadores) / len(multiplicadores)
    
    # Adicionar informações
    info['multiplicador'] = round(q_medio, 3)
    info['lucro_por_acerto'] = round(melhor_lucro, 2)
    info['lucro_por_acerto_percentual'] = round((melhor_lucro / banca_inicial) * 100, 2)
    
    return valores, info


def calcular_masaniello(banca_inicial: float, quantidade_entradas: int, numero_acertos: int, 
                       objetivo_lucro_percentual: float = 20.0, payout: float = 0.80) -> List[float]:
    """
    Calcula a progressão Masaniello (VERSÃO LEGADA - mantida para compatibilidade).
    
    RECOMENDAÇÃO: Use calcular_masaniello_inteligente() para cálculo automático.
    
    Args:
        banca_inicial: Valor da banca inicial
        quantidade_entradas: Número total de operações no ciclo
        numero_acertos: Quantos acertos espera ter
        objetivo_lucro_percentual: Lucro desejado em % da banca
        payout: Retorno da corretora (padrão 80% = 1.80 na IQ Option)
    
    Returns:
        Lista com valores para cada entrada do ciclo
    """
    if numero_acertos >= quantidade_entradas:
        raise ValueError("Número de acertos deve ser menor que quantidade de entradas")
    
    if numero_acertos < 1:
        raise ValueError("Número de acertos deve ser pelo menos 1")
    
    objetivo_lucro = banca_inicial * (objetivo_lucro_percentual / 100)
    numero_perdas = quantidade_entradas - numero_acertos
    
    # Fórmula Masaniello simplificada
    # valor_aposta = (objetivo_lucro + (numero_perdas * valor_medio_aposta)) / (numero_acertos * payout)
    
    # Cálculo iterativo para distribuir valores
    valores = []
    lucro_acumulado_necessario = objetivo_lucro
    
    # Distribuir investimento proporcionalmente
    denominador = (numero_acertos * payout - numero_perdas)
    if denominador <= 0:
        # Impossível - usar fallback
        investimento_total_estimado = banca_inicial * 0.3
    else:
        investimento_total_estimado = objetivo_lucro / denominador
    
    for i in range(quantidade_entradas):
        # Progressão suave - valores crescentes
        fator = 1 + (i / quantidade_entradas) * 0.5  # 0-50% de incremento
        valor_base = investimento_total_estimado / quantidade_entradas
        valor_entrada = valor_base * fator
        valores.append(round(abs(valor_entrada), 2))
    
    # Normalizar para atingir objetivo
    soma_valores = sum(valores)
    if soma_valores > 0:
        fator_normalizacao = investimento_total_estimado / soma_valores
        valores = [round(abs(v * fator_normalizacao), 2) for v in valores]
    
    return valores

class GerenciadorSoros:
    """
    Gerenciador da estratégia Soros (Reinvestimento de Lucros).
    
    Funcionamento:
    - Entrada 1: Valor base
    - Se WIN → Entrada 2: Valor anterior + lucro
    - Se WIN → Entrada 3: Valor anterior + lucro (ÚLTIMA - depois volta ao base)
    - Se LOSS em qualquer momento → Volta para valor base
    
    Máximo: 3 entradas (1 inicial + 2 reinvestimentos)
    """
    
    def __init__(self, valor_base: float, payout: float = 0.87):
        """
        Inicializa o gerenciador Soros.
        
        Args:
            valor_base: Valor inicial da entrada
            payout: Retorno da corretora (padrão 87% = lucro de 87%)
        """
        self.valor_base = valor_base
        self.payout = payout
        self.valor_atual = valor_base
        self.wins_consecutivos = 0
        self.max_wins_sequencia = 2  # Máximo 2 WINs (3 entradas total)
    
    def calcular_proximo_valor(self) -> float:
        """Retorna o valor atual para a próxima operação"""
        return round(self.valor_atual, 2)
    
    def registrar_win(self, valor_apostado: float):
        """
        Registra um WIN e calcula próximo valor.
        
        Args:
            valor_apostado: Valor que foi apostado
        """
        self.wins_consecutivos += 1
        lucro = valor_apostado * self.payout
        
        # Se atingiu máximo de WINs, reseta para base
        if self.wins_consecutivos >= self.max_wins_sequencia:
            self.valor_atual = self.valor_base
            self.wins_consecutivos = 0
        else:
            # Próxima entrada = valor apostado + lucro
            self.valor_atual = valor_apostado + lucro
    
    def registrar_loss(self):
        """
        Registra um LOSS e volta para valor base.
        """
        self.valor_atual = self.valor_base
        self.wins_consecutivos = 0
    
    def resetar(self):
        """Reseta para valor base"""
        self.valor_atual = self.valor_base
        self.wins_consecutivos = 0
    
    def get_info(self) -> str:
        """Retorna informações do estado atual"""
        if self.wins_consecutivos == 0:
            return f"Soros: Entrada INICIAL = ${self.valor_atual:.2f}"
        elif self.wins_consecutivos == 1:
            return f"Soros: Reinvestimento 1 = ${self.valor_atual:.2f} (1 WIN anterior)"
        else:
            return f"Soros: Reinvestimento 2 = ${self.valor_atual:.2f} (ULTIMA entrada!)"

def calcular_martingale(valor_base: float, nivel: int = 2, multiplicador: float = 2.0) -> Tuple[float, float, float]:
    """
    Calcula valores Martingale clássico.
    
    Args:
        valor_base: Valor da entrada inicial
        nivel: 1 (entrada + 1 proteção) ou 2 (entrada + 2 proteções)
        multiplicador: Fator de multiplicação (padrão 2.0)
    
    Returns:
        Tupla (entrada, protecao1, protecao2)
        - Se nivel=1: protecao2 será None
    """
    entrada = round(valor_base, 2)
    protecao1 = round(valor_base * multiplicador, 2)
    
    if nivel >= 2:
        protecao2 = round(protecao1 * multiplicador, 2)
    else:
        protecao2 = None
    
    return (entrada, protecao1, protecao2)

def solicitar_valor_entrada(estrategia_escolhida=None):
    """
    Solicita ao usuário como deseja definir o valor de entrada.
    
    Args:
        estrategia_escolhida: Nome da estratégia (para validação)
    
    Returns:
        dict: {"tipo": "fixo"|"percentual", "valor": float}
    """
    print()
    print("="*60)
    print("  CONFIGURACAO DO VALOR DE ENTRADA")
    print("="*60)
    print()
    
    # Masaniello requer valor fixo
    if estrategia_escolhida == "Masaniello":
        print("IMPORTANTE: Masaniello requer valor FIXO em R$")
        print("O bot calculara a distribuicao do ciclo baseado neste valor")
        print()
        
        try:
            # Verificar se estamos em modo web
            if verificar_modo_web():
                # Modo web - usar valor padrão
                valor = 10.0
                print(f"Valor base do ciclo Masaniello ($): {valor} (padrão para modo web)")
            else:
                # Modo terminal - solicitar input
                valor = float(input("Valor base do ciclo Masaniello ($): ").strip())
            
            if valor <= 0:
                print("[AVISO] Valor invalido. Usando padrao: $10.00")
                valor = 10.0
            
            print()
            print(f"[OK] Configurado: Valor fixo de ${valor:.2f} para ciclo Masaniello")
            print()
            
            return {"tipo": "fixo", "valor": valor}
            
        except (ValueError, KeyboardInterrupt):
            print()
            print("[AVISO] Entrada invalida. Usando padrao: $10.00 fixo")
            return {"tipo": "fixo", "valor": 10.0}
    
    # Para outras estratégias, permite escolher
    print("Como deseja definir o valor de entrada para as operacoes?")
    print()
    print("  1 - Valor fixo em R$")
    print("     Exemplo: $10.00 por operacao (sempre o mesmo valor)")
    print()
    print("  2 - Percentual da banca")
    print("     Exemplo: 2% da banca atual (valor muda conforme saldo)")
    print()
    
    try:
        # Verificar se estamos em modo web
        if verificar_modo_web():
            # Modo web - usar opção padrão
            opcao = "1"
            print(f"Escolha o TIPO (1 ou 2): {opcao} (padrão para modo web)")
        else:
            # Modo terminal - solicitar input
            opcao = input("Escolha o TIPO (1 ou 2): ").strip()
        
        if opcao == "1":
            print()
            # Verificar se estamos em modo web
            if verificar_modo_web():
                # Modo web - usar valor padrão
                valor = 10.0
                print(f"Informe o VALOR fixo por entrada ($): {valor} (padrão para modo web)")
            else:
                # Modo terminal - solicitar input
                valor = float(input("Informe o VALOR fixo por entrada ($): ").strip())
            if valor <= 0:
                print("[AVISO] Valor invalido. Usando padrao: $10.00")
                valor = 10.0
            
            print()
            print(f"[OK] Configurado: Valor fixo de ${valor:.2f} por operacao")
            print()
            
            return {"tipo": "fixo", "valor": valor}
        
        elif opcao == "2":
            print()
            print("Agora informe QUAL percentual da banca deseja usar:")
            # Verificar se estamos em modo interativo
            import sys
            if verificar_modo_web():
                # Modo web - usar percentual padrão
                percentual = 2.0
                print(f"Percentual (ex: 2 para 2% da banca): {percentual} (padrão para modo web)")
            else:
                percentual = float(input("Percentual (ex: 2 para 2% da banca): ").strip())
            if percentual <= 0 or percentual > 50:
                print("[AVISO] Percentual invalido (use 0.1 a 50%). Usando padrao: 2%")
                percentual = 2.0
            
            print()
            print(f"[OK] Configurado: {percentual}% da banca por operacao")
            print(f"     Valor sera calculado automaticamente conforme saldo atual")
            print()
            
            return {"tipo": "percentual", "valor": percentual}
        
        else:
            print()
            print("[AVISO] Opcao invalida. Usando padrao: $10.00 fixo")
            return {"tipo": "fixo", "valor": 10.0}
    
    except (ValueError, KeyboardInterrupt):
        print()
        print("[AVISO] Entrada invalida. Usando padrao: $10.00 fixo")
        return {"tipo": "fixo", "valor": 10.0}

def solicitar_estrategia():
    """
    Solicita ao usuário qual estratégia deseja usar e seus parâmetros.
    
    Returns:
        Tupla (nome_estrategia, parametros_dict)
    """
    print()
    print("="*60)
    print("  SELECAO DE ESTRATEGIA DE GERENCIAMENTO")
    print("="*60)
    print()
    print("Escolha a estrategia de gerenciamento de banca:")
    print()
    print("  1 - Masaniello  (Progressao calculada por ciclos)")
    print("  2 - Martingale  (Progressao geometrica - G1 ou G2)")
    print("  3 - Soros       (Reinvestimento de lucros - max 3 entradas)")
    print("  4 - Valor Fixo  (Sem progressao - mais seguro)")
    print()
    
    try:
        # Verificar se estamos em modo web com configurações
        if verificar_modo_web():
            try:
                from bot.iqoption_bot import WEB_CONFIG
                if WEB_CONFIG and 'estrategia' in WEB_CONFIG:
                    estrategia_web = WEB_CONFIG['estrategia']
                    # Mapear nome da estratégia para número
                    if estrategia_web == "Masaniello":
                        escolha = "1"
                    elif estrategia_web == "Martingale":
                        escolha = "2"
                    elif estrategia_web == "Soros":
                        escolha = "3"
                    elif estrategia_web == "Valor Fixo":
                        escolha = "4"
                    else:
                        escolha = "4"  # Padrão
                    print(f"Estrategia configurada via web: {estrategia_web}")
                else:
                    escolha = "4"  # Valor Fixo padrão
                    print(f"Estrategia (1, 2, 3 ou 4): {escolha} (padrão para modo web)")
            except ImportError:
                escolha = "4"  # Valor Fixo padrão
                print(f"Estrategia (1, 2, 3 ou 4): {escolha} (padrão para modo web)")
        else:
            escolha = input("Estrategia (1, 2, 3 ou 4): ").strip()
        
        if escolha == "1":
            return solicitar_parametros_masaniello()
        elif escolha == "2":
            return solicitar_parametros_martingale()
        elif escolha == "3":
            return solicitar_parametros_soros()
        elif escolha == "4":
            # Valor Fixo - sem parâmetros especiais
            print()
            print("[OK] Valor Fixo selecionado")
            print("     Todas as operacoes terao o mesmo valor")
            return ("Valor Fixo", {})
        else:
            print()
            print(f"[ERRO] Opcao invalida '{escolha}'. Usando Valor Fixo (padrao)")
            return ("Valor Fixo", {})
            
    except (KeyboardInterrupt, Exception) as e:
        print()
        print(f"[ERRO] Erro na selecao. Usando Valor Fixo (padrao)")
        return ("Valor Fixo", {})

def solicitar_parametros_masaniello():
    """Solicita parâmetros da estratégia Masaniello"""
    print()
    print("--- CONFIGURACAO MASANIELLO ---")
    print()
    print("Masaniello: Progressao matematica por ciclos")
    print("  - Usa valor FIXO em R$ como base")
    print("  - Distribui valores para atingir objetivo")
    print("  - Sem protecoes (opera ciclo completo)")
    print()
    
    try:
        # Verificar se estamos em modo interativo
        import sys
        if verificar_modo_web():
            qtd_entradas = int(input("Quantidade de entradas no ciclo (2-20): ").strip())
            if qtd_entradas < 2 or qtd_entradas > 20:
                qtd_entradas = 10
                print(f"[AVISO] Usando padrao: 10 entradas")
            
            num_acertos = int(input(f"Numero de acertos esperados (1-{qtd_entradas-1}): ").strip())
            if num_acertos < 1 or num_acertos >= qtd_entradas:
                num_acertos = int(qtd_entradas * 0.7)
                print(f"[AVISO] Usando padrao: {num_acertos} acertos (70%)")
        else:
            # Modo web - usar valores padrão
            qtd_entradas = 10
            num_acertos = 7
            print(f"Quantidade de entradas no ciclo (2-20): {qtd_entradas} (padrão para modo web)")
            print(f"Numero de acertos esperados (1-{qtd_entradas-1}): {num_acertos} (padrão para modo web)")
        
        # Objetivo fixo em 100%
        objetivo = 100.0
        print()
        print(f"[INFO] Objetivo de lucro: {objetivo}% (fixo)")
        
        print()
        print("Ao atingir o objetivo do ciclo, o bot deve:")
        print("  1 - Parar (encerrar bot)")
        print("  2 - Reiniciar novo ciclo com valor base atualizado")
        print()
        
        # Verificar se estamos em modo interativo
        if verificar_modo_web():
            acao = input("Opcao (1 ou 2, padrao 1): ").strip() or "1"
        else:
            # Modo web - usar opção padrão
            acao = "1"
            print(f"Opcao (1 ou 2, padrao 1): {acao} (padrão para modo web)")
        reiniciar = (acao == "2")
        
        print()
        print(f"[OK] Masaniello configurado:")
        print(f"     Ciclo: {qtd_entradas} entradas")
        print(f"     Acertos esperados: {num_acertos} ({num_acertos/qtd_entradas*100:.0f}%)")
        print(f"     Objetivo: +{objetivo}%")
        print(f"     Apos ciclo: {'Reiniciar' if reiniciar else 'Parar'}")
        print()
        
        # Solicitar banca para calcular prévia
        print("Para calcular a previa dos valores, informe sua banca:")
        try:
            # Verificar se estamos em modo interativo
            if verificar_modo_web():
                banca_previa = float(input("Banca inicial ($): ").strip().replace(',', '.'))
            else:
                # Modo web - usar valor padrão
                banca_previa = 1000.0
                print(f"Banca inicial ($): {banca_previa} (padrão para modo web)")
            
            # Calcular valores do Masaniello
            print()
            print("="*60)
            print("  PREVIA DOS VALORES CALCULADOS - MASANIELLO")
            print("="*60)
            
            valores, info = calcular_masaniello_inteligente(
                banca_inicial=banca_previa,
                quantidade_entradas=qtd_entradas,
                numero_acertos=num_acertos,
                payout=0.87
            )
            
            print()
            print(f"Status: {info['status']}")
            print(f"{info['mensagem']}")
            if 'sugestao' in info:
                print(f"Sugestao: {info['sugestao']}")
            print()
            print(f"Banca inicial: ${banca_previa:.2f}")
            print(f"Investimento total no ciclo: ${info['investimento_total']:.2f} ({info['percentual_banca']:.1f}%)")
            print()
            
            # Mostrar valores de entrada
            print("VALORES DE CADA ENTRADA:")
            print("-" * 60)
            for i, valor in enumerate(valores, 1):
                print(f"  Entrada {i:2d}: ${valor:8.2f}")
            print("-" * 60)
            print(f"  TOTAL:     ${sum(valores):8.2f}")
            print()
            
            # Simular cenários até 3 losses
            print("SIMULACAO DE CENARIOS (Payout 87%):")
            print("="*60)
            
            num_perdas = qtd_entradas - num_acertos
            payout = 0.87
            
            # Cenário 1: Todos acertos
            if num_acertos == qtd_entradas:
                lucro_total = sum([v * payout for v in valores])
                resultado = lucro_total
                print(f"Cenario 1: TODOS ACERTOS ({qtd_entradas} WINs)")
                print(f"  Investido: ${sum(valores):.2f}")
                print(f"  Lucro:     ${lucro_total:.2f}")
                print(f"  Resultado: ${resultado:.2f} ({resultado/banca_previa*100:+.1f}%)")
                print()
            
            # Cenário: Acertos esperados (sem loss extra)
            lucro_acertos = sum([valores[i] * payout for i in range(num_acertos)])
            perda_losses = sum([valores[i] for i in range(num_acertos, qtd_entradas)])
            resultado_esperado = lucro_acertos - perda_losses
            print(f"Cenario 2: ACERTOS ESPERADOS ({num_acertos} WINs / {num_perdas} LOSSes)")
            print(f"  Investido: ${sum(valores):.2f}")
            print(f"  Lucro dos WINs:  ${lucro_acertos:.2f}")
            print(f"  Perda LOSSes:    -${perda_losses:.2f}")
            print(f"  Resultado: ${resultado_esperado:.2f} ({resultado_esperado/banca_previa*100:+.1f}%)")
            print()
            
            # Cenário com 1 LOSS (se houver acertos suficientes)
            if num_acertos > 1:
                losses_simulacao = min(1, num_perdas)
                acertos_simulacao = qtd_entradas - losses_simulacao
                lucro_sim = sum([valores[i] * payout for i in range(acertos_simulacao)])
                perda_sim = sum([valores[i] for i in range(acertos_simulacao, acertos_simulacao + losses_simulacao)])
                resultado_sim = lucro_sim - perda_sim
                print(f"Cenario 3: COM 1 LOSS ({acertos_simulacao} WINs / {losses_simulacao} LOSS)")
                print(f"  Investido: ${sum(valores[:acertos_simulacao + losses_simulacao]):.2f}")
                print(f"  Lucro dos WINs:  ${lucro_sim:.2f}")
                print(f"  Perda LOSSes:    -${perda_sim:.2f}")
                print(f"  Resultado: ${resultado_sim:.2f} ({resultado_sim/banca_previa*100:+.1f}%)")
                print()
            
            # Cenário com 2 LOSSes (se o ciclo permitir)
            if qtd_entradas >= 3:
                losses_simulacao = min(2, qtd_entradas - 1)
                acertos_simulacao = qtd_entradas - losses_simulacao
                lucro_sim = sum([valores[i] * payout for i in range(acertos_simulacao)])
                perda_sim = sum([valores[i] for i in range(acertos_simulacao, acertos_simulacao + losses_simulacao)])
                resultado_sim = lucro_sim - perda_sim
                print(f"Cenario 4: COM 2 LOSSes ({acertos_simulacao} WINs / {losses_simulacao} LOSSes)")
                print(f"  Investido: ${sum(valores[:acertos_simulacao + losses_simulacao]):.2f}")
                print(f"  Lucro dos WINs:  ${lucro_sim:.2f}")
                print(f"  Perda LOSSes:    -${perda_sim:.2f}")
                print(f"  Resultado: ${resultado_sim:.2f} ({resultado_sim/banca_previa*100:+.1f}%)")
                print()
            
            # Cenário com 3 LOSSes (se o ciclo permitir)
            if qtd_entradas >= 4:
                losses_simulacao = min(3, qtd_entradas - 1)
                acertos_simulacao = qtd_entradas - losses_simulacao
                lucro_sim = sum([valores[i] * payout for i in range(acertos_simulacao)])
                perda_sim = sum([valores[i] for i in range(acertos_simulacao, acertos_simulacao + losses_simulacao)])
                resultado_sim = lucro_sim - perda_sim
                print(f"Cenario 5: COM 3 LOSSes ({acertos_simulacao} WINs / {losses_simulacao} LOSSes)")
                print(f"  Investido: ${sum(valores[:acertos_simulacao + losses_simulacao]):.2f}")
                print(f"  Lucro dos WINs:  ${lucro_sim:.2f}")
                print(f"  Perda LOSSes:    -${perda_sim:.2f}")
                print(f"  Resultado: ${resultado_sim:.2f} ({resultado_sim/banca_previa*100:+.1f}%)")
                print()
            
            print("="*60)
            print()
            
        except (ValueError, KeyboardInterrupt):
            print()
            print("[AVISO] Previa nao calculada. Continuando...")
            print()
        
        return ("Masaniello", {
            "quantidade_entradas": qtd_entradas,
            "numero_acertos": num_acertos,
            "objetivo_lucro_percentual": objetivo,
            "reiniciar_apos_ciclo": reiniciar
        })
        
    except (ValueError, KeyboardInterrupt):
        print()
        print("[ERRO] Parametros invalidos. Usando Martingale padrao")
        return ("Martingale", {"nivel": 2, "multiplicador": 2.0})

def solicitar_parametros_soros():
    """Solicita parâmetros da estratégia Soros"""
    print()
    print("--- CONFIGURACAO SOROS ---")
    print()
    print("Soros: Reinvestimento de Lucros (Progressao Inteligente)")
    print()
    print("Como funciona:")
    print("  - Entrada 1: Valor base (voce escolhe)")
    print("  - Se WIN → Entrada 2: Entrada 1 + lucro")
    print("  - Se WIN → Entrada 3: Entrada 2 + lucro (ULTIMA!)")
    print("  - Apos 3ª entrada ou LOSS → Volta ao valor base")
    print()
    print("Vantagens:")
    print("  + Cresce rapido com sequencias de WIN")
    print("  + Maximo 3 entradas por sequencia")
    print("  + Sempre volta ao valor base apos ciclo")
    print()
    print("Payout: 87% (fixo)")
    print()
    
    payout = 0.87  # Fixo em 87%
    
    print(f"[OK] Soros configurado:")
    print(f"     Payout: 87%")
    print(f"     Max entradas: 3")
    print()
    print(f"Exemplo de progressao com valor base $10:")
    valor_base = 10.0
    lucro1 = valor_base * payout
    valor2 = valor_base + lucro1
    lucro2 = valor2 * payout
    valor3 = valor2 + lucro2
    print(f"  Entrada 1: ${valor_base:.2f}")
    print(f"    WIN → Lucro ${lucro1:.2f}")
    print(f"  Entrada 2: ${valor2:.2f} (${valor_base:.2f} + ${lucro1:.2f})")
    print(f"    WIN → Lucro ${lucro2:.2f}")
    print(f"  Entrada 3: ${valor3:.2f} (${valor2:.2f} + ${lucro2:.2f}) - ULTIMA")
    print(f"    WIN ou LOSS → Volta a ${valor_base:.2f}")
    print()
    print(f"  Total lucro se 3 WINs: ${lucro1 + lucro2 + (valor3 * payout):.2f}")
    print()
    
    return ("Soros", {"payout": payout})

def solicitar_parametros_martingale():
    """Solicita parâmetros da estratégia Martingale"""
    print()
    print("--- CONFIGURACAO MARTINGALE ---")
    print()
    print("Martingale: Progressao geometrica para recuperacao")
    print()
    print("Escolha o nivel de Martingale:")
    print("  1 - G1 (entrada + 1 protecao)")
    print("  2 - G2 (entrada + 2 protecoes)")
    print()
    
    try:
        # Verificar se estamos em modo interativo
        import sys
        if verificar_modo_web():
            escolha_nivel = input("Nivel (1 ou 2): ").strip()
        else:
            # Modo web - usar nível padrão
            escolha_nivel = "2"
            print(f"Nivel (1 ou 2): {escolha_nivel} (padrão para modo web)")
        
        if escolha_nivel == "1":
            nivel = 1
        elif escolha_nivel == "2":
            nivel = 2
        else:
            print("[AVISO] Opcao invalida. Usando G2 (padrao)")
            nivel = 2
        
        # Multiplicador fixo
        multiplicador = 2.15
        
        print()
        print(f"[OK] Martingale G{nivel} configurado:")
        print(f"     Nivel: {nivel} (entrada + {nivel} {'protecao' if nivel == 1 else 'protecoes'})")
        print(f"     Multiplicador: {multiplicador}x")
        print()
        
        if nivel == 1:
            print("Exemplo: Se entrada for $10.00")
            print(f"  - Entrada: $10.00")
            print(f"  - Protecao 1: ${10.00 * multiplicador:.2f}")
            print(f"  - Total arriscado: ${10.00 * (1 + multiplicador):.2f}")
        else:
            print("Exemplo: Se entrada for $10.00")
            print(f"  - Entrada: $10.00")
            print(f"  - Protecao 1: ${10.00 * multiplicador:.2f}")
            print(f"  - Protecao 2: ${10.00 * multiplicador * multiplicador:.2f}")
            print(f"  - Total arriscado: ${10.00 * (1 + multiplicador + multiplicador**2):.2f}")
        
        print()
        
        return ("Martingale", {"nivel": nivel, "multiplicador": multiplicador})
        
    except (ValueError, KeyboardInterrupt):
        print()
        print("[AVISO] Erro na configuracao. Usando G2 (padrao)")
        return ("Martingale", {"nivel": 2, "multiplicador": 2.15})

def calcular_valor_entrada_base(config_entrada, saldo_atual):
    """
    Calcula o valor base da entrada conforme configuração do usuário.
    
    Args:
        config_entrada: dict com {"tipo": "fixo"|"percentual", "valor": float}
        saldo_atual: Saldo atual da conta
    
    Returns:
        float: Valor calculado para entrada
    """
    if config_entrada is None:
        return 10.0  # Padrão
    
    tipo = config_entrada.get("tipo", "fixo")
    valor = config_entrada.get("valor", 10.0)
    
    if tipo == "percentual":
        return round(saldo_atual * (valor / 100), 2)
    else:  # "fixo"
        return round(valor, 2)

def aplicar_estrategia_ao_sinal(sinal: dict, estrategia: str, parametros: dict, 
                               banca_atual: float, indice_ciclo: int = 0) -> dict:
    """
    Aplica a estratégia escolhida aos valores de um sinal.
    
    Args:
        sinal: Dicionário com dados do sinal
        estrategia: Nome da estratégia
        parametros: Parâmetros da estratégia
        banca_atual: Saldo atual da conta
        indice_ciclo: Índice no ciclo Masaniello (se aplicável)
    
    Returns:
        Sinal atualizado com valores calculados
    """
    if estrategia == "Masaniello":
        # Calcular todos os valores do ciclo
        qtd = parametros["quantidade_entradas"]
        acertos = parametros["numero_acertos"]
        objetivo = parametros["objetivo_lucro_percentual"]
        
        valores_ciclo = calcular_masaniello(banca_atual, qtd, acertos, objetivo)
        
        # Usar valor do índice atual
        if indice_ciclo < len(valores_ciclo):
            entrada = valores_ciclo[indice_ciclo]
        else:
            entrada = valores_ciclo[0]  # Reinicia ciclo
        
        # Masaniello não usa proteções tradicionais
        sinal['valor_entrada'] = entrada
        sinal['protecao1'] = None
        sinal['protecao2'] = None
        sinal['estrategia_info'] = f"Masaniello ciclo {indice_ciclo + 1}/{qtd}"
        
    elif estrategia == "Soros":
        # Soros usa valor base ou valor do gerenciador
        # Valores são calculados dinamicamente no bot principal
        # Aqui apenas garante que não tem proteções
        if 'valor_entrada' not in sinal or sinal['valor_entrada'] is None:
            valor_base = parametros.get("valor_base", 10.0)
            sinal['valor_entrada'] = valor_base
        
        sinal['protecao1'] = None  # Soros não usa proteções
        sinal['protecao2'] = None
        sinal['estrategia_info'] = "Soros (Reinvestimento)"
        
    elif estrategia == "Martingale":
        # Usar valor base do sinal (se existir) ou calcular % da banca
        valor_base = sinal.get('valor_entrada', banca_atual * 0.02)  # 2% padrão
        nivel = parametros["nivel"]
        mult = parametros["multiplicador"]
        
        entrada, p1, p2 = calcular_martingale(valor_base, nivel, mult)
        
        sinal['valor_entrada'] = entrada
        sinal['protecao1'] = p1
        sinal['protecao2'] = p2 if nivel >= 2 else None
        sinal['estrategia_info'] = f"Martingale nivel {nivel} ({mult}x)"
    
    return sinal

def exibir_resumo_estrategia(estrategia: str, parametros: dict, banca_inicial: float):
    """
    Exibe resumo da estratégia escolhida.
    """
    print()
    print("="*60)
    print(f"  ESTRATEGIA SELECIONADA: {estrategia.upper()}")
    print("="*60)
    print()
    
    if estrategia == "Masaniello":
        qtd = parametros["quantidade_entradas"]
        acertos = parametros["numero_acertos"]
        obj = parametros["objetivo_lucro_percentual"]
        
        print(f"Ciclo: {qtd} entradas")
        print(f"Acertos esperados: {acertos} ({acertos/qtd*100:.0f}%)")
        print(f"Objetivo: +{obj}% = ${banca_inicial * obj / 100:.2f}")
        print()
        print("Valores serao calculados automaticamente para cada entrada.")
        print("Sem protecoes (Masaniello opera com ciclos completos).")
        
    elif estrategia == "Soros":
        valor_base = parametros.get("valor_base", 10.0)
        payout = parametros.get("payout", 0.80)
        
        print(f"Reinvestimento de Lucros (Compounding)")
        print(f"Valor base: ${valor_base:.2f}")
        print(f"Payout: {payout*100:.0f}%")
        print()
        print("Progressao:")
        lucro1 = valor_base * payout
        v2 = valor_base + lucro1
        lucro2 = v2 * payout
        v3 = v2 + lucro2
        print(f"  WIN 1: ${valor_base:.2f} → ${v2:.2f}")
        print(f"  WIN 2: ${v2:.2f} → ${v3:.2f}")
        print(f"  WIN 3: Continua crescendo...")
        print(f"  LOSS: Volta para ${valor_base:.2f}")
        print()
        print("Sem protecoes (Soros reinveste tudo a cada WIN).")
        
    elif estrategia == "Martingale":
        nivel = parametros["nivel"]
        mult = parametros["multiplicador"]
        
        print(f"Nivel: {nivel} ({'1 protecao' if nivel == 1 else '2 protecoes'})")
        print(f"Multiplicador: {mult}x")
        print()
        print("Exemplo de progressao:")
        entrada_ex = banca_inicial * 0.02
        p1_ex = entrada_ex * mult
        p2_ex = p1_ex * mult if nivel >= 2 else None
        
        print(f"  Entrada: ${entrada_ex:.2f}")
        print(f"  Protecao 1: ${p1_ex:.2f}")
        if p2_ex:
            print(f"  Protecao 2: ${p2_ex:.2f}")
            print(f"  Total em risco: ${entrada_ex + p1_ex + p2_ex:.2f}")
        else:
            print(f"  Total em risco: ${entrada_ex + p1_ex:.2f}")
    
    print("="*60)
    print()

