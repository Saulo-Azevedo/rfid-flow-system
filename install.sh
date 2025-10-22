#!/bin/bash

echo "=================================="
echo "  INSTALAÇÃO - SISTEMA RFID MVP"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica se Python está instalado
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo "   Instale Python 3.10 ou superior"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION encontrado${NC}"
echo ""

# Cria ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${RED}❌ Erro ao criar ambiente virtual${NC}"
    exit 1
fi
echo ""

# Ativa ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate
echo -e "${GREEN}✅ Ambiente ativado${NC}"
echo ""

# Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip atualizado${NC}"
echo ""

# Instala dependências
echo "📚 Instalando dependências..."
echo "   (Isso pode levar alguns minutos)"
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências${NC}"
    exit 1
fi
echo ""

# Cria arquivo .env se não existir
if [ ! -f .env ]; then
    echo "⚙️  Criando arquivo de configuração..."
    cp .env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
    echo -e "${YELLOW}⚠️  ATENÇÃO: Edite o arquivo .env com suas configurações${NC}"
else
    echo -e "${YELLOW}ℹ️  Arquivo .env já existe${NC}"
fi
echo ""

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p temp_exports
mkdir -p media
mkdir -p staticfiles
echo -e "${GREEN}✅ Diretórios criados${NC}"
echo ""

# Executa migrações
echo "🗄️  Executando migrações do banco de dados..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Banco de dados criado${NC}"
else
    echo -e "${RED}❌ Erro nas migrações${NC}"
    exit 1
fi
echo ""

# Coleta arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✅ Arquivos estáticos coletados${NC}"
echo ""

# Pergunta se quer criar superusuário
echo "👤 Deseja criar um superusuário agora? (s/n)"
read -r resposta

if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    python manage.py createsuperuser
fi
echo ""

# Resumo
echo "=================================="
echo -e "${GREEN}  ✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo "=================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Conecte o leitor RFID (se tiver)"
echo "3. Inicie o servidor:"
echo ""
echo -e "   ${GREEN}python manage.py runserver${NC}"
echo ""
echo "4. Acesse: http://localhost:8000"
echo ""
echo "5. Para testar sem hardware:"
echo ""
echo -e "   ${GREEN}python leitor/simulator.py${NC}"
echo ""
echo "=================================="
