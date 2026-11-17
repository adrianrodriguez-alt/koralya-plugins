"""Prepara la copia en francés de una guía para servirla dentro de una aplicación Django.

1. Construye antes la versión solo en francés:
     python construir_guia.py --guia guia.json --capturas capturas --salida site_fr --solo-idioma fr
2. python integrar_en_app.py --site site_fr --app <ruta de la app Django> --slug guia-pruebas [--volver /]

Hace:
  - copia p/ y m/ a <app>/static/<slug>/ ;
  - escribe <app>/guias/<slug>.html con las rutas de imágenes y vídeos prefijadas por __ASSETS__
    y un enlace « ← Application » arriba (__RETOUR__) ;
  - escribe <app>/guias/<slug>_vista.py.txt con la vista (sesión obligatoria), la URL y el menú a añadir.
No toca urls.py ni las plantillas del proyecto: eso lo hace Claude a mano, siguiendo references/integrar-en-app.md.
"""
import argparse
import sys
import re
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows (cp1252)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--volver", default="/", help="URL del enlace « ← Application »")
    a = ap.parse_args()
    site, app = Path(a.site).resolve(), Path(a.app).resolve()
    slug = re.sub(r"[^a-z0-9_-]", "-", a.slug.lower())
    func = "guia_" + slug.replace("-", "_")

    html = (site / "index.html").read_text(encoding="utf-8")
    if '"solo_idioma":"fr"' not in html:
        print("AVISO: la guía no parece construida con --solo-idioma fr (seguirá teniendo el selector ES/FR).")
    # Rutas relativas p/ y m/ → __ASSETS__ (la vista lo sustituye por la URL de static)
    html = html.replace("p/${", "__ASSETS__p/${").replace("m/${", "__ASSETS__m/${").replace('"m/" +', '"__ASSETS__m/" +')
    html = html.replace('<div class="feuille">', '<div class="feuille">\n  <a class="retour" href="__RETOUR__" style="display:inline-block;margin:-14px 0 14px;font-size:13px;font-weight:600">← Application</a>', 1)

    dst_static = app / "static" / slug
    for sub in ("p", "m"):
        if (site / sub).exists():
            shutil.copytree(site / sub, dst_static / sub, dirs_exist_ok=True)
    guias = app / "guias"
    guias.mkdir(parents=True, exist_ok=True)
    (guias / f"{slug}.html").write_text(html, encoding="utf-8")

    vista = f'''# --- {app.name}/views.py (o el módulo de vistas que use el proyecto) ---
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.templatetags.static import static

GUIA_{func.upper()} = Path(__file__).resolve().parent / "guias" / "{slug}.html"


@login_required
def {func}(request):
    """Guía en francés, idéntica al artifact. HTML servido tal cual (no es una plantilla Django)."""
    html = GUIA_{func.upper()}.read_text(encoding="utf-8")
    return HttpResponse(html.replace("__ASSETS__", static("{slug}/")).replace("__RETOUR__", "{a.volver}"))


# --- urls.py ---
# path("guide/{slug}/", views.{func}, name="{func}"),

# --- menú ---
# Entrada « Guide » visible para TODOS los niveles que usan la guía, y acceso al kit de ficheros
# para esos mismos niveles (un error ya visto: la cuenta de almacén no podía bajar el kit).
'''
    (guias / f"{slug}_vista.py.txt").write_text(vista, encoding="utf-8")
    n = sum(1 for _ in dst_static.rglob("*") if _.is_file())
    print(f"HTML: {guias / (slug + '.html')}")
    print(f"Static: {dst_static} ({n} ficheros)")
    print(f"Vista, URL y menú a añadir: {guias / (slug + '_vista.py.txt')}")
    print("Después: collectstatic si aplica, desplegar, probar con cada cuenta, commit y HISTORIAL.")


if __name__ == "__main__":
    main()
