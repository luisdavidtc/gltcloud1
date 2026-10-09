# Módulo de Sucursales — entrega final (fases 1 a 5)

## Qué hace
Como dueño (admin de la empresa principal) puedes entrar a cada sucursal para ver y operar sus ventas, inventario, compras y demás; comprar desde la principal repartiendo a las sucursales; y mover mercancía entre empresas del grupo, siempre con **confirmación** de quien la recibe.

## Cómo usarlo (paso a paso)
1. **Vincular sucursales** (una sola vez, Superadministrador → Empresas → editar): en la sucursal, campo *Empresa principal* = tu empresa. Activa los módulos que necesite (Inventario, Compras…) y suscripción vigente.
2. **Compartir productos** con cada sucursal (Inventario → editar producto), para que puedan recibir stock.
3. **Entrar:** Configuración → Sucursales → *Entrar a la sucursal*. Un banner te recuerda dónde estás y tiene *Volver a la principal*.
4. **Comprar y repartir:** Compras → Nueva compra → tarjeta *Repartir a sucursales*. Al confirmar, lo repartido queda como traslado pendiente.
5. **Recibir:** en la sucursal, Inventario → Traslados → *Por recibir* → Confirmar / Rechazar (con motivo). Si es un lote, *Confirmar todo*.
6. **Traslados manuales:** Inventario → Traslados → Nuevo traslado (varias líneas, hacia la principal, una sucursal o entre sucursales). Historial con filtros en la pestaña *Historial*.

## Migraciones (aplicar en orden con `python manage.py migrate`)
- `inventory.0009_transferencia_confirmacion` — 3 columnas nuevas (quién/cuándo resolvió, motivo).
- `inventory.0010_transferencia_lote` — 1 columna nueva (lote).
- `purchases.0002_comprareparto` — tabla nueva.
Todas son aditivas. **Probadas sobre una copia de tu `db.sqlite3`**: se aplican sin errores y los conteos de empresas, usuarios, compras y productos por empresa no cambian.

## Reglas de seguridad (todas en backend)
| Qué | Quién |
|---|---|
| Entrar a una sucursal sin acceso explícito | Admin de la matriz, solo a sus sucursales |
| Enviar / cancelar traslados | Admin o inventario de la empresa origen (activa) |
| Confirmar / rechazar | Empresa activa = destino; admin, inventario, compras o gerente |
| Repartir una compra | Admin de la empresa principal |
| Ver un traslado | Solo las dos empresas involucradas |
Acciones que cambian datos: solo POST. Nada cruza grupos de empresas.

## Garantías de consistencia
- Stock "en tránsito": sale del origen al enviar y entra al destino solo al confirmar; si se rechaza o cancela, vuelve al origen.
- Una vez resuelto, un traslado no se puede procesar de nuevo (doble clic / dos pestañas).
- Envíos de varias líneas y compras repartidas son atómicos: todo o nada.
- Prueba integral que verifica, paso a paso, que el stock total del grupo (stock + tránsito) nunca cambia salvo por compras. Verifiqué que la prueba **falla** si se rompe el reintegro de stock a propósito.

## Cambios de comportamiento a tener en cuenta
- `empresas_accesibles` incluye ahora las sucursales del admin de la matriz (reportes y gestión de accesos las ven).
- El login sigue iniciando en la empresa propia (no pregunta por sucursales).
- `purchase_create` pasa el usuario que confirma; corrige un error previo al confirmar un borrador creado por otra persona (caja ajena).
- Se **retiró** `inventory.services.transferir_inventario` (traslado inmediato): ya nadie lo usaba.
- Se ajustó 1 prueba antigua (Medellín ya no sirve de "empresa sin autorización").

## Mapa de archivos
- **Acceso/sucursales:** `accounts/models.py`, `accounts/views.py`, `tenants/middleware.py`, `tenants/views.py`, `company/{views,urls}.py`, `templates/company/sucursales.html`, `templates/base.html`.
- **Traslados:** `inventory/{models,services,views_traslados,urls}.py`, `templates/inventory/traslado_{list,form}.html`, `static/js/traslado_form.js`.
- **Compras:** `purchases/{models,services,views}.py`, `templates/purchases/purchase_{form,detail}.html`, `static/js/purchase_reparto.js`.
- **Pruebas nuevas (64):** `tenants/tests_sucursales.py` (11), `inventory/tests_traslados.py` (16), `purchases/tests_reparto.py` (14), `inventory/tests_traslados_f4.py` (21), `tenants/tests_sucursales_e2e.py` (2).
- Detalle por fase: `CAMBIOS_SUCURSALES_FASE1.md` … `FASE4.md`.

## Validación final
`check` y `makemigrations --check` limpios · **130 pruebas** de las apps: OK (66 existentes + 64 nuevas) · humo con tus datos reales (copia): Sucursales, Traslados, Compras y Dashboard responden 200 para los dos administradores.

## Limitaciones conocidas / ideas futuras
- Tu base actual tiene 2 empresas independientes (CONECT ACCESORIOS y AFAR SAS) sin vínculo de sucursal; hasta que vincules una, la pantalla de Sucursales aparecerá vacía.
- El selector de producto en traslados y reparto es una lista simple (sin buscador) — conviene un buscador con catálogos grandes.
- Si falla una validación al confirmar una compra, el formulario recarga con el carrito vacío (comportamiento previo del formulario).
- No hay notificación automática (correo/aviso) a la sucursal cuando llega un traslado; solo el contador en la tarjeta y la bandeja.
- Sin pagos/contabilidad entre empresas: la compra se paga completa en la principal.
- `python manage.py test` sin argumentos falla por los scripts sueltos `test_*_aislado.py` de la raíz (ya existían); usa la lista de apps.
