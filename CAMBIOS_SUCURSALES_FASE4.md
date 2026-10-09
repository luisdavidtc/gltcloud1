# Sucursales — Fase 4: traslados manuales, lotes e historial con filtros

## Qué cambia
- **Traslado manual de varias líneas** (Inventario → Traslados → Nuevo traslado): eliges la empresa destino y agregas todos los productos que quieras. Es **todo o nada**: si una línea falla (stock, producto no habilitado en el destino…), no se envía ninguna y las líneas escritas no se pierden.
- **Cualquier dirección dentro del grupo:** matriz → sucursal, **sucursal → matriz** y **sucursal → sucursal**. Nunca hacia empresas de otro grupo.
- **Lotes:** las líneas de un mismo envío comparten un código (8 caracteres). En la bandeja aparece una tarjeta por lote con varias líneas pendientes: **Confirmar todo / Rechazar todo** (destino) o **Cancelar lote** (origen). También se puede seguir actuando línea por línea; "todo el lote" solo procesa lo que siga pendiente.
- **Historial con filtros:** producto (nombre o código), empresa, estado y rango de fechas, con paginación que conserva los filtros. Pestañas: Por recibir · Enviados · Historial.

## Archivos
- `inventory/models.py` + `migrations/0010_transferencia_lote.py` (**aditiva**): campo `lote` (UUID, nulo) y `lote_corto`.
- `inventory/services.py`: `grupo_de`, `mismo_grupo`; `solicitar_traslado` ahora valida "mismo grupo" en vez de "matriz → su sucursal"; `solicitar_traslado_multiple`, `confirmar_lote`, `rechazar_lote`, `cancelar_lote`.
- `inventory/views_traslados.py`, `inventory/urls.py` (3 rutas de lote), `templates/inventory/traslado_list.html`, `traslado_form.html`, `static/js/traslado_form.js`.
- Pruebas: `inventory/tests_traslados_f4.py` (21 nuevas) y ajuste de 3 pruebas de la fase 2.

## Permisos (validados en backend)
| Acción | Quién |
|---|---|
| Enviar / cancelar | Rol **admin o inventario** de la empresa origen (la empresa activa) |
| Confirmar / rechazar | Empresa activa = destino, con rol admin, inventario, compras o gerente |
| Ver | Solo las dos empresas involucradas |

Todas las acciones que modifican datos son POST. Un lote ajeno responde "no hay traslados pendientes para tu empresa" sin cambiar nada.

## Decisiones tomadas (cambian una de la fase 2)
1. **Quién puede enviar:** en la fase 2 solo el admin de la matriz; ahora también admin/inventario de cada sucursal, **desde su propia empresa**. Un vendedor sigue sin poder. Si prefieres que las sucursales no envíen, basta dejar `ROLES_ENVIO` solo para la matriz (un cambio de una línea más una condición en la vista).
2. **Productos ofrecidos:** solo los que la empresa origen tiene activos y con stock; el destino debe tenerlos habilitados (regla existente).
3. **Costo:** el costo promedio de la empresa origen al enviar (igual que en fase 2).
4. **Los traslados anteriores** no tienen lote: siguen funcionando línea por línea.
5. **Selector de producto simple** (lista desplegable con stock). Con catálogos muy grandes convendría un buscador; no lo incluí para no alargar la fase.

## Antes de usar
`python manage.py migrate` (agrega 1 columna nula; no altera traslados existentes).

## Validación
`check` y `makemigrations --check`: limpios. **128 pruebas** de las apps: OK (21 nuevas).

## Siguiente: Fase 5 — pruebas integrales, retiro de código sin uso (`transferir_inventario`) y entrega final
