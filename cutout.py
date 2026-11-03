#!/usr/bin/env python3
"""
Remove the background from guest photos so they sit on the board like the poster.

    pip install "rembg[cpu]"
    python cutout.py raw/segui.jpg raw/delacruz.jpg      # → photos/segui.png, photos/delacruz.png

The first run downloads the person-segmentation model (~170 MB).
"""
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

out_dir = Path(__file__).parent / "photos"
out_dir.mkdir(exist_ok=True)
session = new_session("isnet-general-use")

for src in sys.argv[1:]:
    img = Image.open(src).convert("RGB")
    cut = remove(img, session=session)
    cut = cut.crop(cut.getbbox())          # trim empty space so the photo sits on the footer line
    dst = out_dir / (Path(src).stem + ".png")
    cut.save(dst)
    print(f"{src} -> {dst}")
