---
name: preparar-reunion
description: "Prepara una reunión con el cliente o una demo montando una guía visual (artifact de claude.ai) en castellano y francés, con capturas reales de producción y los clics marcados con recuadros rojos numerados. Dos formatos. « Novedades desde la última reunión »: fichas por zona, índice en burbujas, filtros por origen y vídeos. « Guía de pruebas »: cuentas, kit de ficheros y recorridos paso a paso. Úsala cuando digan « prepara la reunión », « prepara la reunión del jueves con <cliente> », « prepara la demo », « qué hemos hecho desde la última reunión », « resumen de novedades para el cliente », « el artifact de novedades », « hazme la guía para enseñar esto al cliente », « guía para que mi jefe / el cliente pruebe … », « cómo probar … » o « guía de test ». No la uses para un PDF de entrega, una factura o un informe de horas, ni para documentación técnica o de API."
---

# Preparar una reunión

Resultado: un artifact publicado que se entiende sin explicaciones. Cada mejora o cada prueba lleva capturas reales y el sitio exacto marcado. Si lo piden, también va la misma página en francés dentro de la aplicación.

Habla con el usuario en **castellano**. La guía sale en **castellano y francés**, con selector ES/FR.

**Ruta de la skill:** `${CLAUDE_SKILL_DIR}`. En las referencias, `<skill>` significa esa ruta. Ejecuta los scripts con su ruta completa, porque trabajas en la carpeta del proyecto del cliente:
`python "<skill>/scripts/construir_guia.py" …`
Si ves `${CLAUDE_SKILL_DIR}` sin resolver (has leído este archivo a mano en vez de cargar la skill), `<skill>` es la carpeta que contiene este SKILL.md.

**Hazlo, no preguntes de más.** La única validación obligatoria es la lista de fichas (paso 2). Zonas, orden, qué capturar y qué lleva vídeo lo decides tú. Calidad alta: tiene que parecer un documento cuidado, no una página de pruebas.

## 1. Decide el formato
- « prepara la reunión », « novedades », « qué hemos hecho » → **Novedades** (references/diseno.md §A). Es el formato por defecto.
- « que X pruebe », « cómo probar », « guía de test » → **Guía de pruebas** (references/diseno.md §B).
- Si en la reunión se va a enseñar o probar algo concreto, **propón** además una guía de pruebas de esos recorridos. Propónla, no la hagas sin preguntar.
- Antes de nada, mira el proyecto. Necesitas:
  - la URL de producción;
  - si hay datos de prueba que se puedan cargar y borrar;
  - las cuentas por nivel;
  - el logo del cliente (`static/`, la carta gráfica, o un artifact anterior suyo leído con `Artifact read`).
- **Explora la aplicación** antes de elegir pantallas: `python "<skill>/scripts/capturas_base.py" --explorar guion.json rutas.txt` hace una captura de página completa de cada ruta y marca « ROTA » la que tenga un CSS, JS o página en error.
- **Si producción está rota** (pantalla sin estilos, error 500, recurso que falta), **no la captures**: para, dile al usuario qué falla y qué fichas afecta. Sigue solo con el resto si te lo confirma. Una captura de una pantalla rota en una guía para el cliente es peor que no tener la ficha.

## 2. Reúne el contenido y valídalo con el usuario
- **Novedades:** sigue references/fuentes.md, en este orden:
  1. la última reunión (Koralya);
  2. las notas de reuniones;
  3. `HISTORIAL.md` y `git log`;
  4. los tickets cerrados.

  Mete solo lo que el cliente **ve o usa** y **nunca importes de dinero de Koralya**.
- **Guía de pruebas:** reúne los recorridos pedidos, una cuenta por nivel, los datos de prueba (identificables y que se puedan borrar) y el kit de ficheros. Si la aplicación no tiene datos de prueba que se puedan borrar, propónlo antes de capturar nada. Excepción: una **demo sin persistencia** (nada se guarda, cada recarga vuelve al inicio). Ahí no hace falta proponer nada; adapta « Todo está preparado » y « Al terminar » (references/diseno.md § Pruebas).
- Enseña la lista y **espera su visto bueno**:
  - Novedades: zona → título, una línea de « qué cambia », origen y fecha.
  - Pruebas: sección → recorrido, con cuenta y dispositivo.

## 3. Captura en producción
Sigue references/capturas.md:
- **Una captura por paso**, con un recuadro por cada cosa que se pulsa o se mira.
- Usa `scripts/capturas_base.py`: Chromium en francés, sin toasts.
- Viewports: 1440×900, 1180×820 y 390×844.
- Vídeo de 10 a 25 s solo para lo que se entiende mejor en movimiento.
- **Nunca captures cambiando datos reales.** Al acabar, deja los datos de prueba como estaban.
- Genera la hoja de control (`scripts/planche.py`) y **mírala con Read**. Rehaz lo que falle antes de seguir.

## 4. Construye
- Escribe el contenido en un JSON `{… "es": …, "fr": …}` con los mismos id en los dos idiomas. El formato está en references/diseno.md § Formato y hay un ejemplo en assets/ejemplos/.
- Ejecuta:
  `python "<skill>/scripts/construir_guia.py" --guia guia.json --capturas capturas --videos capturas/videos --salida site`
  El script se niega a construir si ES y FR no coinciden. Corrige cada ERROR y lee los AVISO, que señalan textos largos y recuadros fuera de pantalla.
- Respeta las reglas de references/diseno.md §Reglas:
  - imagen ampliada dentro de la página, nunca en otra pestaña;
  - flechas solo dentro de la misma ficha;
  - columna izquierda limpia;
  - descarga en cada prueba;
  - poco texto;
  - traducción completa.

## 5. Comprueba
- `python "<skill>/scripts/probar_local.py" site --capturas control` debe acabar en `RESULTADO: OK`. Comprueba a 1440 y 390 px:
  - sin errores de consola;
  - sin desplazamiento horizontal;
  - ampliación y flechas;
  - cambio ES/FR.
- Mira tú las capturas de control.
- **Guía de pruebas:** cada enlace de descarga debe responder 200 con la sesión de **cada** cuenta que lo usa (pruébalo en producción con Playwright o `requests`).

## 6. Publica y entrega
- **La plantilla manda.** Es un documento claro, como un PDF, con un solo tema; no la adaptes al contrato de `artifact-design` (modo oscuro, tokens…) ni cambies su CSS. Si la herramienta Artifact exige cargar `artifact-design` antes de publicar, cárgala, pero publica `site/index.html` tal cual.
- Publica `site/index.html` con `files` (todas las `p/*.webp` y `m/*`) e `icon`: `checklist` para pruebas, `sparkles` para novedades.
- Para actualizar la guía después, vuelve a publicar **el mismo `file_path`**: el enlace no cambia.
- Entrega en pocas líneas:
  - el enlace y qué contiene;
  - qué has comprobado;
  - qué tiene que hacer el usuario: compartirlo desde « Compartir » y, en una guía de pruebas, borrar los datos de prueba al terminar.
- Si la guía lleva contraseñas y el artifact queda compartido con « cualquiera que tenga el enlace », avísalo en una línea.

## 7. Dentro de la aplicación (solo si lo piden)
Sigue references/integrar-en-app.md:
- Copia en francés idéntica al artifact (`--solo-idioma fr` + `scripts/integrar_en_app.py`).
- Servida por una vista que exige sesión, con las imágenes en `static/`.
- Entrada en el menú, y acceso a la guía y al kit para todos los niveles que la usan.
- Al final: despliega, prueba con cada cuenta, haz commit y apúntalo en el HISTORIAL.
