# Módulo de Reportes — Notas de implementación

Este documento resume los cambios hechos para agregar el módulo de **Reportes**
al ERP, para quien retome el proyecto después.

## Archivos nuevos

```
reports/
├── __init__.py
├── apps.py
├── models.py            # vacío a propósito (ver docstring del archivo)
├── utils.py              # helpers de fecha y ordenamiento, compartidos
├── services.py            # TODAS las consultas/agregaciones (única fuente de verdad)
├── formatting.py           # helpers de moneda/número compartidos
├── pdf.py                # generador de PDF genérico, reutilizado por los 9 reportes
├── views.py               # 1 vista de pantalla + Excel + PDF (+ ticket donde aplica) por reporte
├── urls.py
└── templatetags/
    ├── __init__.py
    └── reports_extras.py   # tag `query_replace` para encabezados de columna ordenables

templates/reports/
├── index.html              # panel de acceso a todos los reportes
├── dashboard.html           # dashboard de indicadores (KPIs + gráficos Chart.js)
├── ventas_dia.html / ventas_dia_ticket.html
├── ventas_rango.html
├── top_productos.html
├── inventario.html
├── clientes.html / cliente_historial.html
├── proveedores.html
├── caja.html / caja_ticket.html
├── gastos.html
├── reparaciones.html
└── _export_buttons.html, _index_card.html, _th_orden.html   # parciales reutilizables
```

## Archivos modificados

- `erp_config/settings.py`: se agregó `'reports'` a `INSTALLED_APPS`.
- `erp_config/urls.py`: se montó `path('reportes/', include('reports.urls'))`.
- `templates/base.html`: el ítem de menú "Reportes" (antes `href="#"`) ahora
  enlaza a `reports:index` y solo se muestra a administradores (`user.es_admin`).

**No se modificó ningún modelo existente** ni se agregaron migraciones: todo el
módulo es de solo lectura sobre los modelos que ya existían.

## Decisiones de diseño (por qué se hizo así)

1. **Reutilización, no duplicación.** `reports/services.py` no reimplementa
   nada que ya exista: el cálculo de saldo/ingresos/egresos de una sesión de
   caja llama a `cashregister.services.calcular_resumen_movimientos` (la misma
   función que usa el propio módulo de Caja al abrir/cerrar/exportar), y la
   exportación a Excel usa `core.excel.exportar_a_excel` tal cual la usan
   Proveedores y Compras.

2. **Un solo generador de PDF (`reports/pdf.py::generar_pdf_reporte`)** para
   los 9 reportes, en vez de reescribir la plomería de reportlab en cada uno.
   Cada vista solo arma columnas/filas/resumen ya formateados como texto.

3. **Acceso restringido a administradores** (`ROLES_REPORTES = ('admin',)`
   en `reports/views.py`), porque el módulo cruza información sensible de
   varias áreas a la vez (utilidad, caja, gastos) — a diferencia de los
   listados propios de cada app (ej. Ventas, que sí ven los vendedores).

4. **Dos limitaciones del ERP actual que el reporte NO inventa para resolver:**
   - **Compras**: no existe el modelo `Compra` todavía (`providers.models.Proveedor`
     ya deja preparado `related_name='compras'` para cuando se implemente en una
     fase posterior — ver `Proveedor.puede_eliminarse`). El reporte de
     "Proveedores y compras" lista los proveedores registrados con una nota
     explícita de esta limitación; en cuanto exista `Compra`, sus totales
     aparecerán ahí solos.
   - **Deuda de clientes**: el ERP no registra ventas a crédito ni cuentas por
     cobrar (`Sale` no tiene ese concepto). El reporte de Clientes lo señala
     como "No aplica" en vez de mostrar un número inventado.
   - **Categoría de gastos**: `CashMovement` no tiene un campo de categoría
     propio; se usa `concepto` (el texto con el que se registra cada gasto en
     Caja) como agrupador, documentado en el propio reporte.

5. **Consultas optimizadas**: todas usan `select_related`/`prefetch_related`
   sobre las relaciones accedidas en listados (`cliente`, `vendedor`,
   `categoria`, `usuario`, `tecnico`, etc.), agregaciones con `Sum`/`Count`/
   `Coalesce` en la base de datos en vez de traer todo a Python, y el gráfico
   de 30 días del dashboard usa una sola consulta agrupada por día (con
   `TruncDate`) en vez de 30 consultas sueltas.

6. **Ordenamiento**: cada columna ordenable de las tablas es un encabezado
   clicable (parcial `_th_orden.html`) que arma el enlace con el tag
   `query_replace`, preservando el resto de filtros aplicados. El campo real
   por el que se ordena está siempre validado contra una lista blanca en
   `services.py`/`utils.py` (nunca se ordena por un nombre de campo arbitrario
   recibido de la URL).

## Reportes incluidos y sus filtros

| Reporte | Filtros | Exporta |
|---|---|---|
| Ventas del día | fecha, vendedor, método de pago, buscar | Excel, PDF, Ticket |
| Ventas por rango | desde/hasta, vendedor, método de pago, buscar | Excel, PDF |
| Productos más vendidos | desde/hasta, vendedor | Excel, PDF |
| Inventario | buscar, categoría, estado de stock | Excel, PDF |
| Clientes | desde/hasta, buscar (+ historial por cliente) | Excel, PDF |
| Proveedores y compras | buscar, estado, ciudad | Excel, PDF |
| Caja | desde/hasta, usuario, estado | Excel, PDF, Ticket |
| Gastos | desde/hasta, usuario, categoría (concepto) | Excel, PDF |
| Servicio técnico | desde/hasta, estado, técnico, buscar | Excel, PDF |
| Dashboard de indicadores | (sin filtros; ventas día/semana/mes) | — |

## Pendiente / siguientes pasos sugeridos

- No fue posible ejecutar `python manage.py check`/`runserver` en este entorno
  (sin Django instalado y sin acceso a red para instalarlo). Se hizo una
  revisión estática exhaustiva: sintaxis de todos los `.py` con `py_compile`,
  cruce de cada nombre de URL usado en las plantillas contra `reports/urls.py`,
  balance de tags `{% block/for/if/with %}` en cada template, y verificación
  manual de cada nombre de campo de modelo usado contra el código fuente real
  de `sales`, `clients`, `providers`, `repairs`, `cashregister`, `inventory` y
  `accounts`. Aun así, se recomienda correr `python manage.py check` y abrir
  cada reporte una vez en un entorno con Django instalado antes de producción.
- Paginación: las tablas de los reportes no están paginadas (a diferencia de
  algunos listados existentes). Con catálogos/históricos grandes conviene
  agregar `Paginator` a `ventas_rango`, `inventario`, `clientes` y `gastos`.
- Cuando se implemente el módulo de Compras, actualizar
  `reports/services.py::filtrar_proveedores` y la plantilla `proveedores.html`
  para sumar los totales reales (ya están señalizados con comentarios `TODO`
  implícitos en la documentación de la función).

## Ticket de recepción de reparaciones: QR + fotos + estado

Toda esta funcionalidad (QR de consulta, fotos visibles para el cliente y
estado de la reparación) **ya existía en el proyecto** (`RepairEvidence`,
`RepairOrder.get_public_status_url`, `repairs:public_order_status`,
`templates/repairs/public_status.html`), pero el QR no aparecía en el ticket
que se entrega al cliente al recibir el equipo porque estaba condicionado a
un ajuste global de Configuración de Empresa (`PrintSettings.mostrar_qr`) que
viene **desactivado por defecto**, y que además también controla el QR del
comprobante de venta (no es exclusivo de reparaciones).

Cambios hechos:

- `repairs/views.py::order_print`: el QR de la orden de servicio ahora se
  genera **siempre**, sin depender de `impresion.mostrar_qr` — igual que ya
  hacía `order_detail`. Se mantiene el uso de `mostrar_logo` para el logo.
  Justificación: en esta orden el QR no es decorativo, es la única forma que
  tiene el cliente de consultar el estado y las fotos de su reparación sin
  llamar o volver a la tienda; en el comprobante de venta sí sigue siendo
  opcional vía `mostrar_qr`.
- `templates/repairs/order_print.html` (ambos formatos, carta y térmico):
  se agregó el texto "Escanea para ver el estado y las fotos de tu
  reparación" junto al QR, para que quede claro qué hace al escanearlo.
- `templates/repairs/public_status.html` (la página a la que apunta el QR,
  pública y sin login): ya mostraba el estado (badge) y las fotos marcadas
  como visibles para el cliente (`RepairEvidence.Visibilidad.CLIENTE`); se
  agregó un mensaje ("Todavía no se han subido fotos...") para cuando el
  cliente escanea el ticket recién recibido, antes de que el técnico suba la
  primera foto, en vez de mostrar la sección vacía sin explicación.
- `company/models.py::PrintSettings.mostrar_qr`: se actualizó su
  `verbose_name`/`help_text` para aclarar que ahora solo aplica al
  comprobante de venta (ya no al ticket de servicio técnico), y se agregó la
  migración `company/migrations/0004_alter_printsettings_mostrar_qr.py`
  (cambio de metadatos del campo, sin alterar la columna en base de datos).

Cómo subir fotos durante la reparación: desde `order_detail` (detalle de la
orden dentro del ERP) ya existe el formulario de evidencias
(`evidence_upload`), donde el técnico marca cada foto como "Visible para el
cliente" o "Solo interno"; solo las marcadas como visibles para el cliente
aparecen al escanear el QR.

