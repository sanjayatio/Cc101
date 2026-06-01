import sys
from pathlib import Path

# Add project root to sys.path so `gfl2` is importable when running pytest
# from any working directory.
sys.path.insert(0, str(Path(__file__).parent.parent))
