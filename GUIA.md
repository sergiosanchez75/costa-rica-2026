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

Cada actividad y cada destino tiene `photos_url` (un álbum) y `docs` (una lista de documentos) en `data.py`. Mientras estén vacíos, la web muestra un hueco discontinuo de "añadir". Para rellenarlos:

1. **Fotos** — crea un álbum de Google Photos por destino (y, si quieres, uno por actividad), compártelo, y copia el enlace del álbum.
2. **Documentos** — sube el voucher/entrada a Google Drive, compártelo, y copia el enlace.
3. Pega el enlace en `data.py`, por ejemplo:

   ```python
   "photos_url": "https://photos.app.goo.gl/xxxxxxx",
   "docs": [
       {"label": "Voucher hotel", "url": "https://drive.google.com/file/d/xxxxxxx/view"},
   ],
   ```

4. Guarda y ejecuta `python generate.py` otra vez.

Puedes ir haciendo esto poco a poco durante el viaje, incluso desde el móvil editando `data.py` con cualquier editor de texto y, si tienes Python en el móvil, regenerando ahí — o más cómodamente desde el portátil por la noche en el hotel. También vale con pasarme el enlace y la etiqueta por chat, como hemos hecho hasta ahora.

Los documentos que no pertenecen a un destino o actividad concreta (vuelos, traslados, seguro...) se editan en `TRANSPORT_DOCS` y `MISC_DOCS`.

## Cambiar la contraseña de gastos

Edita `GASTOS_PASSWORD` en `data.py` y regenera. Recuerda: es solo una "cortina" en el propio navegador (evita que alguien entre sin querer), no seguridad real — cualquiera que mire el código fuente de `gastos.html` puede ver el hash. Suficiente para uso familiar, no para datos sensibles de verdad.

## Gastos del día a día (comidas, snacks, ubers...)

La página de Gastos lee y escribe en directo en una Google Sheet: tarjetas por categoría, un quesito y la lista completa se calculan solos, y desde la propia web (botón **+** abajo a la derecha) puedes añadir, editar o eliminar un gasto sin tocar la hoja a mano.

Como una Sheet normal no permite escribir desde fuera, hace falta una pequeña API delante: **Google Apps Script**, gratis y ligado a tu cuenta de Google. Es un paso de configuración único:

1. Crea una Google Sheet nueva para los gastos (puede estar vacía, la cabecera se crea sola).
2. En esa hoja: **Extensiones → Apps Script**.
3. Borra lo que haya en `Code.gs` y pega el contenido completo de [`apps-script/Code.gs`](apps-script/Code.gs) (está en este mismo proyecto).
4. **Implementar → Nueva implementación**, tipo **Aplicación web**:
   - Ejecutar como: **Yo**
   - Quién tiene acceso: **Cualquier usuario**
   - Pulsa **Implementar**.
5. Google te pedirá autorizar el acceso (es tu propia hoja — verás un aviso de "app no verificada", es normal para scripts personales; pulsa Avanzado → ir a la app).
6. Copia la URL que termina en `/exec` y pégala en `EXPENSES_API_URL` (arriba de la sección de gastos en `data.py`).
7. Ejecuta `python generate.py`, guarda y sube los cambios.

A partir de ahí, todo se hace desde la web: el botón **+** abre un formulario (fecha con calendario, tipo de gasto, descripción, lugar e importe — fecha, tipo e importe son obligatorios), y cada gasto de la lista tiene un lapicero para editarlo o borrarlo. Los cambios se guardan directamente en tu Google Sheet.

Notas:
- `Tipo de Gasto` solo puede ser uno de los valores de `EXPENSE_CATEGORIES` en `data.py` (Avión, Hoteles, Transportes, Actividades, Comidas, Snacks, Compras Varias, Seguro Viaje, eSim) — el desplegable del formulario ya los ofrece, no hace falta escribirlos a mano.
- Privacidad: la URL de Apps Script solo la conocéis quienes la tengan (no está indexada ni es adivinable), pero no está protegida por la contraseña de Gastos en sí misma — es el mismo nivel de privacidad que los enlaces de Drive que ya usas para documentos.

**Si vuelves a tocar el código del script más adelante**: en Apps Script, guardar el código NO actualiza la URL `/exec` que ya está en marcha — hace falta volver a desplegar. Lo más fiable es **Implementar → Nueva implementación** (te da una URL nueva, que hay que actualizar en `EXPENSES_API_URL`) en vez de editar la implementación existente, que a veces no aplica bien el código nuevo ni mantiene el "Cualquier usuario" en el acceso.

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
