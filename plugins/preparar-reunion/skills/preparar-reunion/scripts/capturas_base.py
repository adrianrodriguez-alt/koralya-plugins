"""Capturas de producción con recuadros rojos para las guías (Playwright).

Uso como módulo (recorridos complejos):
    import sys; sys.path.insert(0, "<skill>/scripts")
    from capturas_base import Capturador
    cap = Capturador("https://app.cliente.koralya.com", "capturas", dispositivo="pc")
    pg = cap.connecter("bureau.demo@…", "clave")            # login con selectores por defecto (Django)
    pg.goto(cap.url("/commandes/"))
    cap.shot("arc_1", "text=9900001", "button:has-text('ARC')")   # el 1.er recuadro lleva la etiqueta
    with cap.video("regle_ia"):                              # vídeo 10-25 s + portada
        ...
    cap.fin()

Explorar la aplicación antes de elegir pantallas (página completa de cada ruta + recursos rotos):
    python capturas_base.py --explorar guion.json rutas.txt      -> explora/explora_<ruta>.png

Uso con guion JSON:
    python capturas_base.py guion.json
    {"base_url": "https://…", "salida": "capturas",
     "login": {"url": "/accounts/login/", "usuario": "#id_username", "clave": "#id_password", "entrar": "button[type=submit]"},
     "cuentas": {"bureau": {"usuario": "…", "clave": "…"}},
     "recorridos": [{"cuenta": "bureau", "dispositivo": "pc", "video": null,
        "pasos": [{"ir": "/commandes/"}, {"rellenar": ["#q", "9900001"]}, {"clic": "text=ARC"},
                  {"subir": ["input[type=file]", "kit/ARC.pdf"]}, {"esperar": ".resultat"},
                  {"captura": "arc_3", "marcas": [".resultat", "#id_date"], "haut": null}]}]}
    Otros pasos: {"elegir": [sel, valor]}, {"tecla": "Escape"}, {"pausa": ms}, {"pasar": sel} (hover, menús),
    {"arrastrar": [origen, destino]} (kanban), y en "captura" "toasts": true para dejar ver el toast.
    Login solo por perfil: en la cuenta {"clics": ["label[for=p-lamine]"]} y usuario/clave vacíos o los de la pantalla.

Recuadros: % del viewport (no de la página entera), margen de 6 px, en <salida>/boites.json
({"arc_1": {"b": [[x, y, w, h], ...], "w": 1440, "h": 900}}). La página solo se desplaza hacia el
primer recuadro; con haut=<selector> se alinea ese bloque arriba (campos que no caben en pantalla).
"""
import contextlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)

DISPOSITIVOS = {
    "pc": {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
    "tablet": {"viewport": {"width": 1180, "height": 820}, "device_scale_factor": 1, "has_touch": True},
    "movil": {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2, "is_mobile": True, "has_touch": True},
}
# Toasts y mensajes flotantes: se ocultan siempre antes de capturar.
OCULTAR = ["#toasts", ".toasts", ".toast", ".toast-container", ".messages", ".alert-dismissible", ".django-messages", "#djDebug"]
CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"]
LOGIN = {"url": "/accounts/login/",
         "usuario": "input[name=username], input[name=email], input[type=email], #id_username, #id_login",
         "clave": "input[type=password]",
         "entrar": "button[type=submit], input[type=submit]"}


class Capturador:
    def __init__(self, base_url, salida="capturas", dispositivo="pc", ocultar=None, headless=True, marge=6):
        self.base = base_url.rstrip("/")
        self.salida = Path(salida)
        self.salida.mkdir(parents=True, exist_ok=True)
        self.dispositivo = dispositivo
        self.ocultar = OCULTAR + list(ocultar or [])
        self.marge = marge
        self.boites_path = self.salida / "boites.json"
        self.boites = json.loads(self.boites_path.read_text(encoding="utf-8")) if self.boites_path.exists() else {}
        self._pw = sync_playwright().start()
        args = {"headless": headless, "args": ["--lang=fr-FR"], "env": {**os.environ, "LANG": "fr_FR.UTF-8"}}
        try:
            self.browser = self._pw.chromium.launch(**args)
        except Exception:
            exe = next((c for c in CHROMES if os.path.exists(c)), None)
            if not exe:
                raise SystemExit("Sin Chromium: ejecuta `python -m playwright install chromium`.")
            self.browser = self._pw.chromium.launch(executable_path=exe, **args)
        self.ctx = None
        self.page = None
        self._storage = None
        self.nueva_pagina(dispositivo)

    # ---------- utilidades ----------
    def url(self, ruta):
        return ruta if ruta.startswith("http") else self.base + "/" + ruta.lstrip("/")

    def _css_ocultar(self):
        return ",".join(self.ocultar) + "{display:none!important}"

    def nueva_pagina(self, dispositivo=None, video_dir=None, limpia=False):
        """Contexto nuevo (francés, Europa/París). Conserva la sesión iniciada salvo con limpia=True."""
        if self.ctx:
            self._storage = None if limpia else self.ctx.storage_state()
            self.ctx.close()
        elif limpia:
            self._storage = None
        self.dispositivo = dispositivo or self.dispositivo
        opts = dict(DISPOSITIVOS[self.dispositivo], locale="fr-FR", timezone_id="Europe/Paris", storage_state=self._storage)
        if video_dir:
            opts["record_video_dir"] = str(video_dir)
            opts["record_video_size"] = opts["viewport"]
        self.ctx = self.browser.new_context(**opts)
        css = self._css_ocultar()
        self.ctx.add_init_script(
            "(()=>{const s=document.createElement('style');s.textContent=%s;"
            "const add=()=>document.head?document.head.appendChild(s):requestAnimationFrame(add);add();})()" % json.dumps(css))
        self.page = self.ctx.new_page()
        return self.page

    def connecter(self, usuario, clave, url=None, sel_usuario=None, sel_clave=None, sel_entrar=None, esperar=None, clics=None):
        """Inicia sesión con una cuenta. Después de entrar espera a que cambie la URL (o al selector `esperar`).
        clics: selectores que se pulsan antes de « entrar » (elegir un perfil, aceptar cookies, una pestaña…).
        Con usuario/clave vacíos no se rellenan esos campos (login solo por perfil)."""
        pg = self.page
        pg.goto(self.url(url or LOGIN["url"]), wait_until="domcontentloaded")
        if usuario:
            pg.locator(sel_usuario or LOGIN["usuario"]).first.fill(usuario)
        if clave:
            pg.locator(sel_clave or LOGIN["clave"]).first.fill(clave)
        for c in clics or []:
            pg.locator(c).first.click()
        antes = pg.url
        pg.locator(sel_entrar or LOGIN["entrar"]).first.click()
        if esperar:
            pg.wait_for_selector(esperar, timeout=30000)
        else:
            pg.wait_for_url(lambda u: u != antes, timeout=30000)
        pg.wait_for_load_state("networkidle")
        return pg

    def _loc(self, m):
        return self.page.locator(m).first if isinstance(m, str) else m

    def shot(self, nombre, *marcas, haut=None, pausa=350, toasts=False, raton_fuera=True):
        """Captura del viewport y recuadros en % (el primero lleva la etiqueta del paso en la guía).
        marcas: selectores, Locators o dicts {"x","y","w","h"} en px del viewport.
        toasts=True: deja ver los toasts en esta captura (solo cuando el toast ES el resultado del paso)."""
        pg = self.page
        if toasts:
            pg.add_style_tag(content=",".join(self.ocultar) + "{display:revert!important}")
        else:
            pg.add_style_tag(content=self._css_ocultar())
        vp = pg.viewport_size
        if haut:
            self._loc(haut).evaluate("e => e.scrollIntoView({block: 'start'})")
        elif marcas and not isinstance(marcas[0], dict):
            primero = self._loc(marcas[0])
            primero.scroll_into_view_if_needed()
            r = primero.bounding_box()
            # pegado al borde tras el desplazamiento: margen de 80 px para que se vean el recuadro y su etiqueta
            if r and (r["y"] < 40 or r["y"] + r["height"] > vp["height"] - 10) and r["height"] < vp["height"] - 120:
                pg.evaluate(f"window.scrollBy(0, {r['y'] - 80})")
        if raton_fuera:
            pg.mouse.move(vp["width"] - 1, vp["height"] - 1)  # sin hover ni tooltip del clic anterior
        pg.wait_for_timeout(pausa)
        b = []
        for m in marcas:
            if isinstance(m, dict):
                r = m
            else:
                r = self._loc(m).bounding_box()
                if not r:
                    print(f"AVISO {nombre}: « {m} » no es visible; recuadro omitido")
                    continue
                r = {"x": r["x"], "y": r["y"], "w": r["width"], "h": r["height"]}
            k = self.marge
            x0, y0 = max(r["x"] - k, 0), max(r["y"] - k, 0)
            x1, y1 = min(r["x"] + r["w"] + k, vp["width"]), min(r["y"] + r["h"] + k, vp["height"])
            if x1 <= x0 or y1 <= y0:
                print(f"AVISO {nombre}: « {m} » está fuera de la pantalla; recuadro omitido (usa haut=)")
                continue
            if (x0, y0, x1, y1) != (r["x"] - k, r["y"] - k, r["x"] + r["w"] + k, r["y"] + r["h"] + k):
                print(f"AVISO {nombre}: « {m} » no cabe entero en pantalla; recuadro recortado a lo visible")
            b.append([round(x0 / vp["width"] * 100, 2), round(y0 / vp["height"] * 100, 2),
                      round((x1 - x0) / vp["width"] * 100, 2), round((y1 - y0) / vp["height"] * 100, 2)])
        destino = self.salida / f"{nombre}.png"
        pg.screenshot(path=str(destino))
        self.boites[nombre] = {"b": b, "w": vp["width"], "h": vp["height"]}
        self.boites_path.write_text(json.dumps(self.boites, ensure_ascii=False, indent=1), encoding="utf-8")
        fuera = [x for x in b if x[0] < 0 or x[1] < 0 or x[0] + x[2] > 100 or x[1] + x[3] > 100]
        print(f"{nombre}.png · {len(b)} recuadro(s)" + (f" · AVISO fuera de pantalla: {fuera}" if fuera else ""))
        return destino

    @contextlib.contextmanager
    def video(self, nombre, url=None):
        """Graba un vídeo corto (10-25 s) de lo que se haga dentro del bloque. Guarda <nombre>.webm y
        <nombre>_poster.png en <salida>/videos/. Conserva la sesión; vuelve al contexto normal al acabar."""
        vdir = self.salida / "videos"
        vdir.mkdir(exist_ok=True)
        tmp = vdir / "_tmp"
        actual = self.page.url
        try:
            pg = self.nueva_pagina(self.dispositivo, video_dir=tmp)
        except Exception as e:
            if "ffmpeg" in str(e):
                raise SystemExit("Para grabar vídeo falta el ffmpeg de Playwright: `python -m playwright install ffmpeg`.")
            raise
        pg.goto(url and self.url(url) or actual, wait_until="networkidle")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(vdir / f"{nombre}_poster.png"))
        t0 = time.time()
        try:
            yield pg
        finally:
            v = pg.video
            pg.wait_for_timeout(600)
            self.ctx.close()
            self.ctx = None
            shutil.move(v.path(), vdir / f"{nombre}.webm")
            shutil.rmtree(tmp, ignore_errors=True)
            dur = time.time() - t0
            print(f"vídeo {nombre}.webm · {dur:.0f} s" + (" · AVISO: fuera de 10-25 s" if not 10 <= dur <= 25 else ""))
            self.nueva_pagina(self.dispositivo)
            self.page.goto(actual, wait_until="domcontentloaded")

    def fin(self):
        if self.ctx:
            self.ctx.close()
        self.browser.close()
        self._pw.stop()


# ---------- guion JSON ----------
def _paso(cap, p, base_guion):
    pg = cap.page
    if "ir" in p:
        pg.goto(cap.url(p["ir"]), wait_until="networkidle")
    elif "clic" in p:
        pg.locator(p["clic"]).first.click()
    elif "rellenar" in p:
        pg.locator(p["rellenar"][0]).first.fill(p["rellenar"][1])
    elif "elegir" in p:
        pg.locator(p["elegir"][0]).first.select_option(p["elegir"][1])
    elif "subir" in p:
        f = Path(p["subir"][1])
        pg.locator(p["subir"][0]).first.set_input_files(str(f if f.is_absolute() else base_guion / f))
    elif "pasar" in p:
        pg.locator(p["pasar"]).first.hover()
        pg.wait_for_timeout(300)
    elif "arrastrar" in p:
        pg.locator(p["arrastrar"][0]).first.drag_to(pg.locator(p["arrastrar"][1]).first)
        pg.wait_for_timeout(300)
    elif "tecla" in p:
        pg.keyboard.press(p["tecla"])
    elif "esperar" in p:
        pg.wait_for_selector(p["esperar"], timeout=p.get("timeout", 90000))
    elif "pausa" in p:
        pg.wait_for_timeout(p["pausa"])
    elif "captura" in p:
        cap.shot(p["captura"], *p.get("marcas", []), haut=p.get("haut"), toasts=p.get("toasts", False))
    else:
        raise SystemExit(f"paso desconocido: {p}")


def explorar(base_url, rutas_txt, salida, cuenta=None, login=None, dispositivo="pc"):
    """Captura de página completa de cada ruta de rutas.txt (una por línea) para elegir pantallas.
    Señala los 4xx/5xx de la página y de sus recursos (CSS/JS rotos = pantalla que no se debe enseñar)."""
    rutas = [l.strip() for l in Path(rutas_txt).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    cap = Capturador(base_url, salida, dispositivo)
    if cuenta:
        lg = dict(LOGIN, **(login or {}))
        cap.connecter(cuenta.get("usuario", ""), cuenta.get("clave", ""), lg["url"], lg["usuario"], lg["clave"], lg["entrar"],
                      lg.get("esperar"), cuenta.get("clics", []) + lg.get("clics", []))
    malos = []
    cap.page.on("response", lambda r: malos.append(f"{r.status} {r.url}") if r.status >= 400 and not r.url.endswith("favicon.ico") else None)
    for ruta in rutas:
        malos.clear()
        cap.page.goto(cap.url(ruta), wait_until="networkidle")
        nombre = "explora_" + (ruta.strip("/").replace("/", "_") or "inicio")
        cap.page.screenshot(path=str(Path(salida) / f"{nombre}.png"), full_page=True)
        print(f"{'ROTA' if malos else 'ok  '} {ruta} -> {nombre}.png" + (f"  {malos[:3]}" if malos else ""))
    cap.fin()


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--explorar":
        # python capturas_base.py --explorar guion.json rutas.txt  (usa base_url, login y la 1.ª cuenta del guion)
        guion = Path(sys.argv[2]).resolve()
        g = json.loads(guion.read_text(encoding="utf-8"))
        cuenta = next(iter(g.get("cuentas", {}).values()), None)
        explorar(g["base_url"], sys.argv[3], guion.parent / "explora", cuenta, g.get("login"), g.get("dispositivo", "pc"))
        return
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ruta = Path(sys.argv[1]).resolve()
    g = json.loads(ruta.read_text(encoding="utf-8"))
    salida = Path(g.get("salida", "capturas"))
    cap = Capturador(g["base_url"], salida if salida.is_absolute() else ruta.parent / salida, g.get("dispositivo", "pc"), g.get("ocultar"))
    login = dict(LOGIN, **g.get("login", {}))
    try:
        sesion = None
        for r in g["recorridos"]:
            if r.get("dispositivo", cap.dispositivo) != cap.dispositivo:
                cap.nueva_pagina(r["dispositivo"])
            if r.get("cuenta") and r["cuenta"] != sesion:
                c = g["cuentas"][r["cuenta"]]
                cap.nueva_pagina(cap.dispositivo, limpia=True)
                cap.connecter(c.get("usuario", ""), c.get("clave", ""), login["url"], login["usuario"], login["clave"], login["entrar"],
                              login.get("esperar"), c.get("clics", []) + login.get("clics", []))
                sesion = r["cuenta"]
            if r.get("video"):
                with cap.video(r["video"], r.get("ir")):
                    for p in r["pasos"]:
                        _paso(cap, p, ruta.parent)
            else:
                for p in r["pasos"]:
                    _paso(cap, p, ruta.parent)
    finally:
        cap.fin()
    print(f"Listo: {salida} (revisa con planche.py)")


if __name__ == "__main__":
    main()
