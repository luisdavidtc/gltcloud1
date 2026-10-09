# Sucursales — Fase 2: traslados con confirmación

## Flujo
1. **Solicitar** (admin de la matriz, Inventario → Traslados entre sucursales → Nuevo traslado): el stock **sale de la matriz de inmediato** y queda *en tránsito*; el traslado queda **Pendiente**.
2. **La sucursal** entra (pestaña *Por recibir*) y:
   - **Confirma** → el stock entra a la sucursal (costo promedio ponderado recalculado) y el traslado pasa a **Completada**.
   - **Rechaza** (motivo obligatorio) → el stock **vuelve a la matriz** y queda **Cancelada**.
3. **La matriz puede cancelar** mientras siga pendiente → el stock vuelve a su inventario.

Cada resolución guarda quién y cuándo. Una vez resuelto, no se puede volver a procesar (protege contra doble clic o dos pestañas).

## Archivos
- `inventory/models.py` + `migrations/0009_transferencia_confirmacion.py` (**aditiva**): `resuelta_por`, `fecha_resolucion`, `motivo_rechazo` en `TransferenciaInventario`.
- `inventory/services.py`: `solicitar_traslado`, `confirmar_recepcion`, `rechazar_recepcion`, `cancelar_traslado`, `registrar_reintegro_inventario` (devuelve stock sin tocar costos). Todo atómico y con bloqueo de la fila.
- `inventory/views_traslados.py`, `inventory/urls.py`, `templates/inventory/traslado_list.html`, `traslado_form.html`.
- `templates/base.html`: enlace "Traslados entre sucursales" activo.
- `company/views.py` + `templates/company/sucursales.html`: contador "Traslados por recibir" en cada tarjeta de sucursal.
- `inventory/tests_traslados.py`: 16 pruebas.

## Permisos (validados en backend)
| Acción | Quién |
|---|---|
| Solicitar / cancelar | Admin de la empresa principal, desde la propia matriz |
| Confirmar / rechazar | Empresa activa = destino, con rol admin, inventario, compras o gerente (el dueño puede hacerlo entrando a la sucursal) |
| Ver | Solo empresas involucradas en el traslado (404 para las demás) |

Las acciones que modifican datos son solo POST.

## Decisiones tomadas
1. **Stock en tránsito:** se descuenta al solicitar (no al confirmar), para que la matriz no pueda vender o trasladar dos veces la misma mercancía.
2. **Costo del traslado:** costo promedio vigente de la matriz al momento de solicitar.
3. **Solo matriz → sus sucursales** en esta fase (sucursal → matriz y entre sucursales quedan para la fase 4). El producto debe estar habilitado en la sucursal (regla ya existente).
4. **Formulario simple** de un producto por traslado, para poder usar el flujo completo ya; la versión con varias líneas y la compra repartida vienen en las fases 3 y 4.
5. `transferir_inventario` (inmediato) **se conserva sin cambios** porque `confirmar_compra(distribucion=...)` aún lo usa; la fase 3 lo reemplaza por traslados pendientes.

## Antes de usar
Ejecuta `python manage.py migrate` (solo agrega 3 columnas a `inventory_transferenciainventario`; los traslados existentes no cambian).

## Validación
- `makemigrations --check`: sin cambios pendientes. `check`: sin errores.
- 93 pruebas de las apps: OK (16 nuevas de traslados + 11 de la fase 1).

## Siguiente: Fase 3 — compra desde la principal repartida a sucursales
