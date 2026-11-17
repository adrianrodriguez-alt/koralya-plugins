"""Construye la guía (site/index.html + p/*.webp + m/*) a partir de un JSON de contenido.

python construir_guia.py --guia guia.json --capturas <carpeta> [--videos <carpeta>] --salida site/

guia.json: ver references/diseno.md § Formato del JSON (y assets/ejemplos/). Lo esencial:
  "tipo": "novedades" | "pruebas",
  "cliente": {"nombre": "...", "logo": "ruta/logo.svg | data:..."}, "color": "#0052b7" (opcional),
  "textos": {"es": {...}, "fr": {...}} y el contenido del tipo (items/zonas/origenes o contenido.es/fr).
<carpeta de capturas>: imágenes (png/jpg/webp) + boites.json {"nombre": {"b": [[x, y, w, h], ...], "w": 1440, "h": 900}}
  tal como lo escribe capturas_base.py. "capt" dentro del JSON también vale (sustituye a boites.json).

Comprueba antes de escribir: ES y FR con los mismos id, mismos pasos y mismas capturas; capturas y
vídeos que existen; textos demasiado largos (avisos). Sale con código 1 si hay errores.
"""
import argparse
import base64
import json
import mimetypes
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_webp import a_webp  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)

ASSETS = Path(__file__).resolve().parent.parent / "assets"
errores, avisos = [], []


def err(m):
    errores.append(m)


def avi(m):
    avisos.append(m)


def logo_uri(logo, base):
    if not logo:
        return ""
    if logo.startswith("data:") or logo.startswith("http"):
        return logo
    p = (base / logo) if not Path(logo).is_absolute() else Path(logo)
    if not p.exists():
        err(f"logo no encontrado: {p}")
        return ""
    if p.suffix.lower() == ".txt":  # fichero con un data URI ya hecho (logo_datauri.txt)
        return p.read_text(encoding="utf-8").strip()
    mime = "image/svg+xml" if p.suffix.lower() == ".svg" else (mimetypes.guess_type(p.name)[0] or "image/png")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def comprobar_textos(cfg):
    es, fr = cfg["textos"].get("es", {}), cfg["textos"].get("fr", {})
    falta = sorted(set(es) ^ set(fr))
    if falta:
        err(f"textos: claves que solo están en un idioma: {falta}")


def capturas_pruebas(cfg):
    usados = []
    c = cfg["contenido"]
    if set(c) != {"es", "fr"}:
        err("contenido debe tener exactamente 'es' y 'fr'")
        return usados
    se, sf = c["es"]["sections"], c["fr"]["sections"]
    if len(se) != len(sf):
        err(f"secciones: ES {len(se)} / FR {len(sf)}")
    for a, b in zip(se, sf):
        ida, idb = [f["id"] for f in a["fichas"]], [f["id"] for f in b["fichas"]]
        if ida != idb:
            err(f"sección « {a['t']} »: fichas distintas ES {ida} / FR {idb}")
        for fa, fb in zip(a["fichas"], b["fichas"]):
            if [p[1] for p in fa["p"]] != [p[1] for p in fb["p"]]:
                err(f"ficha {fa['id']}: pasos/capturas distintos entre ES y FR")
            if [k[0] for k in fa.get("kit", [])] != [k[0] for k in fb.get("kit", [])]:
                err(f"ficha {fa['id']}: ficheros del kit distintos entre ES y FR")
            if fa.get("cuenta") and fa["cuenta"] not in {x["n"] for x in cfg.get("cuentas", [])} and cfg.get("cuentas"):
                err(f"ficha {fa['id']}: cuenta « {fa['cuenta']} » no está en cuentas")
            for lang, f in (("es", fa), ("fr", fb)):
                if len(f.get("q", "")) > 420:
                    avi(f"ficha {f['id']} ({lang}): párrafo de {len(f['q'])} caracteres; regla: poco texto")
                for t, _ in f["p"]:
                    if len(t) > 170:
                        avi(f"ficha {f['id']} ({lang}): paso largo ({len(t)} car.): « {t[:50]}… »")
            usados += [p[1] for p in fa["p"] if p[1]]
    if [k[0] for k in c["es"].get("kit", [])] != [k[0] for k in c["fr"].get("kit", [])]:
        err("kit general distinto entre ES y FR")
    return usados


def capturas_novedades(cfg):
    usados = []
    zonas = {z["id"] for z in cfg["zonas"]}
    origs = {o["id"] for o in cfg["origenes"]}
    for z in cfg["zonas"]:
        if not (z.get("es") and z.get("fr")):
            err(f"zona {z['id']}: falta es o fr")
    vistos = set()
    for i in cfg["items"]:
        if i["id"] in vistos:
            err(f"mejora repetida: {i['id']}")
        vistos.add(i["id"])
        if i.get("z") not in zonas:
            err(f"mejora {i['id']}: zona « {i.get('z')} » no existe")
        if i.get("o") not in origs:
            err(f"mejora {i['id']}: origen « {i.get('o')} » no existe")
        for lang in ("es", "fr"):
            t = i.get(lang)
            if not t or not t.get("n") or not t.get("q"):
                err(f"mejora {i['id']}: falta {lang}.n o {lang}.q")
                continue
            if len(t["q"]) > 480:
                avi(f"mejora {i['id']} ({lang}): « qué cambia » de {len(t['q'])} caracteres; regla: 1-2 frases")
        if i.get("es") and i.get("fr") and len(i["es"].get("s", [])) != len(i["fr"].get("s", [])):
            err(f"mejora {i['id']}: número de pasos distinto ES {len(i['es'].get('s', []))} / FR {len(i['fr'].get('s', []))}")
        if i.get("es") and len(i["es"].get("s", [])) > 4:
            avi(f"mejora {i['id']}: {len(i['es']['s'])} pasos; regla: 1 a 4")
        if len(i.get("capturas", [])) > 4:
            avi(f"mejora {i['id']}: {len(i['capturas'])} capturas; regla: 1 a 4")
        if not i.get("capturas") and not i.get("video"):
            avi(f"mejora {i['id']}: sin captura ni vídeo")
        usados += i.get("capturas", [])
    return usados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guia", required=True)
    ap.add_argument("--capturas")
    ap.add_argument("--videos")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--solo-idioma", choices=("es", "fr"), help="versión de un solo idioma, sin selector")
    a = ap.parse_args()

    guia = Path(a.guia).resolve()
    cfg = json.loads(guia.read_text(encoding="utf-8"))
    base = guia.parent
    tipo = cfg.get("tipo")
    if tipo not in ("novedades", "pruebas"):
        sys.exit("tipo debe ser 'novedades' o 'pruebas'")
    comprobar_textos(cfg)
    usados = capturas_pruebas(cfg) if tipo == "pruebas" else capturas_novedades(cfg)

    cap_dir = Path(a.capturas).resolve() if a.capturas else None
    boites = dict(cfg.get("capt") or {})
    if cap_dir and (cap_dir / "boites.json").exists():
        boites.update(json.loads((cap_dir / "boites.json").read_text(encoding="utf-8")))

    out = Path(a.salida).resolve()
    (out / "p").mkdir(parents=True, exist_ok=True)
    capt = {}
    for nombre in dict.fromkeys(usados):
        if nombre not in boites:
            err(f"captura « {nombre} » sin recuadros en boites.json")
            continue
        img = None
        for ext in (".webp", ".png", ".jpg", ".jpeg"):
            if cap_dir and (cap_dir / (nombre + ext)).exists():
                img = cap_dir / (nombre + ext)
                break
        if not img:
            err(f"captura « {nombre} »: no está la imagen en {cap_dir}")
            continue
        w, h = a_webp(img, out / "p" / f"{nombre}.webp")
        info = boites[nombre]
        for k, b in enumerate(info["b"]):
            if b[0] < -1 or b[1] < -1 or b[0] + b[2] > 101:
                avi(f"captura {nombre}: recuadro {k + 1} fuera de la pantalla {b}")
        vw = info.get("w", w)
        capt[nombre] = {"img": info.get("img", nombre), "b": info["b"], "w": vw, "r": round(w / h, 4)}
    cfg["capt"] = capt

    if tipo == "novedades":
        vids = [i["video"] for i in cfg["items"] if i.get("video")]
        if vids:
            vdir = Path(a.videos).resolve() if a.videos else None
            (out / "m").mkdir(exist_ok=True)
            for v in vids:
                cand = [vdir / v] if vdir and Path(v).suffix else ([vdir / (v + e) for e in (".mp4", ".webm")] if vdir else [])
                src = next((c for c in cand if c.exists()), None)
                if not src:
                    err(f"vídeo « {v} » no encontrado en {vdir}")
                    continue
                if src.suffix == ".webm" and shutil.which("ffmpeg"):
                    dst = out / "m" / (src.stem + ".mp4")
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-movflags", "+faststart",
                                    "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", str(dst)], check=True)
                else:
                    dst = out / "m" / src.name
                    shutil.copyfile(src, dst)
                for i in cfg["items"]:
                    if i.get("video") == v:
                        i["video"] = dst.name
                poster = next((vdir / f"{src.stem}_poster{e}" for e in (".webp", ".png", ".jpg") if (vdir / f"{src.stem}_poster{e}").exists()), None)
                if poster:
                    a_webp(poster, out / "m" / f"{dst.stem}_poster.webp")
                else:
                    avi(f"vídeo {v}: sin imagen de portada ({src.stem}_poster.png)")

    if a.solo_idioma:
        cfg["solo_idioma"] = a.solo_idioma
    cliente = cfg.get("cliente", {})
    logo = logo_uri(cliente.get("logo"), base)

    for m in avisos:
        print("AVISO:", m)
    if errores:
        for m in errores:
            print("ERROR:", m)
        sys.exit(1)

    css = (ASSETS / "comun" / "estilos.css").read_text(encoding="utf-8")
    if cfg.get("color"):
        css += f"\n:root {{ --bleu: {cfg['color']} }}\n"
    plantilla = (ASSETS / ("novedades" if tipo == "novedades" else "guia_pruebas") / "gabarit.html").read_text(encoding="utf-8")
    datos = {k: v for k, v in cfg.items() if k not in ("cliente",)}
    datos_js = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    titulo = cfg["textos"].get(a.solo_idioma or cfg.get("idioma", "es"), {}).get("titre", cliente.get("nombre", "Guía"))
    html = (plantilla.replace("/*__ESTILOS__*/", css)
            .replace("/*__CFG__*/null", datos_js)
            .replace("__LOGO__", logo)
            .replace("__CLIENTE__", cliente.get("nombre", ""))
            .replace("__TITULO__", titulo.replace("<", "&lt;")))
    (out / "index.html").write_text(html, encoding="utf-8")
    n_caps = len(capt)
    print(f"OK: {out / 'index.html'} · {n_caps} capturas · ES/FR coinciden")


if __name__ == "__main__":
    main()
