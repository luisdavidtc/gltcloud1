# Contabilidad — Fase 1: arquitectura del módulo

## Objetivo de esta fase
Reemplazar la pantalla genérica "Próximamente" a la que llegaba Contabilidad
después del OTP por un Dashboard real y propio del módulo, con las 12
pantallas del plan contable ya "enganchadas" (cada una en su propia URL,
mostrando por ahora "Próximamente" mientras llega la Fase 2 con la lógica
contable real: asientos, plan de cuentas, impuestos, balances, cálculos).

**No se tocó el sistema OTP.** El flujo de código de verificación de
`security` sigue exactamente igual (mismos modelos, mismas vistas, mismo
`gate.html`, mismo JS). Solo se cambió a dónde apunta el `?next=` una vez
validado el código.

## App nueva: `accounting`
Completamente aislada, sin que ninguna otra app del ERP dependa de ella ni
viceversa (mismo criterio de arquitectura que `reports` o `purchases`):

- `accounting/apps.py` — configuración estándar de la app.
- `accounting/models.py` — **vacío a propósito**. El modelo de datos contable
  (Plan de cuentas, Asientos, Comprobantes, etc.) es la Fase 2.
- `accounting/permissions.py` — decorador propio `contabilidad_required`.
  No se reutilizó `accounts.decorators.role_required` para no tener que
  tocar ese archivo compartido por todo el ERP: el requerimiento pedía un
  mensaje distinto ("No tiene permisos para acceder al módulo.") y
  cambiarlo ahí habría afectado a Ventas, Inventario, Compras, etc.
- `accounting/tenant_utils.py` — mismo patrón multiempresa que el resto del
  proyecto (`request.empresa`), listo para cuando la Fase 2 empiece a
  filtrar datos contables por empresa.
- `accounting/views.py` — `dashboard` (grid de 12 tarjetas) y
  `en_desarrollo` (pantalla "Próximamente" genérica, parametrizada por
  código, propia de esta app).
- `accounting/urls.py` — `''` → dashboard, `'<slug:codigo>/'` → próximamente.
- `templates/accounting/dashboard.html` y `templates/accounting/en_desarrollo.html`
  — mismo lenguaje visual del ERP (tarjetas `shadow-sm border-0`, íconos
  Bootstrap Icons en círculo de color, badge `erp-badge-soon-lg`, mismos
  botones `btn-outline-primary`).

## Seguridad de cada vista
Misma cadena de decoradores que ya usa el resto de módulos del ERP
(ver `purchases/views.py`), más el propio de Contabilidad:

```
@login_required
@contabilidad_required          # rol Administrador o Contador
@requiere_modulo('contabilidad') # empresa con el módulo contratado
@requiere_acceso_seguro('contabilidad') # refuerzo del OTP por URL directa
```

Los demás roles (vendedor, técnico, cajero, etc.) reciben el mensaje
"No tiene permisos para acceder al módulo." y nunca ven el ítem en el
sidebar.

## Archivos existentes modificados (mínimo indispensable)

| Archivo | Cambio |
|---|---|
| `erp_config/settings.py` | Se agregó `'accounting'` a `INSTALLED_APPS`. |
| `erp_config/urls.py` | Se agregó `path('contabilidad/', include('accounting.urls'))`. |
| `templates/base.html` | Bloque de Contabilidad del sidebar: ahora también lo ve el rol Contador (antes solo Administrador), se quitó el badge "Próximamente", y el `next=` del enlace de OTP ahora apunta a `accounting:dashboard` en vez de `core:en_desarrollo`. |

**Cero cambios** en `sales`, `inventory`, `clients`, `providers`,
`cashregister`, `repairs`, `purchases` ni `security` (modelos, vistas, urls
o templates).

## Pruebas realizadas
- `python manage.py check` — sin errores.
- `python manage.py makemigrations --check` — Contabilidad no genera
  migraciones (no tiene modelos aún); el resto del proyecto no tuvo
  cambios de esquema por esta entrega.
- Flujo completo simulado con el test client de Django, con una empresa de
  prueba y tres usuarios (`admin`, `contador`, `vendedor`):
  - **Vendedor** → `403 Forbidden` al entrar a `/contabilidad/` (no ve el
    ítem en el sidebar).
  - **Contador** → exento de OTP (regla ya existente de `security`), entra
    directo al Dashboard con las 12 tarjetas.
  - **Administrador** → redirigido al `gate` de OTP; tras enviar y validar
    el código (flujo real, con el email de `security` generándose
    correctamente), llega al Dashboard.
  - Cada una de las 12 tarjetas abre su pantalla "Próximamente" propia.
  - URL con código inventado (`/contabilidad/no-existe/`) → `404`.
  - Se confirmó que Ventas, Inventario, Clientes, Proveedores, Compras,
    Servicio Técnico y Reportes siguen respondiendo igual que antes (mismos
    controles de módulo activo, sin errores de plantilla) tras el cambio en
    `base.html`.

## Siguiente fase (no incluida aquí)
Modelo de datos contable, Plan de cuentas, asientos automáticos desde
Ventas/Compras/Caja, impuestos, y el cálculo real de cada uno de los 12
libros/estados.
