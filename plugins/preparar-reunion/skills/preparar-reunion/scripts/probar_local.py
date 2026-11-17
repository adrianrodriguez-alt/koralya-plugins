"""Prueba la guía construida antes de publicarla: http.server + Playwright a 1440 y 390 px.

python probar_local.py <site/> [--capturas <carpeta para las capturas de control>] [--puerto 8799]

Comprueba: errores de consola, imágenes que no cargan, scrollWidth = ancho de la ventana,
ampliación (abre, flechas solo dentro de la ficha, Escape cierra), cambio ES/FR y que no queda
ningún enlace que abra una imagen en otra pestaña. Guarda capturas de control a 1440 y 390 px.
Código de salida 1 si algo falla.
"""
import argparse
import functools
import http.server
import os
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)

CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"]


class Silencioso(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8",
                      ".webp": "image/webp", ".mp4": "video/mp4", ".webm": "video/webm"}

    def log_message(self, *a):
        pass


def lanzar(pw):
    try:
        return pw.chromium.launch(headless=True)
    except Exception:
        exe = next((c for c in CHROMES if os.path.exists(c)), None)
        if not exe:
            raise SystemExit("Sin Chromium: `python -m playwright install chromium`.")
        return pw.chromium.launch(executable_path=exe, headless=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--capturas")
    ap.add_argument("--puerto", type=int, default=8799)
    a = ap.parse_args()
    site = Path(a.site).resolve()
    shots = Path(a.capturas or tempfile.mkdtemp(prefix="control_guia_"))
    shots.mkdir(parents=True, exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.puerto), functools.partial(Silencioso, directory=str(site)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{a.puerto}/index.html"
    fallos = []

    def ok(cond, msg):
        print(("ok  " if cond else "KO  ") + msg)
        if not cond:
            fallos.append(msg)

    with sync_playwright() as pw:
        b = lanzar(pw)
        for w, h in ((1440, 900), (390, 844)):
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            # « Failed to load resource » no dice qué fichero: los 4xx/5xx se registran con su URL (salvo el favicon)
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
            pg.on("response", lambda r: errs.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("favicon.ico") else None)
            pg.on("requestfailed", lambda r: errs.append("no carga: " + r.url) if "ABORTED" not in (r.failure or "") else None)
            pg.add_init_script("try{localStorage.clear()}catch(e){}")
            pg.goto(url, wait_until="networkidle")
            pg.evaluate("() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
            pg.wait_for_timeout(1200)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            ok(sw <= w, f"{w}px · sin desplazamiento horizontal (scrollWidth {sw})")
            rotas = pg.evaluate("() => [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src').slice(0, 60))")
            ok(not rotas, f"{w}px · todas las imágenes cargan" + (f" (rotas: {rotas[:3]})" if rotas else ""))
            cortadas = pg.evaluate("() => [...document.querySelectorAll('.niv, .chip, .filtre, .leyenda .tx, h2.sec, .ficha h4')].filter(e => e.offsetParent && e.scrollWidth > e.clientWidth + 1 && !e.closest('.cadre')).map(e => e.textContent.trim().slice(0, 30))")
            ok(not cortadas, f"{w}px · ninguna pastilla ni título recortado" + (f" (recortados: {cortadas[:4]})" if cortadas else ""))
            logo = pg.evaluate("() => { const i = document.querySelector('.couv img'); return !!i && i.naturalWidth > 0 }")
            ok(logo, f"{w}px · el logo del cliente se ve")
            n_fichas = pg.locator(".ficha").count()
            ok(n_fichas > 0, f"{w}px · {n_fichas} fichas")
            pg.screenshot(path=str(shots / f"control_{w}.png"), full_page=(w == 1440))
            # ampliación: abrir la 1.ª ficha con 2+ capturas, avanzar hasta el final, comprobar que no salta de ficha
            fichas = pg.locator(".ficha")
            prueba = None
            for i in range(n_fichas):
                if fichas.nth(i).locator(".onglets button[data-p]:not(.vid)").count() >= 2:
                    prueba = fichas.nth(i)
                    break
            if prueba is None and n_fichas:
                prueba = fichas.first
            if prueba is not None and prueba.locator(".cadre-vue .ecran").count():
                fid = prueba.get_attribute("id")
                prueba.locator(".cadre-vue .ecran").click()
                pg.wait_for_timeout(300)
                ok(pg.locator("#zoom").is_visible(), f"{w}px · la imagen se amplía dentro de la página ({fid})")
                ok(len(pg.context.pages) == 1, f"{w}px · no abre otra pestaña")
                n = prueba.locator(".onglets button[data-p]:not(.vid)").count() or 1
                for _ in range(n + 2):
                    if pg.locator("#zoom .suiv").is_enabled() and pg.locator("#zoom .suiv").is_visible():
                        pg.locator("#zoom .suiv").click()
                        pg.wait_for_timeout(120)
                titulo = pg.locator("#zoom .z-haut").inner_text()
                nombre = prueba.locator("h4").inner_text()
                ok(nombre.strip() in titulo, f"{w}px · las flechas se quedan en la ficha (« {nombre[:30]} »)")
                if n > 1:
                    ok(pg.locator("#zoom .suiv").is_disabled(), f"{w}px · flecha › desactivada en el último paso")
                if w == 1440:
                    pg.screenshot(path=str(shots / "control_zoom.png"))
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(200)
                ok(not pg.locator("#zoom").is_visible(), f"{w}px · Escape cierra la ampliación")
            # idioma
            if pg.locator(".langue").is_visible():
                es = pg.locator("h1").inner_text()
                pg.locator(".langue button[data-l=fr]").click()
                pg.wait_for_timeout(250)
                fr = pg.locator("h1").inner_text()
                ok(es != fr and pg.evaluate("document.documentElement.lang") == "fr", f"{w}px · ES → FR cambia la página (« {fr[:40]} »)")
                if w == 390:
                    pg.screenshot(path=str(shots / "control_390_fr.png"))
                pg.locator(".langue button[data-l=es]").click()
            if w == 1440:
                for vb in pg.locator(".onglets .vid").all():
                    art = vb.locator("xpath=ancestor::article")
                    fid = art.get_attribute("id")
                    vb.click()
                    pg.wait_for_timeout(150)
                    dur = art.locator("video").evaluate(
                        "v => new Promise(r => { if (v.readyState >= 1) return r(v.duration); v.preload = 'metadata';"
                        " v.onloadedmetadata = () => r(v.duration); v.onerror = () => r(-1); v.load(); setTimeout(() => r(-2), 8000) })")
                    ok(bool(dur) and dur > 0, f"{w}px · el vídeo de « {fid} » carga" + (f" ({dur:.0f} s)" if dur and dur > 0 else ""))
            ok(not errs, f"{w}px · sin errores de consola" + (f": {errs[:3]}" if errs else ""))
            pg.close()
        b.close()
    srv.shutdown()
    print(f"Capturas de control: {shots}")
    print("RESULTADO:", "OK" if not fallos else f"{len(fallos)} fallo(s)")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
