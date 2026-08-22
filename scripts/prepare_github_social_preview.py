from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "assets" / "brand" / "rfi-evidence-ledger-social-preview-wide.png"
target = root / "assets" / "brand" / "rfi-evidence-ledger-social-preview.jpg"

with Image.open(source) as image:
    width, height = image.size
    target_height = width // 2
    top = (height - target_height) // 2
    cropped = image.crop((0, top, width, top + target_height))
    prepared = cropped.resize((1280, 640), Image.Resampling.LANCZOS).convert("RGB")
    prepared.save(target, "JPEG", quality=92, optimize=True)

print(target)
