"""
Simulador de leituras RFID - Versão Turbinada
Simula cenários realistas do dia a dia
"""

import requests
import time
import random
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Inicializa colorama para cores no terminal
init(autoreset=True)

# Configuração
API_URL = "http://localhost:8000/api/registrar-leitura/"
INTERVALO_MIN = 1  # segundos
INTERVALO_MAX = 5  # segundos

# Dados realistas para simulação
OPERADORES = [
    'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima',
    'Carlos Souza', 'Juliana Alves', 'Roberto Fernandes', 'Patrícia Rocha',
    'Fernando Dias', 'Camila Pereira', 'Sistema Automático', ''
]

OBSERVACOES = [
    'Leitura normal',
    'Botijão cheio',
    'Botijão vazio - retorno',
    'Primeira carga',
    'Recarga',
    'Inspeção de qualidade',
    'Manutenção preventiva',
    'Troca de válvula',
    'Conferência de estoque',
    'Saída para entrega',
    'Retorno de entrega',
    'Botijão danificado',
    'Em teste',
    ''
]

LOCALIZACOES = [
    'Portaria Principal',
    'Depósito A',
    'Depósito B',
    'Área de Carga',
    'Área de Descarga',
    'Pátio Externo',
    'Câmara Fria',
    'Almoxarifado',
    'Em Trânsito',
    'Manutenção',
    ''
]


def gerar_tag_realista():
    """Gera uma tag RFID no formato EPC Gen2 realista"""
    # Formato: E200 + 12 dígitos hexadecimais
    prefixo = "E200"
    numero = ''.join([random.choice('0123456789ABCDEF') for _ in range(12)])
    return f"{prefixo}{numero}"


def gerar_numero_serie():
    """Gera número de série realista"""
    prefixos = ['BT', 'CIL', 'GLP', 'BOT']
    ano = random.randint(2020, 2025)
    numero = random.randint(1000, 9999)
    return f"{random.choice(prefixos)}-{ano}-{numero}"


def exibir_cabecalho():
    """Exibe cabeçalho visual do simulador"""
    print("\n" + "=" * 80)
    print(Fore.CYAN + Style.BRIGHT + "  🔥 SIMULADOR AVANÇADO DE LEITURAS RFID 🔥".center(80))
    print("=" * 80 + "\n")


def exibir_estatisticas(sucesso, falhas, duplicadas, tempo_inicio):
    """Exibe estatísticas da simulação"""
    tempo_decorrido = time.time() - tempo_inicio
    total = sucesso + falhas
    taxa_sucesso = (sucesso / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 80)
    print(Fore.GREEN + Style.BRIGHT + "  📊 ESTATÍSTICAS DA SIMULAÇÃO".center(80))
    print("=" * 80)
    print(f"  ✅ Leituras bem-sucedidas: {Fore.GREEN}{sucesso}")
    print(f"  ❌ Falhas: {Fore.RED}{falhas}")
    print(f"  🔄 Leituras duplicadas (ignoradas): {Fore.YELLOW}{duplicadas}")
    print(f"  📈 Taxa de sucesso: {Fore.CYAN}{taxa_sucesso:.1f}%")
    print(f"  ⏱️  Tempo decorrido: {Fore.MAGENTA}{tempo_decorrido:.1f}s")
    print(f"  ⚡ Velocidade média: {Fore.CYAN}{(total/tempo_decorrido):.2f} leituras/s" if tempo_decorrido > 0 else "")
    print("=" * 80 + "\n")


def simular_leituras_continuas():
    """Simula leituras contínuas com dados realistas"""
    
    exibir_cabecalho()
    print(f"📡 API: {Fore.CYAN}{API_URL}")
    print(f"⏱️  Intervalo: {Fore.YELLOW}{INTERVALO_MIN}-{INTERVALO_MAX} segundos")
    print(f"\n{Fore.GREEN}🔄 Iniciando simulação contínua...")
    print(f"{Fore.YELLOW}Pressione Ctrl+C para parar\n")
    
    contador = 0
    sucesso = 0
    falhas = 0
    duplicadas = 0
    tempo_inicio = time.time()
    tags_usadas = set()
    
    try:
        while True:
            # Gera tag (30% de chance de repetir uma existente)
            if tags_usadas and random.random() < 0.3:
                tag = random.choice(list(tags_usadas))
            else:
                tag = gerar_tag_realista()
                tags_usadas.add(tag)
            
            # Dados realistas da leitura
            dados = {
                'tag_rfid': tag,
                'operador': random.choice(OPERADORES),
                'observacao': random.choice(OBSERVACOES),
            }
            
            try:
                response = requests.post(API_URL, json=dados, timeout=5)
                timestamp = datetime.now().strftime('%H:%M:%S')
                contador += 1
                
                if response.status_code == 200:
                    resultado = response.json()
                    
                    if resultado.get('novo'):
                        sucesso += 1
                        print(f"{Fore.GREEN}[{timestamp}] 🆕 NOVO #{contador}: {tag[:20]}... | "
                              f"Op: {dados['operador'][:15] or 'N/A'} | {dados['observacao'][:20]}")
                    else:
                        duplicadas += 1
                        print(f"{Fore.YELLOW}[{timestamp}] 🔄 DUP #{contador}: {tag[:20]}... | "
                              f"Total: {resultado.get('total_leituras', '?')}")
                else:
                    falhas += 1
                    print(f"{Fore.RED}[{timestamp}] ❌ Erro {response.status_code}: {tag[:20]}...")
                    
            except requests.exceptions.ConnectionError:
                falhas += 1
                print(f"{Fore.RED}❌ Erro: Não foi possível conectar à API")
                print(f"   Verifique se o servidor está rodando em {API_URL}")
                time.sleep(5)
            except Exception as e:
                falhas += 1
                print(f"{Fore.RED}❌ Erro inesperado: {str(e)[:50]}")
            
            # Intervalo aleatório
            intervalo = random.uniform(INTERVALO_MIN, INTERVALO_MAX)
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⏹️  Simulação interrompida pelo usuário")
        exibir_estatisticas(sucesso, falhas, duplicadas, tempo_inicio)


def simular_lote(quantidade=50, dados_completos=True):
    """Simula um lote de leituras"""
    
    print(f"\n{Fore.CYAN}📦 Simulando lote de {quantidade} leituras...")
    if dados_completos:
        print(f"{Fore.GREEN}✨ Modo completo: Gerando dados realistas\n")
    
    sucesso = 0
    falhas = 0
    duplicadas = 0
    tempo_inicio = time.time()
    
    # Barra de progresso
    largura_barra = 50
    
    for i in range(1, quantidade + 1):
        # Gera dados
        tag = gerar_tag_realista()
        
        dados = {
            'tag_rfid': tag,
            'operador': random.choice(OPERADORES) if dados_completos else 'Simulador',
            'observacao': random.choice(OBSERVACOES) if dados_completos else '',
        }
        
        try:
            response = requests.post(API_URL, json=dados, timeout=5)
            
            if response.status_code == 200:
                resultado = response.json()
                if resultado.get('novo'):
                    sucesso += 1
                    status = f"{Fore.GREEN}✅"
                else:
                    duplicadas += 1
                    status = f"{Fore.YELLOW}🔄"
            else:
                falhas += 1
                status = f"{Fore.RED}❌"
                
        except Exception as e:
            falhas += 1
            status = f"{Fore.RED}❌"
        
        # Exibe progresso
        progresso = i / quantidade
        blocos = int(largura_barra * progresso)
        barra = "█" * blocos + "░" * (largura_barra - blocos)
        percentual = progresso * 100
        
        print(f"\r{status} [{barra}] {percentual:.1f}% ({i}/{quantidade})", end='', flush=True)
        
        # Pequena pausa
        time.sleep(0.05)
    
    print()  # Nova linha
    exibir_estatisticas(sucesso, falhas, duplicadas, tempo_inicio)


def simular_cenario_realista():
    """Simula um dia típico de trabalho"""
    
    exibir_cabecalho()
    print(f"{Fore.CYAN}🏭 SIMULAÇÃO: Dia Típico de Operação\n")
    
    cenarios = [
        ("☀️ Turno Manhã - Recebimento", 30, INTERVALO_MIN * 2),
        ("🌤️ Turno Tarde - Expedição", 40, INTERVALO_MIN * 1.5),
        ("🌙 Turno Noite - Conferência", 20, INTERVALO_MIN * 3),
    ]
    
    total_sucesso = 0
    total_falhas = 0
    total_duplicadas = 0
    tempo_total = time.time()
    
    for nome_turno, quantidade, intervalo in cenarios:
        print(f"\n{Fore.YELLOW}{nome_turno} ({quantidade} operações)")
        print("─" * 80)
        
        tempo_turno = time.time()
        sucesso = 0
        falhas = 0
        duplicadas = 0
        
        for i in range(1, quantidade + 1):
            tag = gerar_tag_realista()
            dados = {
                'tag_rfid': tag,
                'operador': random.choice(OPERADORES),
                'observacao': random.choice(OBSERVACOES),
            }
            
            try:
                response = requests.post(API_URL, json=dados, timeout=5)
                if response.status_code == 200:
                    resultado = response.json()
                    if resultado.get('novo'):
                        sucesso += 1
                        print(f"{Fore.GREEN}✅ [{i:02d}/{quantidade}] {tag[:20]}... | {dados['observacao'][:30]}")
                    else:
                        duplicadas += 1
                        print(f"{Fore.YELLOW}🔄 [{i:02d}/{quantidade}] {tag[:20]}... (duplicada)")
                else:
                    falhas += 1
                    print(f"{Fore.RED}❌ [{i:02d}/{quantidade}] Erro {response.status_code}")
            except Exception as e:
                falhas += 1
                print(f"{Fore.RED}❌ [{i:02d}/{quantidade}] Erro: {str(e)[:40]}")
            
            time.sleep(intervalo)
        
        tempo_decorrido = time.time() - tempo_turno
        print(f"\n{Fore.CYAN}📊 Turno concluído em {tempo_decorrido:.1f}s")
        print(f"   ✅ {sucesso} | ❌ {falhas} | 🔄 {duplicadas}")
        
        total_sucesso += sucesso
        total_falhas += falhas
        total_duplicadas += duplicadas
    
    print("\n" + "=" * 80)
    print(f"{Fore.GREEN + Style.BRIGHT}🏁 RESUMO DO DIA".center(80))
    print("=" * 80)
    tempo_total_decorrido = time.time() - tempo_total
    print(f"  ✅ Total de sucesso: {Fore.GREEN}{total_sucesso}")
    print(f"  ❌ Total de falhas: {Fore.RED}{total_falhas}")
    print(f"  🔄 Total de duplicadas: {Fore.YELLOW}{total_duplicadas}")
    print(f"  ⏱️  Tempo total: {Fore.MAGENTA}{tempo_total_decorrido:.1f}s")
    print("=" * 80 + "\n")


def menu():
    """Menu interativo"""
    
    exibir_cabecalho()
    
    print(f"{Fore.CYAN}Escolha uma opção:\n")
    print(f"{Fore.GREEN}1. {Fore.WHITE}🔄 Leituras contínuas (modo realista)")
    print(f"{Fore.GREEN}2. {Fore.WHITE}📦 Lote rápido (50 leituras)")
    print(f"{Fore.GREEN}3. {Fore.WHITE}📦 Lote grande (250 leituras)")
    print(f"{Fore.GREEN}4. {Fore.WHITE}🎯 Quantidade personalizada")
    print(f"{Fore.GREEN}5. {Fore.WHITE}🏭 Simular dia de trabalho (cenário realista)")
    print(f"{Fore.GREEN}6. {Fore.WHITE}⚡ Teste de carga (500 leituras rápidas)")
    print(f"{Fore.RED}7. {Fore.WHITE}🚪 Sair\n")
    
    try:
        opcao = input(f"{Fore.YELLOW}Digite o número da opção: {Fore.WHITE}")
        
        if opcao == '1':
            simular_leituras_continuas()
        elif opcao == '2':
            simular_lote(50, dados_completos=True)
        elif opcao == '3':
            simular_lote(250, dados_completos=True)
        elif opcao == '4':
            try:
                qtd = int(input(f"{Fore.CYAN}Quantidade de leituras: {Fore.WHITE}"))
                completo = input(f"{Fore.CYAN}Dados completos? (s/n): {Fore.WHITE}").lower() == 's'
                simular_lote(qtd, dados_completos=completo)
            except ValueError:
                print(f"{Fore.RED}❌ Quantidade inválida")
        elif opcao == '5':
            simular_cenario_realista()
        elif opcao == '6':
            print(f"\n{Fore.YELLOW}⚠️  ATENÇÃO: Teste de carga intenso!")
            confirma = input(f"{Fore.CYAN}Continuar? (s/n): {Fore.WHITE}").lower()
            if confirma == 's':
                simular_lote(500, dados_completos=False)
        elif opcao == '7':
            print(f"\n{Fore.CYAN}👋 Até logo!")
            return
        else:
            print(f"{Fore.RED}❌ Opção inválida")
        
        input(f"\n{Fore.YELLOW}Pressione Enter para voltar ao menu...")
        menu()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Até logo!")
        return


if __name__ == "__main__":
    try:
        # Testa conexão
        print(f"{Fore.CYAN}🔍 Testando conexão com a API...")
        response = requests.get("http://localhost:8000/", timeout=3)
        print(f"{Fore.GREEN}✅ Servidor Django está online!\n")
    except:
        print(f"{Fore.RED}⚠️  ATENÇÃO: Servidor Django não detectado")
        print(f"   Certifique-se de que está rodando em http://localhost:8000")
        print(f"   Execute: {Fore.CYAN}python manage.py runserver\n")
        input(f"{Fore.YELLOW}Pressione Enter para continuar mesmo assim...")
    
    menu()
