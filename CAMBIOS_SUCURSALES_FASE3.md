# Sucursales — Fase 3: compra desde la principal repartida a sucursales

## Flujo
1. En **Compras → Nueva compra** (empresa principal, usuario admin) aparece la tarjeta **Repartir a sucursales (opcional)**: por cada fila eliges producto de la compra, sucursal y cantidad.
2. **Guardar borrador:** el reparto se guarda con la compra; no mueve stock ni crea traslados. Al editar el borrador se recarga.
3. **Confirmar compra:** el stock entra completo a la principal, caja/cuenta por pagar quedan en la principal (como siempre), y cada reparto sale del stock de la principal y se convierte en un **traslado Pendiente**.
4. La sucursal entra (Inventario → Traslados → *Por recibir*) y **confirma** (el stock entra a su inventario con el costo de la compra) o **rechaza** (el stock vuelve a la principal).
5. El **detalle de la compra** muestra el reparto y el estado de cada traslado (Pendiente de confirmar / Recibido / Cancelado).

## Archivos
- `purchases/models.py` + `migrations/0002_comprareparto.py` (**aditiva**, tabla nueva): `CompraReparto` (compra, producto, sucursal destino, cantidad; único por compra+producto+sucursal). Se guarda por producto, no por ítem, para sobrevivir a la edición del borrador.
- `purchases/services.py`: `confirmar_compra` ahora lee el reparto guardado (o el parámetro `distribucion`), lo valida completo **antes** de tocar la BD y crea traslados pendientes en la misma transacción atómica.
- `inventory/services.py`: `solicitar_traslado` acepta `costo_unitario` (costo de la compra).
- `purchases/views.py`: `_guardar_repartos` (validación en backend), contexto del formulario y del detalle, mensaje tras confirmar.
- `templates/purchases/purchase_form.html`, `purchase_detail.html`, `static/js/purchase_reparto.js`.
- `purchases/tests_reparto.py`: 14 pruebas.

## Validaciones (backend)
- Solo el **admin de la empresa principal** puede repartir (otros roles no ven la tarjeta y, si fuerzan el POST, se rechaza).
- La sucursal debe ser de la empresa que compra (una sucursal de otro grupo se rechaza).
- El producto debe estar en la compra y **habilitado en la sucursal**; si no, se explica que hay que compartirlo primero.
- Lo repartido de un producto nunca supera lo comprado.
- Si algo falla al confirmar, se revierte **toda** la compra (inventario, caja, cuenta por pagar y traslados).
- Un usuario sin permiso que edita un borrador no borra el reparto existente.

## Decisiones tomadas
1. **Costo del traslado:** costo promedio ponderado de ese producto en la compra (antes del descuento general), no el costo promedio de la bodega.
2. **El reparto es de unidades:** lo no repartido se queda en la principal.
3. **Pago:** la compra se paga/queda por pagar completa en la principal; no se divide entre sucursales (eso sería contabilidad entre empresas, fuera de alcance).
4. `confirmar_compra` ahora recibe `usuario=request.user` desde la vista. Efecto lateral positivo: antes, si alguien confirmaba un borrador creado por otra persona, la validación de caja comparaba con el creador y podía fallar con "Solo puedes operar en tu propia caja".
5. `transferir_inventario` (traslado inmediato) queda en el código pero **ya no lo usa nadie**; se puede retirar en la fase 5.

## Limitación conocida (ya existía)
Si una validación falla al confirmar, la pantalla se recarga con el carrito vacío (el carrito se arma por JS). No lo cambié para no tocar el formulario más allá del reparto.

## Antes de usar
`python manage.py migrate` (crea la tabla `purchases_comprareparto`; no altera datos existentes). Cada sucursal necesita el módulo de inventario activo para confirmar.

## Validación
`check` y `makemigrations --check`: limpios. 107 pruebas de las apps: OK (14 nuevas de esta fase).

## Siguiente: Fase 4 — traslados manuales (varias líneas, entre sucursales y hacia la matriz) e historial con filtros
