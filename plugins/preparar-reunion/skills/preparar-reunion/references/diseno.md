# Diseño de las guías

Las dos plantillas (`assets/novedades/gabarit.html` y `assets/guia_pruebas/gabarit.html`) comparten `assets/comun/estilos.css`. Reproducen las dos guías de referencia que ya se entregaron a un cliente (novedades de un configurador y guía de pruebas de una plataforma de gestión). **No cambies la anatomía ni el CSS**: lo que cambia es el JSON de contenido. El color principal del cliente va en `"color"` (sustituye a `--bleu`).

## Índice
- §A Novedades: anatomía
- §B Guía de pruebas: anatomía
- §Reglas (corregidas por Adrián, no las repitas)
- §Formato del JSON (novedades / pruebas)

## §A · Novedades desde la última reunión
1. **Portada.** Contiene:
   - logo del cliente;
   - sobretítulo azul (« Configurador Acme · Koralya Tech »);
   - título (« Novedades desde la reunión del 21/10/2026 »);
   - a la derecha, para quién es y el periodo con el autor;
   - selector ES | FR.
2. **Accesos para probar** (opcional): una tarjeta por aplicación, con una fila por cuenta (nivel en pastilla de color, usuario y contraseña que se copian al pulsar, qué ve).
3. **Cifras**, cuatro y calculadas solas:
   - mejoras;
   - peticiones de la reunión hechas: orígenes con `"reunion": true` y mejoras con `"reunion": true`;
   - tickets resueltos: orígenes con `"ticket": true`. Si no hay tickets, usa esta cifra para otra fuente (por ejemplo el documento de quejas del cliente: origen con `"ticket": true`) y cambia su texto en `textos.es.c` / `textos.fr.c` (lista de 4 textos, el 3.º es este);
   - capturas + vídeos.
4. **Intro** con la leyenda roja « ① dónde mirar o pulsar ».
5. **Índice en burbujas**: una fila por zona, una burbuja por mejora, del color de su origen, con su código o número y ▶ si tiene vídeo. Al pasar el ratón se ve la frase `h`; al pulsar, va a la ficha. Con `"indice": false` se quita.
6. **Buscador + filtros por origen** + « N de M mejoras ».
7. **Bandas oscuras por zona** (« 1. Vista 3D » + subtítulo), en el orden en que se usa la aplicación, no por fecha.
8. **Fichas.** La cabecera lleva número, título, pastilla de origen con su código (« Ana · A1 », « Tickets · ACM-046 ») y fecha.
   - **Izquierda:** « qué cambia » (sin caja ni etiqueta), « Dónde pulsar » (1-4 pasos numerados, el actual en rojo), « Lo que se pidió » (frase textual de la reunión, si la hay) y « Abrir en la aplicación ↗ ».
   - **Derecha:** captura con recuadros, botones 1·2·3 y « ▶ Vídeo ».
9. **Pie**: « capturas y vídeos hechos en producción el … · los enlaces piden iniciar sesión ».

## §B · Guía de pruebas
1. **Portada**: logo, sobretítulo, « Cómo probar … », a la derecha qué cubre y la fecha, y el selector ES | FR.
2. **Cuentas de prueba**, solo si se piden y en lo más alto: una fila por cuenta, con nivel en pastilla, usuario y contraseña que se copian al pulsar, y qué ve.
3. **« Todo está preparado »**: dice que los datos de prueba están cargados, que cada paso indica su cuenta y que los enlaces del kit necesitan la sesión abierta. Debajo, una pastilla por fichero del kit (zip completo incluido).
4. **Bandas oscuras de sección**: « Antes de empezar », « 1. … », « 2. … », cada una con un subtítulo de una línea (cuenta y dispositivo).
5. **Fichas**, una por recorrido.
   - **Cabecera**: número en cuadrado azul, título, « Cuenta Oficina » y « Ordenador / Tablet / Móvil ».
   - **Izquierda**: un párrafo de qué hace la funcionalidad, « Ficheros para la prueba » (↓ descarga) y « Pasos » numerados. El paso actual sale en rojo y en negrita; al pulsar un paso cambia la captura.
   - **Derecha**: captura con recuadros rojos y, sobre el primero, la etiqueta « ① texto corto del paso ». Debajo, botones 1 · 2 · 3.
6. **Imagen ampliada dentro de la página**:
   - Muestra el título de la ficha, « Paso 2/4 », la explicación y las flechas ‹ ›.
   - Funciona con el teclado y deslizando en el móvil.
   - Se cierra con ×, con Escape o pulsando fuera.
7. **« Al terminar »**: cómo dejarlo todo como estaba (« Effacer » los datos de prueba).
8. **Pie**: « Capturas de producción, hechas el … con estos mismos datos de prueba ».

## §Reglas (ya corregidas por Adrián: no repitas estos fallos)
- **Nunca abras una imagen en otra pestaña**: claude.ai la bloquea (`ERR_BLOCKED_BY_RESPONSE`). La ampliación va dentro de la página; ya lo hace la plantilla, no lo cambies.
- **Las flechas de la ampliación se quedan en la misma ficha.**
  - En el último paso, la flecha › está desactivada.
  - Con una sola captura no hay flechas.
- **Ancho sin hacerla altísima**:
  - hoja de 1 440 px como máximo;
  - columnas `4fr / 8fr`, con el texto a 280 px como mínimo;
  - captura de 860 px como máximo.
- **Columna izquierda limpia**:
  - nada de cajas rosas ni etiquetas « Lo nuevo »;
  - las URL largas se sustituyen por « Abrir en … ↗ ».
- **Enlace de descarga en cada prueba**, justo encima de los pasos (« ↓ ARC_9900001.pdf »), además del zip completo arriba.
- **La URL de la plataforma y los enlaces** son los de producción, nunca `127.0.0.1` ni la de pruebas: quien lee la guía no está en tu máquina.
- **Cuentas arriba del todo**, si se piden. Si el artifact se comparte « con cualquiera que tenga el enlace », avisa en una línea.
- **Traducción completa ES/FR**: títulos, pasos, pastillas, etiquetas de la ampliación (« Étape 2/4 ») y el bloque final.
  - Los nombres de botones de la aplicación se dejan como salen en pantalla, entre « ».
  - Comillas francesas « » con espacio: la plantilla pone el espacio fino sola.
- **Móvil a 390 px** sin desplazamiento horizontal. Usuario y contraseña van uno debajo del otro, sin recortar.
- **Poco texto**:
  - un párrafo por ficha (1-2 frases en novedades);
  - pasos de una línea;
  - sin jerga técnica: el lector es el cliente o un jefe, no un desarrollador.
- **Qué no va nunca**:
  - importes de dinero de Koralya (facturación, horas cobradas);
  - notas internas de tickets;
  - refactors, tests o servidores, salvo que el cliente los pidiera.

## §Formato del JSON

### Común a los dos tipos
```json
{
  "tipo": "novedades | pruebas",
  "cliente": {"nombre": "Acme", "logo": "logo.svg | logo_datauri.txt | data:image/svg+xml;base64,…"},
  "color": "#0052b7",
  "textos": {"es": {…}, "fr": {…}}
}
```
- En `textos`, las claves tienen que coincidir en ES y FR.
- Los textos de interfaz (« Paso », « Copiado », « Ficheros para la prueba »…) ya vienen en la plantilla y se pueden sobrescribir.
- El logo tiene que ser el del cliente: búscalo en `static/` del proyecto, en su carta gráfica o en un artifact anterior suyo.

### Novedades · ejemplo completo en `assets/ejemplos/novedades.json`
```json
"textos": {"es": {"sur": "…", "titre": "Novedades desde la reunión del 21/10/2026", "pour": "Para Acme", "par": "Del 21/10 al 11/11/2026 · Adrián",
                  "abrir": "Abrir en el configurador", "pied": "…", "c": ["mejoras…", "peticiones…", "tickets resueltos", "capturas…"]}, "fr": {…}},
"indice": true,
"accesos": [{"nombre": {"es": "Configurador", "fr": "Configurateur"}, "url": "https://…",
             "filas": [{"nivel": {"es": "Oficina", "fr": "Bureau"}, "c": "#0052b7", "u": "usuario", "m": "contraseña", "ve": {"es": "…", "fr": "…"}}]}],
"zonas": [{"id": "3d", "es": ["Vista 3D", "recorrido del vendedor"], "fr": ["Vue 3D", "parcours vendeur"]}],
"origenes": [{"id": "ana", "color": "#0052b7", "es": "Ana", "fr": "Ana", "reunion": true},
             {"id": "ticket", "color": "#b45309", "es": "Tickets", "fr": "Tickets", "ticket": true}],
"items": [{"id": "cotes", "z": "3d", "o": "ana", "code": "A1", "d": "23/10", "t": "g", "reunion": false,
           "url": "https://…/etape/…", "capturas": ["cotes_1", "cotes_2"], "video": "piece",
           "es": {"n": "Cotas de cada pieza", "h": "frase de la burbuja", "q": "qué cambia (1-2 frases)",
                  "s": ["paso de la captura 1", "paso de la captura 2"], "c": "« frase textual de la reunión »"},
           "fr": {…mismos campos y mismo número de pasos…}}]
```
- `t`: `g` = burbuja grande (lo importante), `p` = pequeña, sin `t` = normal.
- `s[k]` es el texto del paso de `capturas[k]`. Los pasos sobrantes se ven pero no cambian la captura.
- Por defecto el origen va por persona del cliente que lo pidió (« Ana », « Marc »). También puede ir por fuente: « Tickets », « Fallos de la demo », « Koralya » (lo que propusimos nosotros).
- `code`: el número de la petición en las notas de la reunión (A1, M2…) o el código del ticket (ACM-046).
- `video`: el nombre sin extensión en `capturas/videos/` (`<nombre>.webm`/`.mp4` + `<nombre>_poster.png`).

### Pruebas · un recorrido por ficha
```json
"plataforma": {"url": "https://app.cliente.koralya.com", "nombre": {"es": "Plataforma de gestión", "fr": "Plateforme de gestion"}},
"kit_url": "https://app.cliente.koralya.com/donnees-demo/kit/",
"cuentas": [{"n": "bureau", "c": "#0052b7", "u": "bureau.demo@…", "m": "…",
             "nivel": {"es": "Oficina", "fr": "Bureau"}, "ve": {"es": "qué ve", "fr": "ce qu'il voit"}}],
"textos": {"es": {"sur": "Plataforma de gestión", "titre": "Cómo probar la plataforma", "quoi": "ARC, llegada del vehículo y Magasin",
                  "date": "Con los datos de prueba · 13/11/2026", "prep": "<b>Todo está preparado</b>: …",
                  "finT": "Al terminar", "fin": "Con la cuenta Administrador, « Données de démo » → « Effacer »…",
                  "pied": "Capturas de producción, hechas el 13/11/2026 con estos mismos datos de prueba."}, "fr": {…}},
"contenido": {
  "es": {"kit": [["kit-demo.zip", "Todo el kit (.zip)"], ["ARC_9900001.pdf", "ARC sin diferencias"]],
         "sections": [{"t": "1. ARC leído por la IA", "s": "cuenta Oficina · ordenador",
                       "fichas": [{"id": "arc-ok", "n": "Un ARC que coincide con el pedido", "cuenta": "bureau", "disp": "Ordenador",
                                   "q": "qué hace la funcionalidad (un párrafo)",
                                   "kit": [["ARC_9900001.pdf", "ARC_9900001.pdf"]],
                                   "p": [["« Commandes fournisseurs »: busca 9900001 y pulsa ARC.", "arc_1"], ["…", "arc_2"]]}]}]},
  "fr": {…mismas secciones, fichas, id, capturas y ficheros…}}
```
- `kit` acepta un nombre (que se pega a `kit_url`) o una URL completa. **Sin kit** (`"kit": []` y sin `kit_url`) no salen las pastillas, ni arriba ni en las fichas.
- `disp` es texto libre y **se traduce**: Ordenador / Ordinateur, Tablet / Tablette, Móvil / Téléphone. Debe coincidir con el viewport de las capturas de esa ficha.
- `nivel` de cada cuenta: **14 caracteres como máximo** (« Comercial », « Atelier »). Si hace falta precisar (« perfil Lamine »), va en `ve`.
- **Demo sin persistencia** (nada se guarda): sin `kit`; `prep` = « <b>Todo está preparado</b>: la demo trae datos ficticios y no guarda nada. Lo que cuenta es el perfil que eliges al entrar; la contraseña puede ser cualquiera. »; `fin` = « No hay nada que borrar: al recargar la página todo vuelve a como estaba. ». Y en `cuentas`, el perfil que hay que elegir.
- `cuenta` es el `n` de una cuenta. Sin `cuentas`, no salen las filas de cuentas ni la pastilla.
- Un paso cuya captura sea `""` se muestra en la lista pero no cambia la captura.
