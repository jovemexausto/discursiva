#!/bin/bash
set -euo pipefail

if [[ ! -f "pyproject.toml" ]]; then
    echo ">>> Erro: este script deve ser executado a partir da raiz do workspace."
    exit 1
fi

echo ">>> Gerando requirements.txt ..."

# Exporta deps de ambos os apps e consolida sem duplicatas
{
    uv export --package discursiva-api    --no-dev --no-hashes --format requirements-txt
    uv export --package discursiva-worker --no-dev --no-hashes --format requirements-txt
} | grep -vE "discursiva-|-e ./|^#|^\s+#" | sort -u > requirements.txt

echo ">>> requirements.txt gerado com sucesso."
