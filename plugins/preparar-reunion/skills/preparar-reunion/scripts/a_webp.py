"""Convierte capturas a webp para la guía: lado mayor ≤ 1600 px, calidad 82.

python a_webp.py <origen.png|carpeta> <destino.webp|carpeta> [--max 1600] [--q 82]
"""
import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)

EXT = {".png", ".jpg", ".jpeg", ".webp"}


def a_webp(src, dst, maximo=1600, calidad=82):
    """Escribe dst en webp. Si src ya es webp y cabe, se copia tal cual (sin recomprimir)."""
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        w, h = im.size
        if src.suffix.lower() == ".webp" and max(w, h) <= maximo:
            shutil.copyfile(src, dst)
            return w, h
        im = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
        if max(w, h) > maximo:
            k = maximo / max(w, h)
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=calidad, method=6)
        return w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("origen")
    ap.add_argument("destino")
    ap.add_argument("--max", type=int, default=1600)
    ap.add_argument("--q", type=int, default=82)
    a = ap.parse_args()
    src = Path(a.origen)
    if src.is_dir():
        n = 0
        for f in sorted(src.iterdir()):
            if f.suffix.lower() in EXT:
                a_webp(f, Path(a.destino) / (f.stem + ".webp"), a.max, a.q)
                n += 1
        print(f"{n} imágenes convertidas en {a.destino}")
    elif src.is_file():
        a_webp(src, a.destino, a.max, a.q)
        print(a.destino)
    else:
        sys.exit(f"No existe: {src}")


if __name__ == "__main__":
    main()
