
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Now import and run
from scripts.seed_bns_comprehensive import seed_bns_sections
import asyncio

asyncio.run(seed_bns_sections())
