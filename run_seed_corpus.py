
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
# Also add scripts directory so we can import _bootstrap
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# Import _bootstrap
import _bootstrap
_bootstrap.ensure_backend_on_path()

# Now import seed_corpus_v2 from scripts
import sys
sys.path.insert(0, str(Path(__file__).parent))
from scripts.seed_corpus_v2 import seed
import asyncio

asyncio.run(seed())
