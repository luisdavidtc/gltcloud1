# Informe — página se quedaba cargando / productos no cargaban en Facturación

## Causa raíz
La corrección anterior (precio/stock) usó `Product.para_empresa(empresa)`
en TODOS los lugares, incluidos el buscador de Facturación y el
listado de Inventario. El problema: `para_empresa()` usa
`get_or_create` — es decir, **si el producto todavía no tenía una fila
`ProductoEmpresa` para esa empresa, la crea ahí mismo**, escribiendo en
la base de datos.

Eso convirtió dos pantallas que solo deberían **leer** datos (el
buscador de productos de Facturación, que se llama en cada tecla que
escribes, y el listado de Inventario) en pantallas que **escriben** en
la base de datos en cada petición. Con SQLite (que bloquea todo el
archivo de la base de datos durante una escritura), varias peticiones
casi simultáneas — como las que dispara escribir rápido en el buscador,
o recargar mientras otra pestaña sigue cargando — se ponen en fila
esperando el turno de escritura, y eso se siente como que la página no
responde o los productos nunca terminan de cargar.

## Solución aplicada
Separé claramente los dos casos:
- **`Product.para_empresa(empresa)`** — se mantiene igual, para cuando
  sí se va a modificar stock/precio (crear/editar producto, confirmar
  una compra o una venta). Ahí SÍ tiene sentido crear la fila si falta.
- **`Product.disponibilidad_en(empresa)`** (nuevo) — de solo lectura:
  si no existe la fila, devuelve los datos en cero sin guardar nada en
  la base de datos. Se usa en el buscador de Facturación y en el
  listado de Inventario — las dos pantallas de solo consulta.

## Archivos modificados
- `inventory/models.py` — nuevo método `disponibilidad_en()`; se documentó la diferencia con `para_empresa()`; `stock_bajo_en()` (no se usaba todavía en ningún lado, pero tenía el mismo problema) ahora también usa el de solo lectura.
- `sales/views.py` — el buscador de productos de Facturación (`product_search`) usa `disponibilidad_en()` en vez de `para_empresa()`. Los puntos que sí modifican stock (confirmar venta, anular venta) siguen usando `para_empresa()` sin cambios — ahí es correcto.
- `inventory/views.py` — el listado de productos (`product_list`) usa `disponibilidad_en()`. La creación/edición de producto sigue usando `para_empresa()` sin cambios.

## Pruebas realizadas
```
5 búsquedas seguidas en el buscador de Facturación (simulando escribir rápido):
  ProductoEmpresa antes: 2 → después: 2   (ya no crea filas de más)

Producto sin ProductoEmpresa todavía → el buscador lo sigue mostrando
  (con stock/precio en 0, sin romper la pantalla ni la búsqueda)

Producto con datos reales (stock 20, precio $150.000) → se sigue
  mostrando correctamente vía el nuevo método de solo lectura
```

`python manage.py check`: sin errores.

## Por qué antes "a veces" cargaba y "a veces" no
Esto explica también por qué el problema podía sentirse inconsistente:
mientras ningún producto necesitara crear su fila (porque ya se había
"tocado" antes por otra pantalla), todo iba rápido. El bloqueo aparecía
justo en el momento de escribir en el buscador con productos que
todavía no tenían disponibilidad creada para esa empresa — que es
además exactamente el escenario que reportaste.
