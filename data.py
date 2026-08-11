# -*- coding: utf-8 -*-
"""
Datos del viaje a Costa Rica 2026.

Edita este archivo para cambiar textos, anadir enlaces de fotos/documentos,
o ajustar los gastos. Despues de editar, vuelve a ejecutar:

    python generate.py

para regenerar el sitio (index.html, destinos/, actividades/, documentos.html, gastos.html).

COMO RELLENAR LOS ENLACES DE FOTOS
------------------------------------------------
1. Crea un album de Google Photos compartido por destino (y, si quieres, uno por
   actividad).
2. Comparte el album y copia el enlace.
3. Pega ese enlace en "photos_url". Si lo dejas en None, la web muestra un hueco
   con borde discontinuo invitando a anadirlo despues.

COMO ANADIR DOCUMENTOS (vouchers, entradas, confirmaciones...)
------------------------------------------------
Cada destino (DESTINATIONS) y cada actividad (ACTIVITIES) tiene una lista
"docs". Puedes anadir tantos documentos como quieras, cada uno con una
etiqueta corta y su enlace (por ejemplo, subido a Google Drive y compartido):

    "docs": [
        {"label": "Confirmación de reserva", "url": "https://drive.google.com/..."},
        {"label": "Factura", "url": "https://drive.google.com/..."},
    ],

Si la lista esta vacia ([]), la web muestra un hueco discontinuo invitando a
anadir documentos.

La pagina de Documentos junta todo esto en 4 categorias:
  - Hoteles     -> se genera solo, a partir de "docs" en DESTINATIONS.
  - Excursiones -> se genera solo, a partir de "docs" en ACTIVITIES.
  - Transportes -> se edita a mano en TRANSPORT_DOCS (mas abajo).
  - Varios      -> se edita a mano en MISC_DOCS (mas abajo).
"""

TRIP_TITLE = "Costa Rica 2026"
TRIP_SUBTITLE = "Cuaderno de viaje en familia"
TRIP_DATES = "18 - 30 agosto 2026"

# Contrasena de la seccion de gastos (solo una cortina, no seguridad real:
# cualquiera que mire el codigo fuente puede verla). Cambiala aqui.
GASTOS_PASSWORD = "puravida2026"

DESTINATIONS = [
    {
        "id": "san-jose",
        "name": "San José",
        "subtitle": "Llegada y salida",
        "color": "ciudad",
        "critter": "toucan",
        "stays": [
            {"dates": "18 - 20 agosto", "hotel": "Holiday Inn Express San José"},
            {"dates": "29 - 30 agosto", "hotel": "Holiday Inn Express San José"},
        ],
        "intro": "La puerta de entrada y salida del viaje: una tarde para pasear por el centro antes de salir hacia la selva, y una última noche de piscina y descanso antes del vuelo de vuelta.",
        "photos_url": None,
        "docs": [
            {"label": "Confirmación recepción hotel", "url": "https://drive.google.com/file/d/1x2NgRnMRe9wQvxcNW7kp_LI7oLxRFFjX/view?usp=drive_link"},
            {"label": "Hotel 18-20 agosto", "url": "https://drive.google.com/file/d/1YFIrOZ9XNwknPJVBOn84haf7SLlnROF_/view?usp=drive_link"},
            {"label": "Hotel 29-30 agosto", "url": "https://drive.google.com/file/d/12w0EEeCaBu1aXeFs7zzg1QJHnbH1zDqn/view?usp=drive_link"},
        ],
    },
    {
        "id": "tortuguero",
        "name": "Tortuguero",
        "subtitle": "Canales, selva y tortugas",
        "color": "oceano",
        "critter": "turtle",
        "stays": [
            {"dates": "20 - 22 agosto", "hotel": "Laguna Lodge"},
        ],
        "intro": "Un pueblo al que solo se llega en barca, rodeado de canales. Monos, caimanes y, si hay suerte, tortugas desovando de noche en la playa.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher hotel Laguna Lodge", "url": "https://drive.google.com/file/d/1h_OaFFEqFQylDMm_TmAvr6FaqhAOGaFX/view?usp=drive_link"},
        ],
    },
    {
        "id": "la-fortuna",
        "name": "La Fortuna",
        "subtitle": "Volcán Arenal",
        "color": "guanacaste",
        "critter": "volcano",
        "stays": [
            {"dates": "22 - 25 agosto", "hotel": "Hotel Monte Real"},
        ],
        "intro": "Tres días a los pies del volcán Arenal: cascada, puentes colgantes sobre el bosque nuboso y aguas termales para descansar.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher hotel Monte Real", "url": "https://drive.google.com/file/d/1ZncVSqUYh9DVN9LPHGudUqfsc8jZ0vaG/view?usp=drive_link"},
        ],
    },
    {
        "id": "manuel-antonio",
        "name": "Manuel Antonio",
        "subtitle": "Parque nacional y playa",
        "color": "mango",
        "critter": "monkey",
        "stays": [
            {"dates": "25 - 29 agosto", "hotel": "Iglú Beach Lodge"},
        ],
        "intro": "Selva y playa a la vez: el parque nacional con sus monos y perezosos, atardeceres en Espadilla y una excursión a Uvita a ver ballenas.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher hotel Iglú Beach Lodge", "url": "https://drive.google.com/file/d/1wwMQCsitWTzIsVGdUrDtg0pHi0sF4_dZ/view?usp=drive_link"},
        ],
    },
]

ACTIVITIES = [
    # --- San Jose ---
    {
        "id": "visita-san-jose",
        "destination_id": "san-jose",
        "day_label": "Mié 19 agosto",
        "time": "11:00",
        "title": "Visita a San José",
        "description": "Paseo por el centro: plaza principal, Teatro Nacional y Mercado Central. Comida típica en el mercado o alrededores. Vuelta al hotel sobre las 16:00 para piscina y descanso.",
        "photos_url": None,
        "docs": [],
    },
    # --- Tortuguero ---
    {
        "id": "canales-tortuguero",
        "destination_id": "tortuguero",
        "day_label": "Jue 20 agosto",
        "time": "06:00",
        "title": "Traslado por los canales",
        "description": "Recogida en el hotel a las 06:00. A Tortuguero solo se puede llegar en barca: traslado en bus y después en bote por los canales, con visita al pueblo a la llegada.",
        "photos_url": None,
        "docs": [],
    },
    {
        "id": "parque-nacional-tortuguero",
        "destination_id": "tortuguero",
        "day_label": "Vie 21 agosto",
        "time": "08:30",
        "title": "Parque Nacional Tortuguero",
        "description": "Paseo en bote por los canales para observar monos, caimanes y fauna del parque. Por la tarde, caminata por los senderos del bosque.",
        "photos_url": None,
        "docs": [],
    },
    {
        "id": "desove-tortugas",
        "destination_id": "tortuguero",
        "day_label": "Vie 21 agosto",
        "time": "20:00",
        "title": "Tour de desove de tortugas",
        "description": "Salida nocturna guiada a la playa para ver a las tortugas desovar. Una de las experiencias más especiales del viaje.",
        "photos_url": None,
        "docs": [],
    },
    # --- La Fortuna ---
    {
        "id": "catarata-la-fortuna",
        "destination_id": "la-fortuna",
        "day_label": "Dom 23 agosto",
        "time": "08:00",
        "title": "Catarata La Fortuna",
        "description": "Descenso hasta la cascada de La Fortuna, una de las más fotografiadas de Costa Rica. Zona habilitada para baño en la poza.",
        "photos_url": None,
        "docs": [],
    },
    {
        "id": "puentes-colgantes",
        "destination_id": "la-fortuna",
        "day_label": "Lun 24 agosto",
        "time": "08:00",
        "title": "Puentes Colgantes de Mistico",
        "description": "Recorrido guiado por el bosque nuboso a través de los puentes colgantes, con vistas al volcán Arenal.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher Puentes Colgantes Mistico", "url": "https://drive.google.com/file/d/1p19lmTYQLf4FiYDsQjatOQ3c_GDytfZc/view?usp=drive_link"},
        ],
    },
    {
        "id": "ecotermales",
        "destination_id": "la-fortuna",
        "day_label": "Lun 24 agosto",
        "time": "Tarde libre",
        "title": "Ecotermales",
        "description": "Tarde de relax en las aguas termales del volcán, con comida incluida.",
        "photos_url": None,
        "docs": [],
    },
    # --- Manuel Antonio ---
    {
        "id": "rio-tarcoles",
        "destination_id": "manuel-antonio",
        "day_label": "Mar 25 agosto",
        "time": "En ruta",
        "title": "Cocodrilos en el Río Tárcoles",
        "description": "Parada en el camino hacia Manuel Antonio para ver los grandes cocodrilos del río Tárcoles desde el puente.",
        "photos_url": None,
        "docs": [],
    },
    {
        "id": "manglares",
        "destination_id": "manuel-antonio",
        "day_label": "Mié 26 agosto",
        "time": "08:00",
        "title": "Tour de manglares en bote",
        "description": "Recogida en el hotel a las 08:00 para un recorrido en bote por los manglares, observando aves y fauna local.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher tour manglares", "url": "https://drive.google.com/file/d/1UkeQpsG00TU5xKVJ0mSmNuaM02j-NFyd/view?usp=drive_link"},
        ],
    },
    {
        "id": "parque-nacional-manuel-antonio",
        "destination_id": "manuel-antonio",
        "day_label": "Jue 27 agosto",
        "time": "07:00",
        "title": "Parque Nacional Manuel Antonio",
        "description": "Visita guiada al parque nacional: fauna y playas dentro del parque. Tarde libre de playa.",
        "photos_url": None,
        "docs": [
            {"label": "Entrada PN Manuel Antonio", "url": "https://drive.google.com/file/d/1OfjBzH6Ilkcy9IUcq5rH7jUDmTArTJUM/view?usp=drive_link"},
        ],
    },
    {
        "id": "ballenas-uvita",
        "destination_id": "manuel-antonio",
        "day_label": "Vie 28 agosto",
        "time": "07:00",
        "title": "Avistamiento de ballenas en Uvita",
        "description": "Excursión en barco hasta Uvita para el avistamiento de ballenas. Tarde de playa y despedida de Manuel Antonio.",
        "photos_url": None,
        "docs": [
            {"label": "Voucher tour ballenas", "url": "https://drive.google.com/file/d/1wAB3lNp2-1u2uitMXSvS1kc1c53UbuCo/view?usp=drive_link"},
        ],
    },
]

# Itinerario dia a dia para el calendario de la pagina de inicio.
DAYS = [
    {"n": 1, "weekday": "Martes", "date": "18 ago", "destination_id": "san-jose",
     "headline": "Vuelo", "detail": "Madrid → Panamá → San José, llegada 21:45"},
    {"n": 2, "weekday": "Miércoles", "date": "19 ago", "destination_id": "san-jose",
     "headline": "San José", "detail": "Plaza principal, Teatro Nacional, Mercado Central"},
    {"n": 3, "weekday": "Jueves", "date": "20 ago", "destination_id": "tortuguero",
     "headline": "Llegada", "detail": "Traslado en bus y barca por los canales"},
    {"n": 4, "weekday": "Viernes", "date": "21 ago", "destination_id": "tortuguero",
     "headline": "PN Tortuguero", "detail": "Canales en bote · senderos · desove de tortugas 20:00"},
    {"n": 5, "weekday": "Sábado", "date": "22 ago", "destination_id": "la-fortuna",
     "headline": "Llegada", "detail": "Traslado en barca y coche · tarde en el pueblo"},
    {"n": 6, "weekday": "Domingo", "date": "23 ago", "destination_id": "la-fortuna",
     "headline": "Catarata", "detail": "Cascada La Fortuna"},
    {"n": 7, "weekday": "Lunes", "date": "24 ago", "destination_id": "la-fortuna",
     "headline": "Puentes", "detail": "Puentes Colgantes de Mistico, con guía"},
    {"n": 8, "weekday": "Martes", "date": "25 ago", "destination_id": "manuel-antonio",
     "headline": "Llegada", "detail": "Cocodrilos en el Tárcoles · atardecer en Espadilla"},
    {"n": 9, "weekday": "Miércoles", "date": "26 ago", "destination_id": "manuel-antonio",
     "headline": "Manglares", "detail": "Tour en bote por los manglares"},
    {"n": 10, "weekday": "Jueves", "date": "27 ago", "destination_id": "manuel-antonio",
     "headline": "PN Manuel Antonio", "detail": "Visita guiada al parque · tarde de playa"},
    {"n": 11, "weekday": "Viernes", "date": "28 ago", "destination_id": "manuel-antonio",
     "headline": "Uvita", "detail": "Excursión avistamiento de ballenas"},
    {"n": 12, "weekday": "Sábado", "date": "29 ago", "destination_id": "san-jose",
     "headline": "Vuelta a SJ", "detail": "Traslado a San José (4h) · piscina"},
    {"n": 13, "weekday": "Domingo", "date": "30 ago", "destination_id": "san-jose",
     "headline": "Vuelo", "detail": "San José → Panamá → Madrid (llegada 31/08)"},
]

# La página de Documentos tiene 4 categorías: Hoteles, Transportes, Excursiones y Varios.
#
# "Hoteles" se genera solo a partir de DESTINATIONS (arriba) y "Excursiones" se genera
# solo a partir de ACTIVITIES: no hace falta repetir esos documentos aquí, con ponerlos
# en el "docs" del destino o de la actividad correspondiente ya aparecen en las dos
# páginas a la vez.
#
# Aquí solo se editan los documentos que no pertenecen a un destino o actividad
# concretos: vuelos y traslados (TRANSPORT_DOCS) y todo lo demás (MISC_DOCS).

TRANSPORT_DOCS = [
    {"title": "Madrid → Panamá → San José", "subtitle": "Vuelo · 18 agosto · sale 15:05, llega 21:45", "docs": []},
    {"title": "San José → Panamá → Madrid", "subtitle": "Vuelo · 30 agosto · sale 14:48, llega 31/08 13:15", "docs": []},
    {"title": "Tortuguero → La Fortuna", "subtitle": "Traslado · 22 agosto · barca y coche", "docs": []},
    {"title": "La Fortuna → Manuel Antonio", "subtitle": "Traslado · 25 agosto", "docs": []},
    {"title": "Manuel Antonio → San José", "subtitle": "Traslado · 29 agosto", "docs": []},
]

MISC_DOCS = [
    {"title": "Póliza y condiciones del seguro", "subtitle": "Cobertura del 18 al 31 de agosto", "docs": []},
]

# Gastos reales (EUR), tal y como estan en la hoja de planificacion.
EXPENSES = {
    "categories": [
        {"label": "Avión", "amount": 4211.16, "color": "ciudad"},
        {"label": "Alojamiento", "amount": 2461.07, "color": "hoja"},
        {"label": "Comidas", "amount": 1655.00, "color": "mango"},
        {"label": "Actividades", "amount": 1128.81, "color": "guanacaste"},
        {"label": "Traslados", "amount": 900.00, "color": "oceano"},
        {"label": "Seguro de viaje", "amount": 285.00, "color": "tinta"},
    ],
    "total": 10641.04,
    "paid": 4352.16,
    "pending": 2285.33,
}
