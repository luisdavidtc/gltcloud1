# Pagos mixtos: combinar hasta 3 métodos de pago en una venta

## Qué cambió

Antes, `Sale.metodo_pago` era un solo campo: una venta se pagaba con un
único método por el total completo. Ahora una venta se puede pagar
combinando hasta **3 métodos distintos** (ej. mitad efectivo, mitad
tarjeta), desde el mismo modal "Confirmar Venta" del POS.

## Backend

- **Nuevo modelo `SalePayment`** (`sales/models.py`): una fila por cada
  método usado en una venta (1 a 3 por venta). La suma de sus valores
  siempre es igual a `Sale.total`.
- **Nueva opción `MIXTO`** en `Sale.MetodoPago`: cuando una venta usa 2
  o más métodos, `Sale.metodo_pago` queda en `"Pago mixto"` — un resumen
  rápido para todo lo que ya filtraba/agrupaba por ese campo (listados,
  filtros de reportes, PDFs). El detalle real de cuánto se pagó con cada
  método vive en `Sale.pagos` (related name de `SalePayment`).
- **Migración de backfill** (`sales/migrations/0014`): a cada venta ya
  facturada antes de este cambio se le creó una única línea en
  `SalePayment`, igual a su `metodo_pago`/`total` de siempre. El
  histórico queda intacto y compatible — ninguna venta antigua aparece
  como "pago mixto".
- **`Sale.monto_pagado_con(metodo)`** y **`Sale.es_pago_mixto`**: nuevos
  helpers en el modelo, fuente de verdad para "cuánto de esta venta se
  pagó con tal método".
- **`cashregister.services.registrar_venta_en_caja`**: ahora suma a la
  caja solo la porción en efectivo de la venta (total o parcial en un
  pago mixto), en vez de asumir que toda la venta fue en efectivo.
- **`cashregister.services.calcular_ventas_por_metodo`** (cierre de
  caja): se recalculó para agrupar por `SalePayment` en vez de por
  `Sale.metodo_pago` — una venta mixta aparece correctamente repartida
  en sus métodos reales dentro del cierre, no como una sola fila.
- **`reports.services.resumen_ventas`**: el desglose por método de pago
  de los reportes de Ventas (pantalla, Excel, PDF y ticket) se ajustó de
  la misma forma, para no perder el detalle de una venta mixta bajo un
  genérico "Pago mixto".
- **Cupo de crédito**: en `sales.views.sale_create` y `sale_void`, la
  validación y el ajuste del cupo del cliente ahora se calculan solo
  sobre la porción de la venta pagada a crédito (puede combinarse con
  otros métodos), no sobre el total.
- **`repairs.models.RepairOrder.facturar`**: se ajustó para crear
  también su `SalePayment` (una línea en efectivo por el total, igual a
  su comportamiento histórico) — sin este cambio, facturar una
  reparación habría dejado de sumarse a la caja.

## Interfaz (POS)

- El modal "Confirmar Venta" reemplazó el selector de un solo método por
  una grilla que **agrega líneas de pago**: cada método elegido se suma
  como una línea editable, con un indicador "Falta por cubrir" en vivo.
- La línea de Efectivo conserva su campo "Valor recibido" y "Cambio"; la
  línea de Crédito muestra el cupo disponible del cliente — cada una
  valida solo su propia porción.
- No se puede repetir un método dentro de la misma venta, ni combinar
  más de 3 métodos. El botón "Finalizar Venta" solo se habilita cuando
  la suma de las líneas cubre exactamente el total.
- `sales/forms.py`: `metodo_pago` salió del formulario (ya no se elige
  con un select); `sales.views.sale_create` lo calcula y lo guarda él
  mismo a partir de las líneas de pago recibidas.

## Documentos

- `sale_detail.html` y `sale_print.html` (factura carta y ticket
  térmico) muestran el desglose línea por línea cuando la venta fue
  mixta.

## Validación hecha en este entorno

- `manage.py check`: sin errores.
- `manage.py makemigrations --check --dry-run`: sin cambios pendientes
  (los modelos y las migraciones quedan sincronizados).
- `manage.py migrate` sobre una base nueva: las 3 migraciones nuevas
  (`0012`, `0013`, `0014`) se aplican sin errores junto con el resto del
  historial de migraciones del proyecto.
- Script de humo (no incluido en la entrega) que ejercitó directamente
  los modelos/servicios modificados: venta con 3 métodos combinados,
  venta con 1 solo método (compatibilidad), rechazo de método repetido/
  más de 3 métodos/suma que no cuadra, ajuste automático de una
  diferencia de redondeo menor, y reversa del cupo de crédito solo por
  su porción — todos los casos pasaron.

## Decisiones tomadas (confirmadas con el cliente antes de implementar)

- Máximo 3 métodos de pago combinables por venta.
- "Crédito" puede combinarse con otros métodos (no es exclusivo).

## Pendiente / fuera de alcance de esta entrega

- El filtro "Método de pago" de los reportes de Ventas sigue
  funcionando sobre `Sale.metodo_pago` (exacto): para ver una venta
  mixta hay que filtrar explícitamente por "Pago mixto", no aparece al
  filtrar por "Efectivo" aunque haya tenido una porción en efectivo. Se
  dejó así a propósito para no rediseñar también la pantalla de filtros
  en esta entrega.
