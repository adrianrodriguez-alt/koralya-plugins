"""Hoja de control: todas las capturas reducidas con sus recuadros dibujados, para revisarlas de un vistazo.

python planche.py <carpeta de capturas> [salida.png] [--cols 4] [--ancho 420]

Lee <carpeta>/boites.json y las imágenes <nombre>.png|webp. En rojo, los recuadros (el 1.º con su número);
en naranja con « FUERA », los que se salen de la pantalla. Míralo antes de construir la guía.
"""
import argparse
import sys
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)

ROJO, NARANJA = (225, 29, 72), (234, 88, 12)


def fuente(t):
    for f in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(f, t)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("salida", nargs="?")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--ancho", type=int, default=420)
    a = ap.parse_args()
    d = Path(a.carpeta)
    boites = json.loads((d / "boites.json").read_text(encoding="utf-8"))
    f_t, f_n = fuente(15), fuente(13)
    celdas = []
    for nombre, info in boites.items():
        img = next((d / (nombre + e) for e in (".png", ".webp", ".jpg") if (d / (nombre + e)).exists()), None)
        if not img:
            print("falta la imagen de", nombre)
            continue
        im = Image.open(img).convert("RGB")
        k = a.ancho / im.width if im.width >= im.height else (a.ancho * 0.75) / im.height * 1.0
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))))
        dr = ImageDraw.Draw(im)
        W, H = im.size
        for n, (x, y, w, h) in enumerate(info["b"]):
            fuera = x < 0 or y < 0 or x + w > 100 or y + h > 100
            c = NARANJA if fuera else ROJO
            box = [x / 100 * W, y / 100 * H, (x + w) / 100 * W, (y + h) / 100 * H]
            dr.rectangle(box, outline=c, width=3)
            etiqueta = f"{n + 1}" + (" FUERA" if fuera else "")
            tx, ty = max(0, box[0]), max(0, min(box[1] - 18, H - 18))
            tw = dr.textlength(etiqueta, font=f_n) + 8
            dr.rectangle([tx, ty, tx + tw, ty + 17], fill=c)
            dr.text((tx + 4, ty + 1), etiqueta, fill="white", font=f_n)
        if not info["b"]:
            dr.rectangle([0, 0, W - 1, H - 1], outline=NARANJA, width=4)
        celdas.append((nombre, im, len(info["b"])))
    if not celdas:
        raise SystemExit("No hay capturas.")
    cols = min(a.cols, len(celdas))
    cw = a.ancho + 16
    filas = [celdas[i:i + cols] for i in range(0, len(celdas), cols)]
    alto_f = [max(c[1].height for c in f) + 34 for f in filas]
    hoja = Image.new("RGB", (cols * cw + 16, sum(alto_f) + 16), (233, 237, 242))
    dr = ImageDraw.Draw(hoja)
    y = 16
    for f, af in zip(filas, alto_f):
        for i, (nombre, im, nb) in enumerate(f):
            x = 16 + i * cw
            dr.text((x, y), f"{nombre}  ·  {nb} recuadro(s)" if nb else f"{nombre}  ·  SIN RECUADROS", fill=(30, 37, 48) if nb else NARANJA, font=f_t)
            hoja.paste(im, (x, y + 22))
        y += af
    out = Path(a.salida) if a.salida else d / "planche.png"
    hoja.save(out)
    print(f"{out} · {len(celdas)} capturas")


if __name__ == "__main__":
    main()
