"""
Simulador de leituras RFID
Útil para testar o sistema sem hardware real
"""

import requests
import time
import random
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000/api/registrar-leitura/"
INTERVALO_MIN = 2  # segundos
INTERVALO_MAX = 8  # segundos

# Tags simuladas (250 botijões)
def gerar_tags(quantidade=250):
    """Gera lista de tags RFID simuladas"""
    tags = []
    for i in range(1, quantidade + 1):
        # Formato EPC Gen2 simplificado
        tag = f"E200{i:012d}"
        tags.append(tag)
    return tags

def simular_leituras_continuas():
    """Simula leituras contínuas como se fosse um leitor real"""
    
    print("=" * 70)
    print("  SIMULADOR DE LEITURAS RFID")
    print("=" * 70)
    print(f"\n📡 API: {API_URL}")
    print(f"⏱️  Intervalo: {INTERVALO_MIN}-{INTERVALO_MAX} segundos")
    print("\n🔄 Iniciando simulação...\n")
    print("Pressione Ctrl+C para parar\n")
    
    tags = gerar_tags(250)
    contador = 0
    
    try:
        while True:
            # Escolhe tag aleatória
            tag = random.choice(tags)
            
            # Simula operadores
            operadores = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', '']
            operador = random.choice(operadores)
            
            # Dados da leitura
            dados = {
                'tag_rfid': tag,
                'operador': operador
            }
            
            try:
                # Envia para API
                response = requests.post(API_URL, json=dados, timeout=5)
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                contador += 1
                
                if response.status_code == 200:
                    resultado = response.json()
                    novo = "🆕 NOVO" if resultado.get('novo') else "✅"
                    print(f"[{timestamp}] {novo} Leitura #{contador}: {tag[:20]}... | Op: {operador or 'N/A'}")
                else:
                    print(f"[{timestamp}] ❌ Erro {response.status_code}: {tag}")
                    
            except requests.exceptions.ConnectionError:
                print(f"❌ Erro: Não foi possível conectar à API")
                print(f"   Verifique se o servidor está rodando em {API_URL}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
            
            # Aguarda intervalo aleatório
            intervalo = random.uniform(INTERVALO_MIN, INTERVALO_MAX)
            time.sleep(intervalo)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Simulação interrompida")
        print(f"📊 Total de leituras simuladas: {contador}")


def simular_lote(quantidade=50):
    """Simula um lote de leituras de uma vez"""
    
    print(f"\n📦 Simulando lote de {quantidade} leituras...\n")
    
    tags = gerar_tags(quantidade)
    sucesso = 0
    falhas = 0
    
    for i, tag in enumerate(tags, 1):
        dados = {
            'tag_rfid': tag,
            'operador': 'Simulador'
        }
        
        try:
            response = requests.post(API_URL, json=dados, timeout=5)
            
            if response.status_code == 200:
                sucesso += 1
                print(f"✅ [{i}/{quantidade}] {tag}")
            else:
                falhas += 1
                print(f"❌ [{i}/{quantidade}] {tag} - Erro {response.status_code}")
                
        except Exception as e:
            falhas += 1
            print(f"❌ [{i}/{quantidade}] {tag} - Erro: {e}")
        
        # Pequena pausa para não sobrecarregar
        time.sleep(0.1)
    
    print(f"\n📊 Resultado:")
    print(f"   ✅ Sucesso: {sucesso}")
    print(f"   ❌ Falhas: {falhas}")


def menu():
    """Menu interativo"""
    
    print("=" * 70)
    print("  SIMULADOR DE LEITURAS RFID")
    print("=" * 70)
    print("\nEscolha uma opção:\n")
    print("1. Simular leituras contínuas (modo realista)")
    print("2. Simular lote de 50 leituras")
    print("3. Simular lote de 250 leituras (todos os botijões)")
    print("4. Simular quantidade personalizada")
    print("5. Sair")
    print()
    
    opcao = input("Digite o número da opção: ")
    
    if opcao == '1':
        simular_leituras_continuas()
    elif opcao == '2':
        simular_lote(50)
    elif opcao == '3':
        simular_lote(250)
    elif opcao == '4':
        try:
            qtd = int(input("Quantidade de leituras: "))
            simular_lote(qtd)
        except ValueError:
            print("❌ Quantidade inválida")
    elif opcao == '5':
        print("👋 Até logo!")
        return
    else:
        print("❌ Opção inválida")
    
    print("\n" + "=" * 70 + "\n")
    menu()


if __name__ == "__main__":
    try:
        # Testa conexão com a API
        print("🔍 Testando conexão com a API...")
        response = requests.get("http://localhost:8000/", timeout=3)
        print("✅ Servidor Django está online!\n")
    except:
        print("⚠️ ATENÇÃO: Servidor Django não detectado")
        print(f"   Certifique-se de que está rodando em http://localhost:8000")
        print(f"   Execute: python manage.py runserver\n")
        input("Pressione Enter para continuar mesmo assim...")
    
    menu()
