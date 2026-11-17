# La guía dentro de la aplicación

Hazlo solo si el usuario lo pide. Así se hizo en el primer proyecto que lo tuvo.

## Contenido
- Una página autónoma **solo en francés**, idéntica al artifact (cuentas incluidas si están en el artifact).
- Sin selector de idioma y con un enlace « ← Application » arriba.
- Se construye con el mismo JSON:
  ```
  python "<skill>/scripts/construir_guia.py" --guia guia.json --capturas capturas --videos capturas/videos --salida site_fr --solo-idioma fr
  ```

## Servicio
```
python "<skill>/scripts/integrar_en_app.py" --site site_fr --app <ruta de la app Django> --slug guia-pruebas --volver /
```
Hace tres cosas:
- Copia `p/` y `m/` a `<app>/static/<slug>/`.
- Escribe `<app>/guias/<slug>.html` con las rutas `p/…` y `m/…` prefijadas por `__ASSETS__`.
- Escribe `<app>/guias/<slug>_vista.py.txt` con la vista, la URL y la nota del menú.

La vista sirve el HTML **tal cual**: no es una plantilla Django, porque las llaves del JS romperían el motor de plantillas. Exige sesión (`@login_required`) y sustituye `__ASSETS__` por `static("<slug>/")`.

Tú añades a mano, siguiendo el estilo del proyecto:
- la vista en el módulo de vistas;
- la ruta en `urls.py`.

## Acceso
- **Una entrada en el menú** (« Guide de test » / « Nouveautés »), visible para **todos** los niveles que usan la guía.
- **El kit para los mismos niveles.** En el primer proyecto, la cuenta de almacén no podía bajar el kit hasta que se abrió a todos los niveles. Comprueba cada descarga con la sesión de cada cuenta: tiene que responder 200.

## Cierre
1. Despliega como despliegue el proyecto (`collectstatic` si aplica).
2. Entra con **cada cuenta** y comprueba que:
   - la entrada del menú aparece;
   - la guía carga con imágenes;
   - la ampliación funciona;
   - las descargas responden.
3. Haz commit y apúntalo en el HISTORIAL del proyecto.
