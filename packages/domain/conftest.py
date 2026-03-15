import sys
from pathlib import Path

# Garante que tanto src/ quanto o diretório raiz do pacote estejam no path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))
