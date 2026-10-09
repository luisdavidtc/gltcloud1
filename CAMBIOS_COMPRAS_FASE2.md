# Módulo de Compras — Fase 2: Formulario, vista y confirmación atómica

## Archivos nuevos
- `purchases/tenant_utils.py` — mismo patrón que el resto del ERP.
- `purchases/forms.py` — `CompraForm` (cabecera: proveedor, forma de pago,
  n.º factura del proveedor, descuento, IVA, observaciones).
- `purchases/services.py` — **el corazón de esta fase**:
  - `confirmar_compra(compra, sesion_caja=None)`: dentro de un único
    `transaction.atomic()`, (1) entra el stock de cada ítem llamando a
    `inventory.services.registrar_entrada_inventario` (nunca toca
    `Product.stock` directamente), (2) recalcula los totales definitivos,
    (3) si es de contado, asigna la sesión de caja y llama a
    `cashregister.services.registrar_compra_en_caja`; si es a crédito, crea
    la `CuentaPorPagar` con la fecha de vencimiento calculada desde
    `proveedor.condicion_pago_dias`, (4) marca la compra como CONFIRMADA. Si
    cualquier paso falla, todo se revierte — no queda nada a medias.
  - `guardar_borrador(compra)`: solo recalcula y guarda, sin tocar
    inventario/caja/cuentas por pagar.
- `purchases/views.py` — `purchase_create` (crear con ítems dinámicos,
  guardar borrador o confirmar), `purchase_detail`, y los endpoints JSON
  `provider_search`/`product_search` (copias propias, no reutiliza los de
  `sales`, para que `purchases` no dependa de esa app).
- `purchases/urls.py`, montado en `/compras/` (`erp_config/urls.py`).
- `templates/purchases/purchase_form.html` y `purchase_detail.html` — **funcionales pero
  todavía con el diseño simple** (cards del design system, sin el grid tipo
  POS de Remisiones). Ya lo dice el propio template arriba del formulario.
  Eso es la Fase 3, como quedó acordado.
- `static/js/purchase_form.js` — búsqueda de proveedor/producto, carrito de
  ítems, cálculo de totales en vivo.

## Archivos modificados (aditivo, un método nuevo, nada existente se toca)
- `cashregister/services.py`: se agregó `registrar_compra_en_caja(compra)`,
  contraparte de `registrar_venta_en_caja` pero como egreso. Ninguna función
  existente cambió una sola línea.

## Cómo se prueba
1. Confirmar que las migraciones de la Fase 1 corrieron bien
   (`makemigrations --check` sin diferencias, `migrate` aplicado).
2. Crear un proveedor de prueba (ya puedes ponerle condición de pago y
   cupo de crédito, agregados en la Fase 1).
3. Ir a `/compras/nueva/`, buscar el proveedor, agregar productos, elegir
   forma de pago:
   - **Contado**: si no tienes caja abierta, te lo dice claramente y te
     ofrece guardar como borrador en vez de bloquear todo el formulario.
     Con caja abierta, al confirmar: sube el stock del producto, se
     recalcula su costo promedio, y el total se descuenta de la caja.
   - **Crédito**: al confirmar, se crea la `CuentaPorPagar` con la fecha de
     vencimiento calculada desde el plazo del proveedor.
4. Revisa en el admin de Django (`/admin/purchases/`) que la Compra, sus
   ItemCompra y (si aplica) la CuentaPorPagar quedaron creados
   correctamente, y en `/admin/inventory/product/` que el stock/costo del
   producto se actualizó.

## Lo que NO se tocó
- Ninguna vista, formulario ni lógica de `sales`, `inventory`, `providers`,
  `clients`, `company`, `repairs`.
- Las funciones ya existentes de `cashregister/services.py`
  (`registrar_venta_en_caja`, `reversar_venta_en_caja`, etc.) — se agregó una
  función nueva, no se modificó ninguna.

## Siguiente paso
Cuando confirmes que puedes crear, guardar como borrador y confirmar una
compra (de contado y a crédito) sin errores, seguimos con la **Fase 3**: el
diseño visual definitivo (grid de productos, cards, atajos de teclado),
igual que hicimos con Remisiones.
