# Guía — Cuaderno de viaje Costa Rica 2026

## Cómo está montado

- `data.py` — todo el contenido editable: días, destinos, actividades, documentos, gastos y la contraseña.
- `generate.py` — genera las páginas HTML a partir de `data.py`. Ejecútalo cada vez que edites `data.py`:

  ```bash
  python generate.py
  ```

- `assets/` — CSS, tipografía y JS compartidos por todas las páginas (no hace falta tocarlos).
- `index.html`, `destinos/*.html`, `actividades/*.html`, `documentos.html`, `gastos.html` — páginas generadas. **No las edites a mano**, se sobrescriben cada vez que ejecutas `generate.py`.

## Añadir fotos y documentos (vouchers, entradas)

Cada actividad y cada destino tiene dos huecos en `data.py`: `photos_url` y `docs_url`. Mientras estén en `None`, la web muestra un botón discontinuo de "añadir". Para rellenarlos:

1. **Fotos** — crea un álbum de Google Photos por destino (y, si quieres, uno por actividad), compártelo, y copia el enlace del álbum.
2. **Documentos** — sube el voucher/entrada a una carpeta de Google Drive, compártela, y copia el enlace.
3. Pega el enlace en `data.py`, por ejemplo:

   ```python
   "photos_url": "https://photos.app.goo.gl/xxxxxxx",
   "docs_url": "https://drive.google.com/drive/folders/xxxxxxx",
   ```

4. Guarda y ejecuta `python generate.py` otra vez.

Puedes ir haciendo esto poco a poco durante el viaje, incluso desde el móvil editando `data.py` con cualquier editor de texto y, si tienes Python en el móvil, regenerando ahí — o más cómodamente desde el portátil por la noche en el hotel.

Los documentos generales del viaje (vuelos, hoteles, seguro, traslados) se editan igual, en la lista `DOC_CATEGORIES`.

## Cambiar la contraseña de gastos

Edita `GASTOS_PASSWORD` en `data.py` y regenera. Recuerda: es solo una "cortina" en el propio navegador (evita que alguien entre sin querer), no seguridad real — cualquiera que mire el código fuente de `gastos.html` puede ver el hash. Suficiente para uso familiar, no para datos sensibles de verdad.

## Publicar en GitHub Pages (para abrir la web desde el móvil)

El repositorio de git ya está inicializado en esta carpeta con un primer commit. Te falta el lado de GitHub, que solo puedes hacer tú (necesita tu cuenta):

1. Entra en [github.com](https://github.com) (crea una cuenta gratis si no tienes) y pulsa **New repository**. Nómbralo, por ejemplo, `costa-rica-2026`. Puede ser público — no hay nada realmente sensible (los gastos están detrás de la cortina, y aun así son solo números de tu propio viaje).
2. GitHub te dará una URL tipo `https://github.com/tu-usuario/costa-rica-2026.git`. Copiala.
3. En una terminal, dentro de esta carpeta:

   ```bash
   git remote add origin https://github.com/tu-usuario/costa-rica-2026.git
   git branch -M main
   git push -u origin main
   ```

4. En GitHub, ve a **Settings → Pages**, y en "Build and deployment" elige **Deploy from a branch**, rama `main`, carpeta `/ (root)`. Guarda.
5. Al cabo de un minuto tu web estará en `https://tu-usuario.github.io/costa-rica-2026/`. Esa es la URL que abrís desde los móviles.

Dime tu usuario de GitHub y el nombre del repo cuando lo hayas creado, y te ayudo a revisar que el push y el Pages han quedado bien.

## Añadir o cambiar actividades/días más adelante

Todo el itinerario vive en las listas `DESTINATIONS`, `ACTIVITIES` y `DAYS` de `data.py`, con comentarios explicando cada campo. Copia un bloque existente como plantilla, cambia los datos, y regenera.
