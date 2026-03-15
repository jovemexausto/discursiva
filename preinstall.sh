#!/bin/bash

# Como não sei onde vai rodar, deixei esse scriptzin só por via das dúvidas, para garantir que o ambiente está OK.
# Só para verificar se docker e uv estão instalados.

CHECK="✅" && CROSS="❌" && INFO="ℹ️" && WHALE="🐳" && PYTHON="🐍" && NODE="📦"
BOLD='\033[1m'&&GREEN='\033[0;32m'&&RED='\033[0;31m'&&BLUE='\033[0;34m'&&CYAN='\033[0;36m' && YELLOW='\033[1;33m'&&NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "----------------------------------------------------------"
echo "              VERIFICAÇÃO DE DEPENDÊNCIAS                 "
echo "----------------------------------------------------------"
echo -e "${NC}"

errors=0

check_uv() {
    echo -ne "  ${PYTHON}  Verificando ${BOLD}UV (Python)${NC}... "
    
    if command -v uv >/dev/null 2>&1; then
        version=$(uv --version 2>&1 | head -n 1)
        echo -e "${GREEN}${BOLD}${CHECK} OK${NC} (${version})"
    else
        echo -e "${RED}${BOLD}${CROSS} NÃO ENCONTRADO${NC}"
        echo -e "${YELLOW}${INFO} Instale em: https://docs.astral.sh/uv/getting-started/installation/${NC}"
        errors=$((errors + 1))
        return 1
    fi
}

check_docker() {
    echo -ne "  ${WHALE}  Verificando ${BOLD}Docker${NC}... "
    
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}${BOLD}${CROSS} NÃO INSTALADO${NC}"
        errors=$((errors + 1))
        return 1
    fi

    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}${BOLD}${CROSS} INSTALADO, MAS NÃO ESTÁ RODANDO${NC}"
        errors=$((errors + 1))
        return 1
    fi

    version=$(docker --version 2>&1 | head -n 1)
    echo -e "${GREEN}${BOLD}${CHECK} OK${NC} (${version})"
}

echo -e "${BLUE}${BOLD}Iniciando diagnóstico do ambiente:${NC}\n"

check_docker
check_uv

echo -e "\n----------------------------------------------------------"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}${BOLD}${CHECK} Tudo pronto! Todas as dependências foram encontradas.${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}${CROSS} Atenção: ${errors} dependência(s) ausente(s).${NC}"
    echo -e "${YELLOW}${INFO} Por favor, instale as ferramentas ausentes para continuar.${NC}"
    exit 1
fi
