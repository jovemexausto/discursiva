import sys
from pathlib import Path

here = Path(__file__).parent

# domain src + tests (for fakes)
domain_root = here.parents[1] / "packages/domain"
sys.path.insert(0, str(domain_root / "src"))
sys.path.insert(0, str(domain_root))

# api src
sys.path.insert(0, str(here / "src"))
