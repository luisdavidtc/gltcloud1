# Sucursales — Fase 1: entrar a las sucursales desde Configuración

## Qué se puede hacer ahora
- **Configuración → Sucursales** (`/configuracion/sucursales/`): el dueño (rol *admin* de la empresa matriz) ve sus sucursales con tarjetas de resumen (ventas de hoy, inventario, compras del mes) y el botón **Entrar a la sucursal**.
- Dentro de la sucursal ve **sus** ventas, inventario, compras, caja, reportes, etc. (todo ya se filtra por `request.empresa`).
- Un **banner** permanente indica "Estás viendo X" con el botón **Volver a la principal**.

## Archivos tocados
- `accounts/models.py`: `sucursales_gestionadas`, `gestiona_sucursal()`, `empresas_para_login`; `empresas_accesibles` ahora incluye las sucursales gestionadas.
- `accounts/views.py`: el selector de empresa del login usa `empresas_para_login` (el dueño sigue iniciando siempre en su principal, sin pregunta extra).
- `tenants/middleware.py`: "Caso C" — autoriza al admin de la matriz para sus sucursales sin `EmpresaAcceso`.
- `tenants/views.py`: `cambiar_empresa_activa` acepta `next` (solo rutas del mismo sitio).
- `company/views.py`, `company/urls.py`, `templates/company/sucursales.html`: nueva pantalla.
- `templates/base.html`: enlace del menú activo (sin "Próximamente") y banner.
- `tenants/tests.py` (ajuste de 1 prueba), `tenants/tests_sucursales.py` (11 pruebas nuevas).

## Decisiones tomadas
1. **Quién entra sin `EmpresaAcceso`:** solo un usuario con rol global *admin* cuya empresa es la matriz (`Empresa.empresa_principal`) y únicamente a *sus* sucursales. Nunca a empresas de otro grupo. Si existe un `EmpresaAcceso.rol` explícito, ese rol manda; si no, es admin.
2. **Login sin cambios:** las sucursales gestionadas no disparan el selector de empresa al iniciar sesión.
3. **Reportes y gestión de accesos de usuarios** (`empresas_accesibles`) ahora también incluyen las sucursales del dueño; es consecuencia directa de la decisión 1.
4. La pantalla se arma desde la empresa propia del usuario, no desde la activa, para que siga funcionando estando dentro de una sucursal.
5. No hay migraciones en esta fase.

## Cambio de comportamiento a tener en cuenta
La prueba `test_f_empresa_no_autorizada_en_el_selector_es_rechazada` usaba Medellín como empresa "sin autorización" para el admin de la principal; ahora esa sucursal sí le pertenece, así que la prueba usa una empresa ajena al grupo.

## Requisitos para que una sucursal funcione
Debe tener los módulos activos (Superadministrador → módulos por empresa) y suscripción vigente; si no, el middleware la bloquea como a cualquier empresa.

## Validación
- `manage.py check`: sin errores.
- 77 pruebas de las apps del proyecto: OK (incluye las 11 nuevas).
- Nota: `manage.py test` sin argumentos falla al crear la BD de pruebas; probablemente por los scripts sueltos `test_correo_aislado.py` / `test_pos_api_aislado.py` de la raíz (ya existían). Se corrió por apps.

## Siguiente: Fase 2 — traslados con confirmación
