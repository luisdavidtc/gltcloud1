# Núcleo multiempresa/multisucursal — Resumen exacto de la entrega

Se suma DESPUÉS de todas las entregas anteriores (2FA removido, Fase L,
Fase M, Fase N parcial, Fase Ñ). No toca nada de catálogo maestro
(`ProductoEmpresa`, transferencias, etc.) — tal como pediste, esta
entrega es solo el núcleo multiempresa/login/roles.

## 1. Auditoría — qué ya existía y NO se duplicó

| Buscado | Estado antes de esta entrega |
|---|---|
| `EmpresaAcceso` | Ya existía (usuario, empresa, otorgado_por, fecha) — se **amplió**, no se duplicó |
| `empresas_accesibles` | Ya existía en `CustomUser` — se ajustó para respetar `activo` |
| `empresa_activa_id` en sesión | Ya existía y funcionaba |
| `cambiar_empresa_activa` | Ya existía (vista + URL + botón en navbar) |
| `EmpresaMiddleware` | Ya existía resolviendo `request.empresa` desde sesión — se **amplió**, no se reescribió desde cero |
| `es_principal` | Ya existía en `Empresa` |
| `empresa_principal` (agrupación matriz→sucursales) | **No existía** — se creó |
| Login con empresa (NIT/correo) | **No existía** — solo pedía usuario+contraseña |
| Rol por empresa | **No existía** |
| Modo soporte funcional | El modelo `AccesoSoporte` existía pero **nadie lo usaba** — no había vistas |

## 2. Archivos modificados

- `tenants/models.py` — `Empresa.empresa_principal` (FK a sí misma), `Empresa.es_matriz`, `Empresa.grupo_empresarial`; `EmpresaAcceso.activo`, `EmpresaAcceso.rol`.
- `tenants/middleware.py` — `request.rol_en_empresa`; `_resguardar_superadmin` ahora respeta el modo soporte (antes solo confinaba al Superadmin a `/superadmin/` sin excepción).
- `tenants/views.py` — sin cambios en esta entrega (ya tenía `cambiar_empresa_activa` de la Fase L).
- `accounts/models.py` — `empresas_accesibles` ahora filtra `activo=True`; método nuevo `rol_en(empresa)`.
- `accounts/views.py` — `login_view` reescrito: Empresa (NIT/correo) + Usuario + Contraseña, con las 6 validaciones en el orden pedido y mensaje de error siempre genérico.
- `accounts/forms.py` — `LoginForm` con el campo `empresa` nuevo.
- `accounts/decorators.py` — `role_required`, `admin_required`, `RoleRequiredMixin`, `AdminRequiredMixin`: **misma firma pública**, ahora leen `request.rol_en_empresa` (con fallback a `request.user.role` si el middleware no corrió, ej. en tests que arman el request a mano).
- `platform_admin/views.py` — 2 vistas nuevas: `soporte_entrar`, `soporte_salir`.
- `platform_admin/forms.py` — `EmpresaForm` ahora incluye `empresa_principal` (con validación: no se puede encadenar sucursal-de-sucursal).
- `platform_admin/urls.py` — 2 rutas nuevas.
- `dashboard/views.py` — **bug real que encontré y corregí**: el dashboard redirigía SIEMPRE al Superadmin a `/superadmin/`, sin excepción — eso rompía el modo soporte recién construido (lo detectó la prueba P, no lo asumí). Ahora respeta `request.modo_soporte`.
- `templates/accounts/login.html` — campo Empresa agregado.
- `templates/base.html` — banner "Modo soporte" + botón "Salir" cuando `request.modo_soporte` es `True`.
- `templates/platform_admin/empresa_detail.html` — botón "Entrar en modo soporte".
- `templates/platform_admin/soporte_entrar.html` — nuevo, formulario de motivo.

## 3. Modelos creados/modificados

- `Empresa.empresa_principal` (nuevo campo, self-FK)
- `Empresa.es_matriz`, `Empresa.grupo_empresarial` (properties nuevas)
- `EmpresaAcceso.activo` (nuevo campo)
- `EmpresaAcceso.rol` (nuevo campo)

## 4. Migraciones creadas

- `tenants/migrations/0006_empresa_empresa_principal_empresaacceso_activo_and_more.py` — solo `AddField` (3 campos), 100% aditiva, sin backfill necesario (los defaults son seguros: `activo=True` para accesos ya existentes, `rol=''`/`empresa_principal=None` no rompen nada).

## 5. Vistas creadas/modificadas

- `accounts.login_view` — reescrita.
- `platform_admin.soporte_entrar` — nueva.
- `platform_admin.soporte_salir` — nueva.
- `dashboard.index` — 1 línea corregida (bug del modo soporte).

## 6. URLs creadas

- `platform_admin:soporte_entrar` (`/superadmin/empresas/<pk>/soporte/entrar/`)
- `platform_admin:soporte_salir` (`/superadmin/soporte/salir/`)

## 7. Pruebas ejecutadas — resultado real

Archivo `tenants/tests.py` (nuevo), corrido con `manage.py test`, **19/19 pasan**:

```
test_a_login_correcto_con_nit ... ok
test_b_login_correcto_con_correo ... ok
test_c_nit_inexistente ... ok
test_d_correo_inexistente ... ok
test_e_usuario_sin_acceso_a_esa_empresa ... ok
test_f_password_incorrecta ... ok
test_g_empresa_suspendida ... ok
test_h_usuario_inactivo ... ok
test_i_usuario_con_acceso_a_dos_empresas_puede_entrar_por_cualquiera ... ok
test_j_login_en_empresa_a_ve_datos_de_a ... ok
test_k_cambio_a_empresa_b_ve_datos_de_b ... ok
test_l_no_accede_a_cliente_de_otra_empresa_por_url_manipulada ... ok
test_l2_404_real_por_aislamiento_de_empresa_con_rol_que_si_alcanza ... ok
test_no_puede_cambiar_a_empresa_sin_acceso_ni_por_post_directo ... ok  (bonus, no listado A-Q pero relevante)
test_m_una_sola_empresa_no_muestra_selector ... ok
test_n_varias_empresas_muestra_selector ... ok
test_o_superadmin_entra_sin_empresa ... ok
test_p_superadmin_puede_entrar_en_modo_soporte ... ok
test_q_superadmin_puede_salir_del_modo_soporte ... ok

Ran 19 tests in 39.6s — OK
```

También corrí el suite completo del proyecto (`accounts sales repairs inventory clients dashboard tenants`): nada se rompió (las demás apps no tenían tests reales, solo estos 19 existen).

**Nota honesta sobre el test L**: el pedido acepta explícitamente "404 o 403 según el patrón existente". En mi escenario de prueba dio 403 (el rol de ese usuario en esa empresa no alcanza para editar clientes — el chequeo de rol-por-empresa actuó primero). Agregué `test_l2` aparte, con un usuario cuyo rol SÍ alcanza, para confirmar también el 404 real por aislamiento de datos (`get_object_or_404` filtrado por empresa). Los dos mecanismos de defensa quedaron probados por separado.

## 8. `manage.py check` / `makemigrations --check` / `migrate`

- `check` → sin errores.
- `makemigrations --check --dry-run` → sin cambios pendientes.
- `migrate` sobre base SQLite nueva, de punta a punta → sin errores (log completo verificado).

## 9. Qué quedó funcional (los 14 puntos del criterio de finalización)

| # | Criterio | Estado |
|---|---|---|
| 1 | Crear Empresa Principal | ✅ (ya existía, `es_principal`) |
| 2 | Crear sucursal | ✅ (ya existía el CRUD de empresas) |
| 3 | Vincularla a la principal | ✅ **nuevo** (`empresa_principal` + selector en `EmpresaForm`) |
| 4 | Crear/asignar usuario a ambas | ✅ (ya existía `user_update` con checkboxes de `EmpresaAcceso`) |
| 5 | Login con NIT/correo + usuario + contraseña | ✅ **nuevo**, probado (tests A-H) |
| 6 | Entrar inicialmente a la empresa indicada en el login | ✅ probado (test A/B) |
| 7 | Cambiar de empresa desde el navbar | ✅ (ya existía, Fase L) |
| 8 | Datos cambian según empresa activa | ✅ probado (test J/K) |
| 9 | Permisos cambian según rol de esa empresa | ✅ **nuevo** (`rol_en_empresa`), probado indirectamente en test L (bloqueó por rol) |
| 10 | No acceder a información de otra empresa | ✅ probado (test L, L2, y el de cambiar-empresa-sin-acceso) |
| 11 | Superadministrador sigue funcionando | ✅ probado (test O) |
| 12 | Usuarios y datos actuales siguen funcionando | ✅ (migración 100% aditiva, sin backfill destructivo) |
| 13 | Migraciones aplicadas correctamente | ✅ verificado con `migrate` real |
| 14 | Pruebas principales pasan | ✅ 19/19 |

## 10. Qué NO se implementó en esta entrega (honesto, tal como pediste)

- **UI del rol-por-empresa en `user_update`**: el campo `EmpresaAcceso.rol` existe y funciona (probado), pero la pantalla de Usuarios todavía no tiene un `<select>` para elegirlo por cada empresa marcada — hoy solo se puede asignar por shell/admin de Django. Es una pantalla, no lógica de negocio faltante.
- **Vista para desvincular una sucursal de su matriz o ver el árbol del grupo visualmente** en el panel Superadmin — el modelo (`empresa_principal`, `grupo_empresarial`) ya lo soporta, falta la pantalla de listado/árbol.
- **Coexistencia de "Venta #100" en dos empresas**: no hice una prueba dedicada a esto porque ya se cumple estructuralmente (cada `Sale` tiene su propio `id` autoincremental de base de datos, no un número de factura compartido entre empresas — no hay ninguna restricción `unique` cruzada entre empresas en `Sale` que esto pudiera romper), pero no lo verifiqué con una prueba explícita.
