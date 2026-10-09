# Fix: carga masiva de inventario no reflejaba stock ni precio de venta

## Síntoma

Al importar productos desde el Excel de carga masiva, los productos se
creaban bien (nombre, código, categoría), pero en el POS/Remisión
aparecían con **$0 de precio y 0 de stock**.

## Causa

El proyecto guarda el stock y los precios en una tabla aparte por
empresa, `ProductoEmpresa` (para que dos empresas puedan compartir un
mismo producto del catálogo con stock y precios distintos cada una).
Esto se implementó cuando se agregó el soporte multiempresa, y el
formulario manual de "Nuevo producto" ya quedó actualizado para
guardar ahí (`inventory.views.product_create`/`product_update`).

La carga masiva (`inventory/import_utils.py`) nunca se actualizó: seguía
guardando `precio_compra`, `precio_venta`, `stock` y `stock_minimo`
directamente en `Product`, que son campos heredados que **ya no lee
ninguna pantalla** (POS, listados, reportes) — todas leen
`ProductoEmpresa`.

## Corrección

`inventory/import_utils.py` → `aplicar_importacion`: ahora, después de
crear o actualizar el `Product` (solo con nombre/categoría/marca/etc.),
guarda el stock y los precios en su `ProductoEmpresa` de la empresa que
importa (`producto.para_empresa(empresa)`), exactamente igual que hace
el formulario manual. Nada más cambió: mismas columnas del Excel, misma
plantilla, mismas validaciones.

No fue necesario tocar el modelo ni las migraciones — no se agregó
ningún campo nuevo, solo se corrigió a qué tabla se escribe.

## Validación hecha en este entorno

- `manage.py check` y `manage.py makemigrations --check --dry-run`: sin
  errores ni cambios pendientes (no se tocó ningún modelo).
- Script de humo que reprodujo el flujo completo: importar un producto
  nuevo (código, precio de compra/venta, stock) y confirmar que su
  `ProductoEmpresa` queda con esos valores; reimportar el mismo código
  con otros valores y confirmar que actualiza (no duplica) esa fila.

## Qué debes hacer

Vuelve a subir el mismo archivo Excel de carga masiva desde "Inventario
→ Importar productos". Como el código ya identifica los productos por
su columna "Código", los que ya existen se van a **actualizar** (no se
duplican) y esta vez sí van a quedar con el stock y el precio de venta
correctos.
