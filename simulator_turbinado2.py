"""
Simulador de leituras RFID - Versão Completa
Simula cenários realistas com TODOS os campos
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
    'Fernando Dias', 'Camila Pereira', 'Marcos Oliveira', 'Luciana Torres',
    'Sistema Automático', ''
]

CLIENTES = [
    'Restaurante Bom Sabor', 'Pizzaria Massa Fina', 'Churrascaria Grill Master',
    'Hotel Presidente', 'Padaria Pão Quente', 'Lanchonete Central',
    'Escola Municipal Santos Dumont', 'Hospital São Lucas', 
    'Condomínio Residencial Jardins', 'Posto de Gasolina Shell',
    'Supermercado Compre Bem', 'Academia Corpo Forte',
    'Salão de Festas Alegria', 'Bar e Restaurante Tropeiro',
    'Indústria Metalúrgica Silva', 'Laboratório de Análises Clínicas',
    'Creche Mundo Infantil', 'Clínica Veterinária Bicho Feliz',
    'Empresa de Eventos Festança', 'Buffet Delícias da Vovó',
    ''
]

LOCALIZACOES = [
    'Portaria Principal', 'Portaria Secundária',
    'Depósito A - Setor 1', 'Depósito A - Setor 2', 'Depósito A - Setor 3',
    'Depósito B - Cheios', 'Depósito B - Vazios',
    'Área de Carga - Doca 1', 'Área de Carga - Doca 2', 'Área de Carga - Doca 3',
    'Área de Descarga - Recebimento', 'Área de Descarga - Inspeção',
    'Pátio Externo - Norte', 'Pátio Externo - Sul',
    'Câmara Fria', 'Sala de Teste e Qualidade',
    'Almoxarifado', 'Área de Manutenção',
    'Em Trânsito - Rota A', 'Em Trânsito - Rota B', 'Em Trânsito - Rota C',
    'Caminhão 001', 'Caminhão 002', 'Caminhão 003',
    'Oficina de Reparos', 'Área de Higienização',
    ''
]

OBSERVACOES = [
    'Leitura normal - Botijão em bom estado',
    'Botijão cheio - Pronto para entrega',
    'Botijão vazio - Retorno de cliente',
    'Primeira carga do dia',
    'Recarga padrão',
    'Inspeção de qualidade aprovada',
    'Inspeção de qualidade - Requer atenção',
    'Manutenção preventiva realizada',
    'Troca de válvula concluída',
    'Conferência de estoque mensal',
    'Saída para entrega - Cliente confirmado',
    'Retorno de entrega - Cliente ausente',
    'Retorno de entrega - Recusado pelo cliente',
    'Botijão com pequeno amassado - OK para uso',
    'Válvula com vazamento - Enviado para manutenção',
    'Em teste de pressão',
    'Aprovado em teste de segurança',
    'Limpeza e higienização completa',
    'Pintura retocada',
    'Etiqueta de segurança renovada',
    'Transferência entre depósitos',
    'Separado para cliente especial',
    'Aguardando coleta',
    'Em quarentena - Aguardando inspeção',
    'Liberado após quarentena',
    ''
]


def gerar_tag_realista():
    """Gera uma tag RFID no formato EPC Gen2 realista"""
    # Formato: E200 + 12 dígitos hexadecimais
    prefixo = "E200"
    numero = ''.join([random.choice('0123456789ABCDEF') for _ in range(12)])
    return f"{prefixo}{numero}"


def exibir_cabecalho():
    """Exibe cabeçalho visual do simulador"""
    print("\n" + "=" * 80)
    print(Fore.CYAN + Style.BRIGHT + "  🔥 SIMULADOR COMPLETO DE LEITURAS RFID 🔥".center(80))
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
    """Simula leituras contínuas com TODOS os dados realistas"""
    
    exibir_cabecalho()
    print(f"📡 API: {Fore.CYAN}{API_URL}")
    print(f"⏱️  Intervalo: {Fore.YELLOW}{INTERVALO_MIN}-{INTERVALO_MAX} segundos")
    print(f"✨ Modo: {Fore.GREEN}DADOS COMPLETOS (Cliente, Localização, Observação)")
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
            
            # Dados COMPLETOS e realistas da leitura
            dados = {
                'tag_rfid': tag,
                'operador': random.choice(OPERADORES),
                'localizacao': random.choice(LOCALIZACOES),
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
                        operador = dados['operador'][:15] if dados['operador'] else 'Sistema'
                        local = dados['localizacao'][:20] if dados['localizacao'] else 'N/A'
                        obs = dados['observacao'][:30] if dados['observacao'] else '-'
                        
                        print(f"{Fore.GREEN}[{timestamp}] 🆕 #{contador}: {tag[:18]}... | "
                              f"Nº: {resultado.get('numero_serie', 'N/A')[:15]}")
                        print(f"          👤 {operador} | 📍 {local}")
                        print(f"          📝 {obs}\n")
                    else:
                        duplicadas += 1
                        print(f"{Fore.YELLOW}[{timestamp}] 🔄 #{contador}: {tag[:18]}... "
                              f"(Duplicada - Total: {resultado.get('total_leituras', '?')})\n")
                else:
                    falhas += 1
                    print(f"{Fore.RED}[{timestamp}] ❌ #{contador}: Erro {response.status_code}\n")
                    
            except requests.exceptions.ConnectionError:
                falhas += 1
                print(f"{Fore.RED}❌ Erro: Não foi possível conectar à API")
                print(f"   Verifique se o servidor está rodando em {API_URL}\n")
                time.sleep(5)
            except Exception as e:
                falhas += 1
                print(f"{Fore.RED}❌ Erro inesperado: {str(e)[:50]}\n")
            
            # Intervalo aleatório
            intervalo = random.uniform(INTERVALO_MIN, INTERVALO_MAX)
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⏹️  Simulação interrompida pelo usuário")
        exibir_estatisticas(sucesso, falhas, duplicadas, tempo_inicio)


def simular_lote(quantidade=50, dados_completos=True):
    """Simula um lote de leituras com dados completos"""
    
    print(f"\n{Fore.CYAN}📦 Simulando lote de {quantidade} leituras...")
    if dados_completos:
        print(f"{Fore.GREEN}✨ Modo COMPLETO: Cliente, Localização e Observação\n")
    else:
        print(f"{Fore.YELLOW}⚡ Modo RÁPIDO: Apenas dados essenciais\n")
    
    sucesso = 0
    falhas = 0
    duplicadas = 0
    tempo_inicio = time.time()
    
    # Barra de progresso
    largura_barra = 50
    
    for i in range(1, quantidade + 1):
        # Gera tag única
        tag = gerar_tag_realista()
        
        if dados_completos:
            dados = {
                'tag_rfid': tag,
                'operador': random.choice(OPERADORES),
                'localizacao': random.choice(LOCALIZACOES),
                'observacao': random.choice(OBSERVACOES),
            }
        else:
            dados = {
                'tag_rfid': tag,
                'operador': 'Simulador',
                'localizacao': '',
                'observacao': '',
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


def simular_cenario_dia_trabalho():
    """Simula um dia completo de operação com turnos e clientes variados"""
    
    exibir_cabecalho()
    print(f"{Fore.CYAN}🏭 SIMULAÇÃO: Dia Típico de Operação - DADOS COMPLETOS\n")
    
    cenarios = [
        ("☀️ Turno Manhã - Recebimento e Inspeção", 25, INTERVALO_MIN * 2),
        ("🌤️ Turno Tarde - Expedição para Clientes", 35, INTERVALO_MIN * 1.5),
        ("🌙 Turno Noite - Conferência e Organização", 15, INTERVALO_MIN * 3),
    ]
    
    total_sucesso = 0
    total_falhas = 0
    total_duplicadas = 0
    tempo_total = time.time()
    
    for nome_turno, quantidade, intervalo in cenarios:
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{nome_turno} ({quantidade} operações)")
        print(f"{'='*80}\n")
        
        tempo_turno = time.time()
        sucesso = 0
        falhas = 0
        duplicadas = 0
        
        for i in range(1, quantidade + 1):
            tag = gerar_tag_realista()
            
            # Dados completos e contextualizados por turno
            dados = {
                'tag_rfid': tag,
                'operador': random.choice(OPERADORES),
                'localizacao': random.choice(LOCALIZACOES),
                'observacao': random.choice(OBSERVACOES),
            }
            
            try:
                response = requests.post(API_URL, json=dados, timeout=5)
                if response.status_code == 200:
                    resultado = response.json()
                    if resultado.get('novo'):
                        sucesso += 1
                        print(f"{Fore.GREEN}✅ [{i:02d}/{quantidade}] {tag[:20]}...")
                        print(f"   Nº Série: {resultado.get('numero_serie', 'N/A')}")
                        print(f"   👤 {dados['operador'] or 'Sistema'}")
                        print(f"   📍 {dados['localizacao'] or 'N/A'}")
                        print(f"   📝 {dados['observacao'][:40] or '-'}\n")
                    else:
                        duplicadas += 1
                        print(f"{Fore.YELLOW}🔄 [{i:02d}/{quantidade}] {tag[:20]}... (duplicada)\n")
                else:
                    falhas += 1
                    print(f"{Fore.RED}❌ [{i:02d}/{quantidade}] Erro {response.status_code}\n")
            except Exception as e:
                falhas += 1
                print(f"{Fore.RED}❌ [{i:02d}/{quantidade}] Erro: {str(e)[:40]}\n")
            
            time.sleep(intervalo)
        
        tempo_decorrido = time.time() - tempo_turno
        print(f"\n{Fore.CYAN}📊 Turno concluído em {tempo_decorrido:.1f}s")
        print(f"   ✅ {sucesso} | ❌ {falhas} | 🔄 {duplicadas}\n")
        
        total_sucesso += sucesso
        total_falhas += falhas
        total_duplicadas += duplicadas
    
    print("\n" + "=" * 80)
    print(f"{Fore.GREEN + Style.BRIGHT}🏁 RESUMO DO DIA".center(90))
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
    print(f"{Fore.GREEN}1. {Fore.WHITE}🔄 Leituras contínuas (dados completos)")
    print(f"{Fore.GREEN}2. {Fore.WHITE}📦 Lote rápido - 50 leituras (dados completos)")
    print(f"{Fore.GREEN}3. {Fore.WHITE}📦 Lote grande - 250 leituras (dados completos)")
    print(f"{Fore.GREEN}4. {Fore.WHITE}🎯 Quantidade personalizada")
    print(f"{Fore.GREEN}5. {Fore.WHITE}🏭 Simular dia de trabalho completo (turnos)")
    print(f"{Fore.GREEN}6. {Fore.WHITE}⚡ Teste de carga - 500 leituras (modo rápido)")
    print(f"{Fore.GREEN}7. {Fore.WHITE}📋 Simular entrega para clientes (20 leituras)")
    print(f"{Fore.RED}8. {Fore.WHITE}🚪 Sair\n")
    
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
            simular_cenario_dia_trabalho()
        elif opcao == '6':
            print(f"\n{Fore.YELLOW}⚠️  ATENÇÃO: Teste de carga intenso!")
            confirma = input(f"{Fore.CYAN}Continuar? (s/n): {Fore.WHITE}").lower()
            if confirma == 's':
                simular_lote(500, dados_completos=False)
        elif opcao == '7':
            print(f"\n{Fore.CYAN}📦 Simulando entregas para clientes...\n")
            simular_lote(20, dados_completos=True)
        elif opcao == '8':
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
