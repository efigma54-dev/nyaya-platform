
#!/usr/bin/env python3
import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from validation.validation_runner import main

if __name__ == "__main__":
    main()
