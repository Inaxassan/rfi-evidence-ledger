from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "assets" / "brand" / "rfi-evidence-ledger-mark.png"
target = root / "assets" / "brand" / "rfi-evidence-ledger-mark-512.png"

with Image.open(source) as image:
    prepared = image.resize((512, 512), Image.Resampling.LANCZOS)
    prepared.save(target, "PNG", optimize=True)

print(target)
