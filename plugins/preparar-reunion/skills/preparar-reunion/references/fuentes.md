# Fuentes de « qué se ha hecho » (novedades)

Reúnelo tú, en este orden, sin preguntar. Al final se presenta la lista al usuario.

Las herramientas del conector Koralya pueden estar diferidas: cárgalas con ToolSearch en una sola llamada, empezando por `who_am_i`.

## 1. La última reunión con el cliente
- Usa `get_recent_meetings(cliente)` y localiza la última reunión con el cliente (no las internas). Si el usuario da una fecha (« desde el 21/10 »), esa fecha manda.
- Lee `get_meeting_transcript(…)` de esa reunión. Sirve para dos cosas:
  - **Fecha de corte**: todo lo hecho después de la reunión.
  - **Frases textuales** de lo que pidió cada persona. Van en la ficha como « Lo que se pidió » (`c`), entre « », en el idioma en que se dijeron, cortas, con […] si se recortan. **Literales de verdad**: no corrijas palabras aunque la transcripción automática se equivoque (« celle-ci » por « Sellsy »). Si la frase no se entiende sin corregirla, elige otra o no pongas cita.
- Si la reunión dio lugar a un roadmap, `get_herahub_meeting` puede traer el reporte IA con la lista de peticiones.

## 2. Las notas de reuniones del proyecto
En el repositorio del proyecto:
- `contexto/reuniones/AAAA-MM-DD_peticiones.md`: lo pedido, numerado por persona (A1, A2… de Ana; M1… de Marc). Ese número va en `code`.
- `contexto/reuniones/AAAA-MM-DD_mejoras.md`: lo hecho desde entonces, si existe.

Cruza cada petición con lo hecho. Las pedidas y hechas son las mejoras con origen = la persona que las pidió.

### Si no hay notas de reunión
Es habitual en proyectos nuevos. Entonces:
- Las peticiones salen de la **transcripción** de la reunión y de los **documentos del cliente posteriores a ella** (un correo o un documento de quejas, como « Point et questions par Loïc »). Lee también las traducciones de `documentos/traducciones_es/` si existen.
- **Numera tú las peticiones** por persona o documento, en orden de aparición (A1, A2… de Ana; L1… del documento de Loïc) y apúntalo en el JSON. Ese número es el `code`.
- Un documento del cliente que no es ni reunión ni ticket es un **origen** más (« Loïc · 27/09 »), con `"reunion": true` si lo que pide cuenta como petición atendida.

## 3. Historial y git
- `contexto/HISTORIAL.md` (o el historial que tenga el proyecto) desde la fecha de corte.
- `git log --since=<AAAA-MM-DD> --pretty="%ad %s" --date=short` en cada repositorio del cliente (configurador, plataforma…).

De aquí salen las mejoras que no pidió nadie (origen « Koralya ») y los fallos de la demo corregidos (origen « Fallos de la demo »).

**Sin git ni historial**, no inventes fechas: usa la fecha del ticket o del documento que la pidió. Si no hay ninguna, deja `d` vacío y dilo en la lista que presentas al usuario.

## 4. Tickets cerrados desde la fecha
- `search_tickets(cliente, kind="client")`; quédate con los resueltos o cerrados después de la fecha de corte. `get_ticket(codigo)` da el detalle.
- Al cliente se le enseña **el código del ticket y qué cambió**.
- **Nunca** se le enseñan las notas internas (`es_interno=true`) ni lo que se habló dentro del equipo.
- Si un ticket tiene capturas, míralas: ayudan a saber qué pantalla capturar.

## Filtrar
Quédate solo con lo que el cliente **ve o usa**:
- **Sí:** pantallas nuevas, botones, cálculos, correcciones visibles, PDFs, emails que recibe.
- **No:** refactors, tests, servidores, dependencias, migraciones o rendimiento invisible, salvo que el cliente lo pidiera (entonces se cuenta por su efecto: « la página carga en 1 s en vez de 6 »).
- **Nunca importes de dinero de Koralya**: ni facturación, ni horas cobradas, ni presupuestos de Koralya. Los precios que maneja la aplicación del cliente sí pueden salir, porque son sus datos.
- Fusiona lo que el usuario vería como una sola cosa. Separa lo que se usa en sitios distintos.

## Agrupar y ordenar
- Agrupa por **zona de la aplicación**, en el orden en que se usa (recorrido del vendedor → récapitulatif → back-office…), **no por fecha**.
- Dentro de cada zona, primero lo pedido en la reunión y lo más visible (burbuja `g`); al final los detalles (burbuja `p`).

## Cada ficha lleva
- título corto (2-5 palabras);
- `h`: una frase para la burbuja;
- `q`: « qué cambia » en una o dos frases;
- `s`: « dónde pulsar » en 1 a 4 pasos, uno por captura;
- origen (quién lo pidió) y su código, más la fecha (« 23/10 » o « 23/10 · 11/11 » si hubo dos entregas);
- enlace a producción (la URL exacta de la pantalla);
- de 1 a 4 capturas marcadas;
- un vídeo corto (10-25 s), solo si se entiende mejor en movimiento.

## Presentar la lista (única validación obligatoria)
Antes de capturar nada, enseña al usuario:
```
Novedades Acme desde el 21/10 (34 mejoras · 13 de la reunión · 6 tickets)

1. Vista 3D
   - Cotas de cada pieza · Ana A1 · 23/10: cada equipo enseña sus medidas en el 3D
   - …
2. Récapitulatif y PDF
   - …
Fuera de la guía (internas): migración a Django 5.2, tests del cálculo de pesos.
```
Espera su visto bueno. Después decide tú qué capturar, qué lleva vídeo y en qué orden.
