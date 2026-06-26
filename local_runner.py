
import asyncio
import sys
import subprocess
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))
print(f"✅ Added {backend_dir} to PYTHONPATH")

# Run all phases!
async def run_pipeline():
    # First check docker containers are healthy
    print("\n🔍 Checking Docker containers...")
    try:
        ps_result = subprocess.run(
            ["docker", "compose", "ps"],
            capture_output=True, text=True
        )
        print(ps_result.stdout)
    except Exception as e:
        print(f"⚠️  Docker not running? {e}")
        print("Using local services (localhost)...")

    print("\n--- Starting Pipeline ---")

    # Step 1: Run seed script
    print("\n📦 Step 1: Seeding BNS Corpus...")
    try:
        from scripts.seed_bns_comprehensive import seed_bns_sections
        await seed_bns_sections()
        print("✅ Seed complete!")
    except Exception as e:
        print(f"⚠️  Seed error: {e}")
        print("(DB/Qdrant may not be running locally yet)")

    # Step 2: Run embed script
    print("\n🔢 Step 2: Embedding Sections...")
    try:
        from scripts.embed_all_sections import embed_all_sections
        await embed_all_sections()
        print("✅ Embedding complete!")
    except Exception as e:
        print(f"⚠️  Embedding error: {e}")

    # Step3: Run validation
    print("\n📊 Step3: Validating Corpus...")
    try:
        from scripts.validate_corpus import validate_corpus
        await validate_corpus()
        print("✅ Validation complete! Reports saved!")
    except Exception as e:
        print(f"⚠️  Validation error: {e}")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
