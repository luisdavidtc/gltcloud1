# Módulo de Compras — Fase 1: Modelos y migraciones

## ⚠️ Importante antes de aplicar esto en tu entorno
Django no está instalado en el sandbox donde preparé esta fase (sin acceso a
internet). Escribí las migraciones **a mano**, replicando exactamente el
formato de Django 5.1.15 (verificado campo por campo contra tus migraciones
reales de `sales` y `providers`), y comparé programáticamente que cada campo
de `purchases/models.py` tenga su reflejo exacto en la migración — coinciden
los 4 modelos. Aun así, **antes de aplicar `migrate`**, corre en tu entorno:

```bash
python manage.py makemigrations --check --dry-run
```

Si Django no detecta cambios pendientes sobre estos modelos, la migración
escrita a mano quedó bien alineada con el código. Si detecta algo, dime qué
reporta y lo ajusto.

## App nueva: `purchases`
- `purchases/models.py` — 4 modelos:
  - **`Compra`** (cabecera, mismo patrón que `sales.Sale`): empresa,
    proveedor, forma de pago (contado/crédito), estado (borrador/confirmada/
    anulada), estado de pago, sesión de caja (solo si contado), totales
    (subtotal/descuento/IVA/total), observaciones.
  - **`ItemCompra`** (líneas): producto, cantidad, costo unitario,
    descuento, subtotal.
  - **`CuentaPorPagar`**: se genera para compras a crédito. Guarda
    `saldo_pendiente` y `fecha_vencimiento`, lista para que más adelante se
    le agregue el registro de abonos (fuera de alcance de esta fase).
  - **`AdjuntoCompra`**: archivo (PDF o imagen) asociado a una compra.
- `purchases/admin.py` — registrado en el admin de Django para que puedas
  crear/ver compras de prueba **ya en esta fase**, sin esperar a la Fase 2
  (vistas/formularios propios).
- `purchases/migrations/0001_initial.py`.

## Cambios aditivos en apps existentes (nada se rompe)
1. **`providers/models.py`**: se agregaron `condicion_pago_dias` y
   `cupo_credito` a `Proveedor` (ambos con default, no afectan proveedores
   existentes). Migración: `providers/migrations/0005_proveedor_condicion_pago_cupo_credito.py`
   — toca también `HistoricalProveedor` (la tabla de auditoría), siguiendo el
   mismo patrón que ya usaste en `0002_proveedor_empresa.py`.
2. **`cashregister/models.py`**: se agregó `compra_relacionada` a
   `CashMovement` — exactamente el hueco que `Origen.COMPRA` ya dejaba
   preparado, con el mismo patrón que `venta_relacionada` (FK opcional,
   `SET_NULL`, nula en todo lo existente). Migración:
   `cashregister/migrations/0007_cashmovement_compra_relacionada.py`.
3. **`erp_config/settings.py`**: se agregó `'purchases'` a `INSTALLED_APPS`.

## Servicio reutilizable de inventario (tu punto 3)
`inventory/services.py` (archivo nuevo) — `registrar_entrada_inventario()`:
recibe un producto, una cantidad y un costo, y actualiza `stock` +
`precio_compra` (costo promedio ponderado) **en un solo lugar**. Ninguna
vista ni modelo debe tocar `Product.stock` directamente; todo lo que entre
mercancía (Compras ahora, ajustes/devoluciones en el futuro) pasa por aquí.
Está pensada para llamarse dentro de una transacción ya abierta por quien
orquesta la operación completa — eso es la Fase 2.

## Sobre tus dos observaciones de arquitectura
- **Transacción atómica única (Compras + Inventario + Caja + Cuentas por
  pagar):** el modelo ya queda listo para eso (todas las FKs necesarias
  existen), pero la orquestación en sí (`purchases.services.confirmar_compra`,
  con `@transaction.atomic`) es lógica de servicio, no de modelo — se
  implementa en la Fase 2, cuando exista la vista que la dispara.
- **Caja preparada para más tipos de movimiento, no solo compras:** evalué
  usar un `GenericForeignKey` en `CashMovement` en vez de una FK dedicada por
  origen, y decidí **no** hacerlo por ahora — lo documenté en un comentario
  dentro de la migración `0007`. Motivo: tu proyecto ya usa el patrón "una FK
  dedicada por origen" (`venta_relacionada`), que da validación de tipo a
  nivel de base de datos y es más simple de consultar en los reportes de
  cierre de caja que ya existen. Un `GenericForeignKey` es más genérico, pero
  es un cambio de paradigma sobre un modelo financiero en producción, y hoy
  solo tienes 2 orígenes reales (venta, compra). Si en el futuro aparecen
  varios orígenes más, ese sería el momento de reconsiderarlo — lo dejo
  anotado para no perder la decisión.

## Lo que NO se tocó
- Ninguna vista, url, formulario ni template existente.
- El modelo `Product` no cambió (el costo promedio se calcula y se guarda en
  su mismo campo `precio_compra`, que ya existía).
- `Sale`, `CashSession`, `CashMovement` (aparte del campo nuevo) siguen
  funcionando exactamente igual.

## Siguiente paso
Cuando confirmes que `makemigrations --check` no reporta diferencias y que
puedes crear una Compra de prueba desde el admin de Django, seguimos con la
**Fase 2**: formulario + vista de guardado, con `purchases.services.confirmar_compra()`
orquestando Compra + Inventario + Caja + Cuenta por pagar en una sola
transacción atómica.
