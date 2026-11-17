# Capturas en producción

Todas las capturas son **de producción**, hechas con Playwright mediante `scripts/capturas_base.py`. Ninguna se inventa ni se retoca. El script guarda la imagen y los recuadros en % del viewport en `<salida>/boites.json`. `construir_guia.py` lee después ese fichero.

## Antes de capturar
- **Datos de prueba.** Tienen que **reconocerse y poder borrarse sin tocar los datos reales**.
  - Lo que funciona: rangos de números aparte (expedientes 2099…, pedidos 9900…), un cliente « CLIENT DÉMO » y los botones « Charger » / « Effacer » en una página « Données de démo ».
  - Si la aplicación no tiene algo así, **propónlo antes de empezar** y créalo con el usuario.
  - **Nunca captures modificando datos reales.** En novedades, captura sobre registros de demo o sobre pantallas de solo lectura.
- **Cuentas**: una por nivel (admin, oficina, almacén…), con contraseña fija y no provisional.
- **Kit de ficheros**: lo que el probador tiene que subir (PDF, fotos…). Debe ser ficticio, marcado « EXEMPLE », y descargable desde la propia aplicación.
- **Guion antes de capturar**: secciones → fichas → pasos, con cuenta y dispositivo. Cada paso es una captura.

## Con el script
Para recorridos lineales, usa un **guion JSON**. El formato completo está en el docstring de `capturas_base.py`.
```
python "<skill>/scripts/capturas_base.py" guion.json
```
Para recorridos con lógica (esperar a la IA, leer un número generado, ramas), usa un **script Python**:
```python
import sys; sys.path.insert(0, r"<skill>/scripts")
from capturas_base import Capturador
cap = Capturador("https://app.cliente.koralya.com", "capturas", dispositivo="pc")
pg = cap.connecter("bureau.demo@…", "…", url="/accounts/login/")
pg.goto(cap.url("/commandes/")); pg.fill("#q", "9900001")
cap.shot("arc_1", "tr:has-text('9900001') >> text=ARC", "#q")       # 1.er recuadro = lo que se pulsa
pg.click("tr:has-text('9900001') >> text=ARC")
pg.set_input_files("input[type=file]", "kit/ARC_9900001.pdf")
pg.wait_for_selector("#arc-resultat", timeout=90000)                    # IA real: espera un selector, no un tiempo
cap.shot("arc_3", "#arc-resultat", "#id_date_confirmee", haut="#arc-form")
cap.nueva_pagina("movil")                                               # misma sesión, otro dispositivo
with cap.video("regle_ia", url="/regles/ajouter/"):                    # 10-25 s
    ...
cap.fin()
```

## Reglas
- **Una captura por paso.** Pon un recuadro por cada cosa que se pulsa o se mira. El **primero** es el que lleva la etiqueta « ① texto del paso », así que debe ser lo que se pulsa.
- `shot()` solo desplaza la página hacia el primer recuadro. Si los campos de un paso no caben en pantalla, pasa `haut="<bloque>"` para alinear ese bloque arriba. Un recuadro fuera de la pantalla no se ve en la guía: `construir_guia.py` y `planche.py` lo marcan.
- **Viewports** (`dispositivo`):
  - `pc` 1440×900 (ordenador);
  - `tablet` 1180×820;
  - `movil` 390×844 con device_scale_factor 2.

  El dispositivo de la captura es el de la ficha. En pruebas, la pastilla « Tablet » tiene que llevar capturas de tablet.
- **Chromium en francés**: ya lo hace el script (`--lang=fr-FR`, `LANG=fr_FR.UTF-8`, `locale="fr-FR"`). Sin eso, las fechas salen en formato estadounidense.
- **Sin toasts.** El script oculta `#toasts`, `.toast`, `.messages`… Si la aplicación usa otro selector, pásalo con `ocultar=[…]` (o `"ocultar"` en el guion).
- **Acciones automáticas**: si al elegir un tipo ya se pasa al paso siguiente, no pulses además « Siguiente ».
- **IA real** (lectura de PDF, propuestas): tarda entre 3 y 60 s. Espera a un selector concreto, nunca un tiempo fijo.
- **Vídeos**, solo para lo que se entiende mejor en movimiento (3D, arrastrar, un asistente que escribe, un ajuste por lote):
  - duración de 10 a 25 s, sin pausas muertas;
  - `cap.video(nombre)` graba `.webm` y saca la portada `_poster.png`;
  - si hay ffmpeg, `construir_guia.py` lo pasa a `.mp4`;
  - si falta el ffmpeg de Playwright: `python -m playwright install ffmpeg`.
- **Al terminar**, vuelve a dejar los datos de prueba como estaban (recargarlos) para que quien pruebe empiece de cero. Comprueba que los datos reales siguen intactos.

## Revisión (obligatoria)
```
python "<skill>/scripts/planche.py" capturas          # → capturas/planche.png
```
**Mira `planche.png` con Read** y busca:
- recuadros mal colocados o en naranja « FUERA »;
- capturas « SIN RECUADROS »;
- toasts o ventanas que tapan algo;
- pasos que no corresponden a su captura;
- datos que no son de prueba.

Rehaz lo que falle y vuelve a generar la hoja. No construyas sin haberla visto.
