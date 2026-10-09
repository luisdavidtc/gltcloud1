# Mejoras funcionales de Ventas + corrección de layout global

## 0. Corrección de layout (hamburguesa tapando el título)

**Causa real:** `.sidebar-toggle` tenía `position: fixed`, lo que lo sacaba
del flujo normal del `.erp-navbar`. El título ocupaba ese espacio y el
botón fijo quedaba flotando encima, tapándolo — en todas las páginas.

**Archivos:** `static/css/styles.css`, `templates/base.html`

- El botón vuelve a vivir en el flujo normal del navbar (ya no es `fixed`).
- `.erp-navbar` ahora es `position: sticky; top: 0;` con su propio
  `z-index` (1030, por debajo del sidebar 1040 y el backdrop 1035), así
  el botón sigue siempre visible al hacer scroll sin taparse a sí mismo.
- Nueva clase `.erp-navbar-toggle-group` con `gap: 20px` (antes usaba
  `gap-3` de Bootstrap = 16px) para la separación mínima pedida.
- Es un cambio estructural en `base.html`/`styles.css`: aplica a **todas**
  las páginas del ERP automáticamente, sin tocar el responsive.

## 1. IVA incluido en el precio de venta

**Archivos:** `sales/models.py`, `sales/views.py`, `sales/forms.py`,
`sales/migrations/0009_saleitem_iva_porcentaje.py`,
`sales/migrations/0010_sale_metodo_pago_credito.py`,
`static/js/sale_form.js`, `templates/sales/sale_form.html`,
`templates/sales/sale_detail.html`, `templates/sales/sale_print.html`

- Se conecta `Product.tipo_iva_venta` / `impuesto_venta_porcentaje` (ya
  existía en Inventario, no se usaba en Ventas) al POS: cada
  `SaleItem` guarda su propio `iva_porcentaje` (0 si el producto es
  Excluido/Exento) al momento de agregarlo a la venta.
- `Sale.recalcular()` ya **no suma** el IVA sobre el subtotal. El total
  siempre es `subtotal - descuento` (el valor realmente vendido). El
  IVA se desglosa hacia adentro del precio solo para efectos
  tributarios/informativos (`Sale.iva_valor`, `Sale.iva_porcentaje`
  ahora es un promedio ponderado, ya no editable a mano).
- Probado con el ejemplo exacto del pedido: precio $35.000, IVA 19% →
  base $29.411,76 / IVA $5.588,24 / total $35.000 (nunca $41.650).
- También probado con productos mixtos (uno Gravado + uno Excluido en
  la misma venta): cada uno respeta su propia tarifa.

## 2. Modal de cliente (buscar + crear sin salir del POS)

**Archivos:** `clients/models.py`, `clients/forms.py`, `clients/views.py`,
`clients/urls.py`, `clients/migrations/0005_client_datos_colombia_y_cupo.py`,
`templates/sales/sale_form.html`, `static/js/sale_form.js`,
`static/css/pos.css`

- El botón "+" abre un modal Bootstrap (ya no navega a otra página).
- Nuevos campos en `Client`: tipo de persona (Natural/Jurídica), tipo
  de identificación (los 8 oficiales de Colombia), celular, ciudad,
  observaciones, y cupo de crédito (`limite_credito`/`saldo_utilizado`).
- `apellido` pasa a ser opcional: en Persona Jurídica el nombre
  completo va en "Nombre o Razón Social" y el apellido queda vacío
  (según lo que confirmaste).
- Guardado 100% AJAX (`clients:client_create_ajax`): crea el cliente,
  cierra el modal, lo selecciona automáticamente en la venta y muestra
  un toast de éxito — sin recargar la página.
- Buscador en vivo de clientes existentes (`clients:client_modal_list`)
  con botón "Seleccionar" por fila.

## 3. Ganancia eliminada del POS

**Archivos:** `templates/sales/sale_form.html`, `static/js/sale_form.js`

- Se quitó por completo la fila "Ganancia" del resumen del cajero: HTML,
  cálculo en JS y el espacio que ocupaba.
- El dato administrativo sigue existiendo en el modelo (`Sale.ganancia`)
  y se sigue mostrando en `sale_list.html`/`sale_detail.html` (vistas de
  back-office, no en el POS).

## 4-6. Modal "Confirmar Venta" + atajos de teclado

**Archivos:** `templates/sales/sale_form.html`, `static/js/sale_form.js`,
`sales/views.py` (validación de cupo de crédito), `static/css/pos.css`

- El botón "Confirmar venta" ya no envía el formulario directo: abre el
  modal con total, cantidad de productos, cliente y observaciones.
- 7 métodos de pago como botones grandes (Efectivo, Tarjeta Débito,
  Tarjeta Crédito, Transferencia, Nequi, Daviplata, Crédito), con
  resaltado visual al seleccionar.
- Efectivo → campo "Valor recibido" con cambio calculado en tiempo real.
  Transferencia/Nequi/Daviplata → sin campo de recibido, solo confirmar.
  Crédito → valida cupo disponible del cliente (`Client.tiene_cupo`) y
  muestra un mensaje claro si no alcanza (tanto en el navegador como en
  el servidor, que es la fuente de verdad final).
- "Finalizar Venta (F9)" guarda la venta, actualiza inventario, registra
  el movimiento de caja, e incrementa/revierte el saldo de crédito del
  cliente si aplica (ver `sale_create`/`sale_void`), cierra el modal y
  muestra el toast "Venta registrada correctamente."
- Atajos: F2 buscar producto, F3 cliente, F4 código, F9 abre/confirma el
  modal, Esc lo cierra (nativo de Bootstrap), Enter confirma dentro de él.

## Migraciones nuevas (aplicar con `python manage.py migrate`)

- `clients.0005_client_datos_colombia_y_cupo`
- `sales.0009_saleitem_iva_porcentaje`
- `sales.0010_sale_metodo_pago_credito`

Todas son aditivas (no borran ni renombran datos existentes) y ya se
probaron corriendo `migrate` contra una base nueva sin errores.

## Verificaciones hechas antes de esta entrega

- `python manage.py check` → sin errores.
- Migraciones aplicadas de cero (`migrate` completo) → sin errores.
- Simulación en `shell` de una venta con productos Gravado + Excluido
  mezclados → total correcto, sin doble cobro de IVA.
- Simulación del ejemplo exacto del pedido (35.000 con IVA 19%) →
  coincide con las cifras que diste (base 29.411,76 / IVA 5.588,24).
- Prueba de `Client.cupo_disponible` / `tiene_cupo()`.
- `node --check` sobre `sale_form.js` (sin errores de sintaxis).
- Balance de tags Django (`{% block %}`, `{% if %}`, `{% for %}`) y de
  `<div>` en `sale_form.html`.

## Pendiente de tu lado (no lo hice porque necesita datos reales)

- Probar el flujo completo en tu entorno con el sidebar/caja real
  (yo solo pude simular con `manage.py shell`, no levanté el server
  completo con sesión de caja abierta).
- Revisar visualmente el modal de "Nuevo cliente" y "Confirmar Venta"
  en tu navegador para validar que el estilo case perfecto con el resto
  del ERP (coloqué los mismos tokens de color/sombra/radio que ya usas,
  pero vale la pena que le eches un ojo).
