# Rediseño de Remisiones (estilo POS con grid de productos)

## Pregunta del usuario: ¿es posible? → Sí, y ya está implementado.

## Archivos nuevos
- `static/css/pos.css` — todo el estilo visual del nuevo layout (topbar, grid de
  productos, tabs de categoría, paginación, cliente, carrito, resumen).
- `static/img/producto-generico.png` — el logo de GLT Cloud que subiste, recortado
  y cuadrado, usado como imagen de respaldo en productos sin foto.
- `static/img/glt-logo.png` — guardé también el logo completo tal cual lo
  subiste, por si más adelante lo quieres usar en el sidebar o el login.

## Archivos modificados
1. **`templates/sales/sale_form.html`** — reescrito completo: topbar tipo POS,
   buscador, accesos rápidos, tabs de categoría, grid de productos, panel de
   cliente, carrito y resumen — con el mismo `<form>`, mismos `name=` de los
   inputs y mismo flujo de guardado que ya tenías.
2. **`static/js/sale_form.js`** — se agregó (sin borrar la lógica de cálculo
   existente):
   - Carga de la grilla de productos por categoría + paginación (8 por página,
     como en tu referencia).
   - Reutiliza exactamente `agregarProducto()` de siempre al hacer clic en una
     card — mismo carrito, mismo cálculo de totales.
   - Stepper +/- de cantidad (dispara el mismo evento `input` que ya existía).
   - Atajos de teclado: **F2** buscar, **F3** cliente, **F4** código, **F9**
     facturar, **F10** limpiar carrito, **Ctrl+S** guardar.
   - Se quitó el dropdown de autocompletado del buscador principal (ya no hace
     falta: ahora la grilla se filtra en vivo) — el escaneo de código de barras
     con Enter sigue funcionando igual que antes.
3. **`sales/views.py`** (backend, con tu autorización):
   - `product_search`: ahora acepta `categoria`, `page` y `por_pagina`
     (opcionales) y devuelve además `imagen`, `categoria_id`,
     `categoria_nombre` y datos de paginación. **Totalmente compatible hacia
     atrás**: si se llama solo con `?q=`, se comporta exactamente igual que
     antes.
   - `sale_create`: se agregó `categorias` al contexto (para las pestañas). No
     se tocó nada de la lógica de guardado de la venta (POST) ni de
     validaciones de stock/caja.

## Sobre los productos sin foto
Como pediste: cualquier producto cuyo campo `imagen` esté vacío usa
automáticamente el logo de GLT Cloud (recortado y cuadrado) tanto en la
grilla como en el carrito. En cuanto subas fotos reales a un producto (campo
`imagen` que ya existía en tu modelo), esas se muestran en su lugar sin que
tengas que cambiar nada más.

## Lo que NO se tocó
- El modelo `Product` (el campo `imagen` y `categoria` ya existían).
- Ninguna URL, ni el formulario `SaleForm`, ni la validación de stock/caja, ni
  cómo se guarda la venta.
- La edición manual de precio y descuento por producto en el carrito: la dejé
  visible y editable (como ya funcionaba), solo la hice más compacta — así no
  se pierde ninguna capacidad que ya tenías.

## Nota
"Facturación electrónica" queda con el mismo look una vez la actives (hereda
los mismos estilos `.erp-card`, `.erp-pos-*`, etc. de `pos.css` y
`design-system.css`), tal como pediste.
