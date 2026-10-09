# Fase de mejoras UX/Productividad — Notas de implementación

Seis cambios, ninguno modifica la arquitectura existente (Django + apps
por dominio + Bootstrap 5) ni rompe funcionalidad. Se verificó sintaxis
Python y JS de todo el proyecto después de cada cambio.

## Cambio 1 — Importación masiva de inventario desde Excel

- `inventory/import_utils.py` (nuevo): toda la lógica de lectura/validación
  (con `openpyxl`, ya era dependencia del proyecto) y de creación/
  actualización, separada de las vistas.
- Validaciones: encabezados exactos de la plantilla, tipos de dato por
  columna (números no negativos, enteros), duplicados de código dentro
  del propio archivo. Cada error indica su **fila real del Excel**.
- **Todo o nada**: si hay algún error, no se importa ningún producto —
  se muestran todos los errores encontrados de una vez.
- Si no hay errores, la importación corre dentro de `transaction.atomic`
  (`inventory/import_utils.py::aplicar_importacion`).
- Upsert por código (evita duplicados): si el código ya existe *en la
  empresa actual*, se actualiza; si no, se crea. Las categorías por
  nombre se crean automáticamente si no existen.
- Plantilla descargable (`product_import_template`) generada con
  `openpyxl` directamente (encabezados en negrita + fila de ejemplo).
- Nuevas rutas: `/inventario/productos/importar/` y `.../plantilla/`.
  Botón "Importar Excel" agregado en `product_list.html`.
- Integrado con el aislamiento por empresa ya construido (Entregas 1-2
  del plan multiempresa): usa `inventory.tenant_utils.obtener_empresa_actual`.
- **Corrección posterior — blindaje multiempresa:** se auditó línea por
  línea `aplicar_importacion` y `product_import`; las dos únicas
  creaciones (`Category.objects.create`, `Product.objects.create`) ya
  pasaban `empresa=empresa` explícito. Se agregaron además dos guardas
  defensivas para que sea estructuralmente imposible crear algo con
  `empresa_id=NULL`: (1) `product_import` corta con un mensaje claro
  *antes* de leer el archivo si `obtener_empresa_actual` no devuelve
  ninguna empresa; (2) `aplicar_importacion` valida lo mismo al entrar y
  levanta un `ValueError` legible en vez de dejar que la base de datos
  rechace la fila con un `IntegrityError` críptico. La vista captura
  ambos casos y los muestra como mensaje, sin romper la página.

## Cambio 2 — Servicio Técnico simplificado

- `templates/repairs/order_form.html` reorganizado: quedan visibles de
  entrada solo Cliente, Equipo, Marca, Modelo, IMEI, Daño reportado,
  Técnico asignado y Observaciones.
- Diagnóstico, Concepto de servicio (factura), Repuestos y Costos (mano
  de obra/IVA/total) pasaron a un acordeón Bootstrap **"Información
  adicional"**, que se **auto-expande si hay errores de validación**
  dentro (para que nunca queden ocultos).
- "Estado" no se agregó como campo del alta a propósito: no es un campo
  editable libremente (tiene sus propias reglas de transición vía
  `RepairStatusForm`) y ya se muestra de forma prominente en
  `order_detail.html`, donde corresponde.
- **Cero cambios de lógica**: mismos campos del formulario
  (`repairs/forms.py` no se tocó), mismos IDs de HTML, mismo
  `static/js/order_form.js` sin modificar — solo se reordenó dónde vive
  cada bloque en la página.

## Cambio 3 — Experiencia de usuario

Alcance real (no se reescribió cada formulario del sistema uno por uno,
por riesgo/tiempo — se resolvió con **componentes compartidos** que
mejoran todas las pantallas que los usan de una sola vez):

- **Paginación**: antes, solo `providers` paginaba (`Paginator`, 20 por
  página) y con una URL de paginación armada a mano (`?page=N&q=...`,
  que se rompía en silencio cada vez que se agregaba un filtro nuevo y
  no se actualizaba ese enlace). Ahora:
  - `templates/partials/_pagination.html` (nuevo): componente único,
    reutilizado por `inventory` (productos y categorías), `clients`,
    `sales` (ventas) y `repairs` (órdenes), además de migrar `providers`
    al mismo componente.
  - `core/templatetags/core_extras.py::query_replace` (nuevo): arma el
    enlace de página preservando **todos** los filtros activos de la
    URL automáticamente, sin listarlos a mano.
  - Antes, `inventory`, `clients`, `sales` y `repairs` no paginaban en
    absoluto — listaban toda la tabla en una sola página. Esto era a la
    vez un problema de UX y de rendimiento a futuro (con miles de
    productos/ventas, esas páginas se habrían vuelto lentas).
- **Alertas y mensajes**: ya estaban bien resueltos (`base.html`, con
  `alert-dismissible fade show` y colores por tipo de mensaje) — se
  revisaron y no se encontró necesidad de cambios.
- **Selects/formularios de las apps tocadas en esta fase** (`inventory`,
  `clients`, `providers`) ya usan clases Bootstrap (`form-control`,
  `form-select`) desde las Entregas 1-2 del plan multiempresa.

## Cambio 4 — Lector de código de barras USB

Sin ninguna librería nueva (el lector funciona como teclado, no necesita
una API especial):

- **Punto de venta** (`static/js/sale_form.js`): al presionar Enter en el
  buscador de productos (lo que hace automáticamente cualquier lector
  USB después de leer un código), se dispara una búsqueda inmediata; si
  hay una coincidencia exacta de código, el producto se agrega solo a la
  venta y el campo queda listo para el siguiente escaneo. Si hay stock
  0, se marca el campo en rojo brevemente en vez de agregarlo.
- **Búsqueda rápida en inventario**: el buscador de `product_list.html`
  ya vivía dentro de un `<form method="get">`, así que escanear un
  código y presionar Enter ya funcionaba (envío nativo del formulario);
  se le agregó `autofocus` para no tener que hacer clic primero.
- `product_search` (`sales/views.py`) ya filtraba por `codigo_barras`,
  no fue necesario tocar el backend.

## Cambio 5 — Versión del sistema

- `erp_config/settings.py`: `ERP_NOMBRE` / `ERP_VERSION = '1.1.0'` — la
  única fuente de verdad del número de versión.
- `core/context_processors.py` (nuevo, registrado en `TEMPLATES`): expone
  esos dos valores a todos los templates.
- `templates/base.html`: el pie del menú lateral (esquina inferior
  izquierda) ahora muestra "ERP Celulares" y "Versión 1.1.0" leídos de
  ahí, reemplazando el "v1.0" que estaba escrito a mano.

## Cambio 6 — Refactor y optimización

- Se revisaron las vistas de listado/detalle de `sales`, `repairs`,
  `providers` e `inventory`: **ya usaban `select_related`/`prefetch_related`
  correctamente** donde hacía falta (ej. `Sale.objects.select_related('cliente', 'vendedor')`,
  `orden.repuestos.select_related('producto')`) — no se encontró ningún
  N+1 real pendiente en esas pantallas.
- La optimización de mayor impacto real de esta fase fue agregar
  paginación donde no existía (Cambio 3): antes esas vistas traían **toda**
  la tabla a memoria en cada request, sin límite.
- Código duplicado eliminado: la paginación manual de `providers`
  (repetida por cada filtro) se reemplazó por el componente compartido
  (Cambio 3).
- Compatibilidad con Django 5 y con el aislamiento por empresa ya
  implementado (Entregas 1-2): todas las paginaciones agregadas envuelven
  querysets que ya estaban filtrados por `empresa`, sin alterar ese
  filtrado.

## Cómo probar cada cambio

1. **Importación**: Inventario → "Importar Excel" → descargar plantilla,
   llenarla (incluyendo un código que ya exista, para probar que
   actualiza en vez de duplicar), subirla.
2. **Servicio Técnico**: crear una orden nueva — debe verse mucho más
   corta; abrir "Información adicional" y confirmar que repuestos/costos
   siguen calculando el total igual que antes.
3. **Paginación**: cargar más de 25 productos/clientes/ventas/órdenes (o
   bajar el número por página temporalmente para probar) y verificar que
   los filtros de búsqueda se mantienen al cambiar de página.
4. **Lector de código de barras**: en una venta nueva, escribir (o
   escanear) el código exacto de un producto en el buscador y presionar
   Enter — debe agregarse solo.
5. **Versión**: revisar la esquina inferior izquierda del menú.
