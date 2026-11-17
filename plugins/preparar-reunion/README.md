# preparar-reunion

Skill de Claude Code que monta la guía visual de una reunión con el cliente: un artifact de claude.ai en castellano y francés, con capturas reales de producción y el sitio exacto marcado con recuadros rojos numerados.

Hace dos tipos de guía:

| Tipo | Cuándo | Qué lleva |
|---|---|---|
| **Novedades** | « prepara la reunión », « qué hemos hecho desde la última reunión » | Cifras, índice en burbujas por zona, buscador, filtros por origen y fichas con « qué cambia », pasos, « Lo que se pidió », enlace a producción, capturas y vídeos. |
| **Guía de pruebas** | « guía para que mi jefe / el cliente pruebe X », « cómo probar » | Cuentas de prueba, kit de ficheros, una ficha por recorrido con cuenta y dispositivo, pasos numerados, capturas y descargas. |

La única pregunta obligatoria es el visto bueno a la lista de fichas antes de capturar.

## Instalar
```
/plugin marketplace add adrianrodriguez-alt/koralya-plugins
/plugin install preparar-reunion@koralya
```
Abre una conversación nueva en el proyecto del cliente y di, por ejemplo:
- « prepara la reunión con <cliente> desde el 21/10 »;
- « guía para que mi jefe pruebe el ARC ».

También puedes llamarla directamente con `/preparar-reunion:preparar-reunion`.

## Requisitos
- Conector **Koralya** (reuniones, transcripciones y tickets).
- Python 3.11+ con `pip install playwright pillow`, y Google Chrome o `python -m playwright install chromium`.
- Para los vídeos: `python -m playwright install ffmpeg`.
- Acceso a producción con las cuentas de prueba.

## Contenido
| Ruta | Qué es |
|---|---|
| `skills/preparar-reunion/SKILL.md` | El proceso: formato → contenido (validado) → capturas → construir → comprobar → publicar → app. |
| `references/diseno.md` | Anatomía de los dos tipos, reglas de diseño ya corregidas y formato del JSON. |
| `references/capturas.md` | Playwright en producción: datos de prueba, viewports, francés, toasts, vídeos y hoja de control. |
| `references/fuentes.md` | De dónde sale « qué se ha hecho »: reunión, notas, HISTORIAL/git, tickets. Qué se filtra. |
| `references/integrar-en-app.md` | La copia en francés dentro de la aplicación Django. |
| `assets/` | Plantillas (`novedades/`, `guia_pruebas/`), estilos comunes y ejemplos JSON neutros. |
| `scripts/` | `capturas_base.py`, `planche.py`, `a_webp.py`, `construir_guia.py`, `probar_local.py`, `integrar_en_app.py`. |
