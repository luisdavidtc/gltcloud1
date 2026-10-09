# Módulo de Compras — Fase 4: Integración del menú + Historial de compras

## Problema que se corrigió
El módulo `purchases` ya tenía modelos, formularios, servicios, vistas de
creación/detalle y migraciones (Fases 1-3), pero el menú lateral seguía
apuntando a `core:en_desarrollo` y no existía una pantalla principal
(`purchase_list`) — por eso al entrar a Compras aparecía "Próximamente".

## Archivos modificados

### Backend
- `purchases/urls.py` — se agregó `''` → `purchase_list` (pantalla
  principal), `<int:pk>/editar/` → `purchase_edit`, `<int:pk>/anular/` →
  `purchase_void`. Se mantuvieron intactas `purchase_create`,
  `purchase_detail` y las APIs de autocompletado.
- `purchases/views.py` — 3 vistas nuevas:
  - `purchase_list`: búsqueda por proveedor o número de compra, filtros
    por fecha y estado, paginación (mismo patrón que `sales.sale_list` /
    `providers.provider_list`).
  - `purchase_edit`: edita una compra **solo si está en BORRADOR**
    (reemplaza sus ítems y recalcula, igual que `purchase_create`). Una
    compra ya CONFIRMADA no se edita en sitio — ya afectó inventario y
    caja/cuentas por pagar, así que su único camino de reversa es anular.
  - `purchase_void`: anula una compra CONFIRMADA, devuelve el stock que
    había entrado y compensa caja (contado) o cancela la cuenta por pagar
    (crédito). Mismo patrón que `sales.sale_void`.
- `cashregister/services.py` — se agregó `reversar_compra_en_caja()`,
  contraparte de `reversar_venta_en_caja()` ya existente, para compensar
  el egreso de una compra de contado al anularse.

### Templates
- `templates/purchases/purchase_list.html` (nuevo): tabla con número,
  fecha, proveedor, estado, total, usuario y acciones (Ver / Editar si
  está en borrador / Anular si está confirmada); breadcrumb, buscador,
  filtros de fecha/estado y paginación reutilizando
  `partials/_pagination.html`.
- `templates/purchases/purchase_confirm_void.html` (nuevo): pantalla de
  confirmación antes de anular, igual que `sales/sale_confirm_void.html`.
- `templates/purchases/purchase_detail.html` — se agregó breadcrumb y
  botones Editar/Anular según el estado de la compra.
- `templates/purchases/purchase_form.html` — se adaptó para servir tanto
  a "Nueva compra" como a "Editar compra" (action del formulario,
  título/breadcrumb dinámicos, bloque `json_script` con los ítems ya
  guardados cuando se edita un borrador).
- `static/js/purchase_form.js` — se agregó (100% aditivo, al final del
  archivo, sin tocar ninguna función existente) la lógica que precarga
  las filas de producto cuando se edita un borrador.

### Menú (`templates/base.html`)
Dentro del submenú de Compras:
- **"Nueva compra"** (nuevo enlace) → `purchases:purchase_create`.
- **"Historial de compras"** → antes `core:en_desarrollo`, ahora
  `purchases:purchase_list`.
- **"Órdenes de compra", "Recepción de mercancía" y "Gastos"** se
  dejaron intencionalmente apuntando a `core:en_desarrollo`: son
  funcionalidades que todavía no existen (ni modelos ni vistas — ver
  nota de alcance en `purchases/models.py`), así que apuntarlas a una
  vista real habría simulado algo que no está construido. Quedan listas
  para cuando se aborden como fases futuras.

## Verificación realizada
Se migró el proyecto en SQLite, se creó una empresa/usuario/proveedor/
producto de prueba y se recorrió el flujo completo con el test client de
Django:
1. Listado vacío se ve correctamente.
2. Se crea una compra de **contado** y se confirma: el stock del
   producto sube en la cantidad comprada y se genera el movimiento de
   **egreso** en la caja abierta.
3. La compra aparece de inmediato en el listado; la búsqueda por número
   de compra (`?q=1`) y por proveedor (`?q=Distribuidora`) funcionan.
4. El detalle carga sin error.
5. Se anula la compra: el estado pasa a `anulada`, el stock vuelve a su
   valor original y se genera un ajuste positivo que compensa el egreso
   en caja.
6. Se crea una compra a **crédito** en borrador, se edita (cambiando
   cantidad, costo y forma de pago se mantiene crédito) y se confirma:
   genera la `CuentaPorPagar` correctamente.
7. Se confirma aislamiento multiempresa: acceder a una compra de otra
   empresa devuelve 404.

No se detectaron errores 404 ni rutas rotas en el recorrido.
