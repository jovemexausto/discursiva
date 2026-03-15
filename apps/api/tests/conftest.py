import sys
from pathlib import Path

domain_root = Path(__file__).parents[3] / "packages" / "domain"
infra_src = Path(__file__).parents[3] / "packages" / "infra" / "src"

sys.path.insert(0, str(domain_root / "src"))
sys.path.insert(0, str(domain_root)) # para tests.fakes
sys.path.insert(0, str(infra_src))
