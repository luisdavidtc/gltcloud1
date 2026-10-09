# Cierre de módulo de Contabilidad + contraseña obligatoria al usar la clave temporal

Dos cambios independientes, cada uno aditivo y verificado por separado.

## 1. Botón "Cerrar módulo de Contabilidad"

**Dónde aparece:** en el navbar superior, junto al título de la pantalla,
**solo** cuando `seccion_activa == 'contabilidad'` (o sea, en
`accounting/dashboard.html` y `accounting/en_desarrollo.html`, sin tocar el
navbar del resto de módulos).

**Qué hace:** envía un POST a `security:cerrar_modulo` (nueva vista en
`security/views.py`), que borra cualquier `SecurityAuthorization` vigente
del usuario para el módulo `contabilidad` y lo devuelve al Dashboard
principal (`dashboard:index`).

Con esto, si el usuario vuelve a entrar a Contabilidad más adelante, se
evalúa `requiere_verificacion()` desde cero — igual que si nunca hubiera
entrado — en vez de reutilizar la autorización de los últimos 30 minutos.

**Reactivación del token para Contabilidad** (ajuste pedido después de ver
el botón en pantalla): el flujo de verificación por correo de `security`
estaba apagado a nivel de datos para todos los módulos desde
`CAMBIOS_2FA_TOTP.md` / `security/migrations/0004_disable_email_otp.py`
(`requiere_token=False`), reemplazado por el 2FA de la app autenticadora a
nivel de cuenta. Con eso apagado, el botón "Cerrar módulo" no tenía ningún
efecto visible: no había nada que "volviera a pedir" nada. Se agregó
`security/migrations/0005_reactivar_token_contabilidad.py`, que enciende
`requiere_token=True` **solo** para Contabilidad (el resto de módulos sigue
en `False`, tal como quedó en `0004`). El 2FA por TOTP de la cuenta no se
toca: sigue siendo un segundo factor aparte, a nivel de todo el login; este
token es adicional, específico del módulo Contabilidad, y ahora sí se
vuelve a pedir cada vez que la autorización no está vigente — incluida la
que el botón "Cerrar módulo" acaba de borrar.

Nota: el rol Administrador (el que aparece en tu pantalla, "Local 59 ·
Administrador") **sí** pasa por este token — solo Contador y el
Superadministrador de la plataforma están exentos por diseño (ver
`security/services.py:usuario_exento_de_token`).

**Archivos:**
- `security/views.py` — nueva vista `cerrar_modulo(request, codigo)`.
- `security/urls.py` — nueva ruta `acceso/<slug:codigo>/cerrar/`,
  `security:cerrar_modulo`.
- `security/migrations/0005_reactivar_token_contabilidad.py` — migración de
  datos, reversible, que reactiva `requiere_token` solo para Contabilidad.
- `templates/base.html` — botón condicional en el navbar (`btn-outline-danger`,
  ícono `bi-box-arrow-left`), como un `<form>` con su propio `csrf_token`
  (la acción modifica datos — borra autorizaciones — así que va por POST,
  no por un simple link).

## 2. Contraseña obligatoria al entrar con la clave temporal de 6 dígitos

Aplica a los dos lugares donde hoy se genera una clave temporal
**solo numérica de 6 dígitos** (`platform_admin/forms.py:generar_password_temporal`):
crear una empresa nueva (con su usuario administrador) y resetear la
contraseña de un usuario desde el panel del Superadministrador.

**Comportamiento:** apenas ese usuario inicia sesión (con o sin 2FA por
TOTP de por medio — el chequeo corre después de que Django ya llamó a
`login()` en cualquiera de los dos flujos), se le redirige de una vez a
una pantalla bloqueante para que fije su propia contraseña, **antes** de
poder ver cualquier otra pantalla del ERP. No puede saltársela visitando
otra URL directamente.

**Regla de la nueva contraseña:** mínimo 8 caracteres, con al menos una
letra y al menos un número, más su confirmación (los dos campos deben
coincidir). Se probó explícitamente: clave muy corta, solo números, solo
letras, confirmación que no coincide y clave válida — los cuatro primeros
casos quedan bloqueados con su mensaje correspondiente.

**Piezas nuevas:**
- `accounts/models.py` — campo `debe_cambiar_password` (booleano,
  `default=False`) en `CustomUser`.
- `accounts/migrations/0006_customuser_debe_cambiar_password_and_more.py` —
  migración aditiva (el resto de operaciones que trae son solo
  `AlterField` de `help_text`/`verbose_name` en campos del 2FA que ya
  existían sin migrar; no tocan el esquema real de la tabla).
- `accounts/forms.py` — `CambioPasswordObligatorioForm`, basado en
  `SetPasswordForm` de Django (ya trae la comparación de "confirmar
  contraseña" y corre `AUTH_PASSWORD_VALIDATORS`, entre ellos
  `MinimumLengthValidator` = 8). Se le suma `clean_new_password1` con la
  regla explícita de letras + números.
- `accounts/views.py` — vista `cambiar_password_obligatorio`: si el
  usuario no tiene el flag activo, lo manda de vuelta a su pantalla normal
  (por si alguien visita la URL sin necesitarla); si lo tiene, procesa el
  formulario, apaga el flag, y usa `update_session_auth_hash` para que el
  cambio de contraseña no invalide la sesión que ya está activa.
- `accounts/urls.py` — ruta `cuentas/cambiar-password-obligatorio/`,
  `accounts:cambiar_password_obligatorio`.
- `accounts/middleware.py` — `PasswordObligatorioMiddleware` (nuevo),
  mismo patrón que `tenants.middleware.EmpresaMiddleware`: una lista de
  prefijos siempre exentos (`/cuentas/`, `/admin/`, `/static/`, `/media/`)
  para no encerrar a nadie fuera de su propio login/logout ni romper
  estáticos.
- `erp_config/settings.py` — se registra el middleware nuevo justo después
  de `AuthenticationMiddleware` y antes de `EmpresaMiddleware`, para que la
  contraseña temporal sea lo primero que se resuelve, incluso antes que
  los gates de empresa suspendida / licencia vencida.
- `templates/accounts/cambiar_password_obligatorio.html` — pantalla nueva,
  mismo lenguaje visual que `login.html` / `verificar_totp.html` (reutiliza
  `login.css`), con enlace de "Cerrar sesión" por si el usuario no es quien
  debería estar cambiando esa contraseña en ese momento.
- `platform_admin/views.py` — se marca `debe_cambiar_password = True` en
  los dos puntos donde se llama a `generar_password_temporal()`:
  `empresa_create` (usuario administrador de una empresa nueva) y
  `empresa_usuario_resetear_password`.

## Verificación realizada

- `python manage.py check` — sin errores.
- `python manage.py makemigrations --check --dry-run` — sin cambios
  pendientes después de generar la migración.
- Migración aplicada de verdad contra una copia de la base de datos
  (`accounts.0006`) — corrió sin errores.
- `CambioPasswordObligatorioForm` probado con 5 casos (muy corta, solo
  números, solo letras, no coinciden, válida) — cada uno con el mensaje
  esperado.
- Simulación completa por shell: crear usuario con
  `debe_cambiar_password=True` → guardar la nueva contraseña por el
  formulario → apagar el flag → confirmar que la contraseña nueva
  autentica.
- Simulación de extremo a extremo con el test client de Django (login real
  por HTTP): `GET /` y `GET /contabilidad/` redirigen a
  `/cuentas/cambiar-password-obligatorio/` mientras el flag está activo;
  la pantalla carga (200); el `POST` con la contraseña válida guarda,
  apaga el flag y redirige a `/`; después de eso, `GET /` ya carga normal
  (200), sin volver a interceptar.
- Simulación del botón "Cerrar módulo": se creó una `SecurityAuthorization`
  vigente a mano, se hizo `POST` a `/seguridad/acceso/contabilidad/cerrar/`
  logueado como el usuario, y se confirmó que la autorización quedó
  borrada y la respuesta redirige a `/`.
- Ciclo completo de extremo a extremo con `requiere_token=True` en
  Contabilidad (después de aplicar `0005`): primera entrada a
  `/contabilidad/` sin autorización → redirige al gate; se valida un
  código (por la vista AJAX real, `validar-codigo/`) → queda autorizado y
  la segunda entrada carga directo (200); `POST` a "Cerrar módulo" → borra
  la autorización; la siguiente entrada a `/contabilidad/` **vuelve a
  redirigir al gate**, pidiendo el código de nuevo — el comportamiento
  pedido.
- Render real de `/contabilidad/` logueado: el botón aparece en el HTML
  con la URL correcta, y se confirmó que **no** aparece en el HTML de
  `/` (dashboard normal) — el `seccion_activa == 'contabilidad'` no se
  filtra a otras pantallas.

## Pendiente de tu parte

- Correr `python manage.py migrate` en tu entorno local para aplicar
  `accounts.0006_customuser_debe_cambiar_password_and_more` y
  `security.0005_reactivar_token_contabilidad`.
- Con el token de Contabilidad reactivado, el envío del código depende de
  que tu `.env` tenga un `EMAIL_HOST` real y funcionando (o del backend de
  consola si `EMAIL_HOST` está vacío, para pruebas locales). Si en algún
  momento el correo no sale, el modal ya lo informa honestamente en vez de
  decir "enviado" por error (ver `security/services.py`, corrección de
  `CAMBIOS_OTP_EMAIL.md`).
- Si en algún momento quieres apagar de nuevo el token para Contabilidad
  sin tocar código, ya existe la pantalla `Seguridad > Configuración de
  seguridad` para alternarlo — la migración solo fija el valor inicial.
- No se tocó ningún dato existente: usuarios que ya tienen contraseña
  propia (no vinieron de un código de 6 dígitos reciente) quedan con
  `debe_cambiar_password=False` por el `default` del campo — nadie que ya
  esté usando el sistema normalmente se ve interrumpido por este cambio.
