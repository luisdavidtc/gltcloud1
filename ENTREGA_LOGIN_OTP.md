# Entrega: Login por correo electrónico + código OTP

Reemplaza el login por NIT + usuario + contraseña por correo + código
de 6 dígitos, con opción de "Confiar en este dispositivo" y sin tocar
la arquitectura multiempresa/multisucursal existente.

## 1. Cómo funciona ahora el login

Tres pasos, cada uno su propia URL:

1. **`/cuentas/login/`** — el usuario escribe su correo. Si el
   navegador ya es un dispositivo confiable reconocido para ese
   usuario, entra directo (sin OTP). Si no, se genera y envía un
   código de 6 dígitos por correo, válido 10 minutos, de un solo uso.
   **Nunca revela si el correo existe**: la respuesta es idéntica
   exista o no una cuenta con ese correo.
2. **`/cuentas/login/verificar/`** — el usuario escribe el código.
   Máximo 5 intentos fallidos por código antes de bloquearlo (hay que
   pedir uno nuevo). Incluye el checkbox "No volver a solicitar
   código en este dispositivo".
3. **`/cuentas/login/empresa/`** — solo si el usuario tiene acceso a
   más de una empresa. Con una sola, se salta este paso y entra
   directo. El Superadministrador de la plataforma nunca pasa por
   este paso (no pertenece a ninguna empresa).

Límites anti-abuso: máximo 1 código cada 45 segundos y máximo 5
códigos por hora, por usuario.

Toda la auditoría (código enviado, validado, incorrecto, expirado,
bloqueado, error de envío, dispositivo reconocido/confiado/revocado,
intento de empresa no autorizada) queda en `LoginAccessLog`
(`accounts.models`), con IP y navegador.

## 2. Cómo funciona "Confiar en este dispositivo"

Al marcar la casilla tras validar el OTP, se crea un `TrustedDevice`
(patrón selector/validador, igual que un "remember me" o un token de
restablecimiento de contraseña): la cookie del navegador
(`glt_dispositivo_confiable`, HttpOnly, `Secure` cuando la conexión es
HTTPS, `SameSite=Lax`, 30 días) guarda `selector:secreto`. El
**secreto nunca se guarda en texto plano** en la base de datos, solo
su hash irreversible — aunque alguien leyera la base de datos
completa, no podría reconstruir una cookie válida.

En logins posteriores, si la cookie corresponde a un dispositivo
vigente **del mismo usuario que escribió el correo** (no basta con
tener la cookie; también hay que escribir el correo correcto), se
salta el paso de OTP.

Gestión desde el ERP: **Perfil de usuario > Dispositivos confiables**
(`/cuentas/dispositivos/`, enlazado en el menú de usuario de la barra
superior) — lista los dispositivos, con botón para revocar uno o
todos. También se revocan automáticamente todos los dispositivos de
un usuario cuando:
- Cambia su contraseña obligatoria (`cambiar_password_obligatorio`).
- El Superadministrador le resetea la contraseña desde su panel.

## 3. Cómo quedó integrado con multiempresa

No se tocó nada de la resolución de empresa activa
(`tenants.middleware.EmpresaMiddleware`, `EmpresaAcceso`,
`CustomUser.empresas_accesibles`, el selector de empresa activa en la
barra superior ya existente): el login nuevo solo decide **cuál
empresa queda como activa en la sesión** al final del flujo,
reutilizando exactamente esos mismos componentes:

- Una empresa → se fija directo, igual que antes.
- Varias empresas → selector nuevo (paso 3), que revalida
  server-side contra `user.empresas_accesibles` — nunca confía en el
  POST.
- Ninguna empresa → se cierra la sesión con mensaje claro.
- Empresa suspendida o con licencia vencida → el login nunca lo
  bloquea (a diferencia del login viejo): el usuario se autentica
  normalmente y es el `EmpresaMiddleware` existente el que lo
  redirige a la pantalla informativa correspondiente en la siguiente
  petición — se reutiliza el gate que ya existía en vez de
  duplicarlo.
- Superadministrador → flujo independiente sin selector de empresa,
  intacto.

## 4. Archivos modificados

| Archivo | Cambio |
|---|---|
| `accounts/models.py` | + `LoginOTP`, `TrustedDevice`, `LoginAccessLog` |
| `accounts/forms.py` | `LoginEmpresaForm` (NIT+usuario+contraseña) reemplazado por `EmailLoginForm` y `VerificarOTPLoginForm`. `UserCreateForm`/`UserUpdateForm`: `email` ahora obligatorio y único |
| `accounts/views.py` | Reescrito el login (3 vistas nuevas: `login_view`, `login_verificar`, `login_seleccionar_empresa`) + `login_reenviar_codigo`, `dispositivos_confiables`, `revocar_dispositivo_view`, `revocar_todos_dispositivos_view`. `cambiar_password_obligatorio` ahora revoca dispositivos confiables al cambiar la contraseña |
| `accounts/urls.py` | + 8 rutas nuevas (verificar, reenviar, selector de empresa, dispositivos) |
| `accounts/otp_login.py` | **Nuevo** — toda la lógica de negocio del login por correo+OTP y dispositivos confiables |
| `platform_admin/forms.py` | `AdminUsuarioForm.admin_email` ahora obligatorio y único (antes opcional — sin esto, el admin de una empresa nueva no podría entrar nunca) |
| `platform_admin/views.py` | `empresa_usuario_resetear_password` también revoca los dispositivos confiables del usuario reseteado |
| `templates/accounts/login.html` | Rediseñado: solo campo de correo (antes NIT+usuario+contraseña) |
| `templates/accounts/login_verificar.html` | **Nuevo** — código de 6 dígitos + checkbox de confiar dispositivo |
| `templates/accounts/login_seleccionar_empresa.html` | **Nuevo** — selector de empresa post-login |
| `templates/accounts/email_otp_login.html` | **Nuevo** — correo con el código |
| `templates/accounts/dispositivos_confiables.html` | **Nuevo** — gestión de dispositivos confiables |
| `templates/base.html` | + enlace "Dispositivos confiables" en el menú de usuario |
| `tenants/tests.py` | Actualizado: el helper `_login` y los tests de login/selector/superadmin ahora usan el flujo por correo+OTP en vez de NIT+usuario+contraseña |

## 5. Modelos y migración

- `LoginOTP`, `TrustedDevice`, `LoginAccessLog` — nuevos, en `accounts`.
- Migración `accounts/0008_login_otp_correo.py` — creada y **ya
  ejecutada** sobre `db.sqlite3` (se hizo un backup de la base de
  datos antes, además del backup completo del proyecto).
- No se tocó ningún modelo de `inventory`, `sales`, `purchases`,
  `repairs`, `contabilidad`, `clients` ni ningún otro módulo fuera de
  autenticación/multiempresa.
- El sistema de 2FA por TOTP que ya estaba desactivado en el proyecto
  (`accounts/totp.py`, `accounts/views_totp.py`, migración
  `0007_eliminar_2fa_totp`) se dejó tal cual — ya estaba desconectado
  de las URLs antes de este cambio, no se tocó.

## 6. Pruebas realizadas

Corrí un script de validación con 36 verificaciones cubriendo los 12
casos pedidos (A-K del pedido original + límites de solicitudes) — **todas
pasaron**:

| # | Caso | Resultado |
|---|---|---|
| A | Usuario normal: correo → OTP → acceso correcto | ✅ |
| B | OTP incorrecto rechazado | ✅ |
| C | OTP expirado rechazado | ✅ |
| D | Exceso de intentos bloquea el código | ✅ |
| E | Confiar en este dispositivo: 2do login sin OTP | ✅ |
| F | Dispositivo nuevo sí pide OTP | ✅ |
| G | Dispositivo revocado vuelve a pedir OTP | ✅ |
| H | Usuario con una empresa entra directo | ✅ |
| I | Usuario con varias empresas puede elegir | ✅ |
| J | Intento de acceder a empresa no autorizada rechazado | ✅ |
| K | Superadministrador conserva su acceso independiente | ✅ |
| — | Correo inexistente no revela nada | ✅ |
| — | Límite de reenvío (45s) y de solicitudes por hora (5) | ✅ |

También corrí el flujo completo con los **3 usuarios reales** del
proyecto (`administrador` → Superadministrador, `masterstore3` y
`eagletechnology` → cada uno a su propia empresa): los tres
funcionan correctamente de punta a punta.

Además actualicé y corrí la suite de pruebas automatizadas existente
(`tenants/tests.py`, 19 pruebas de la auditoría multiempresa): **18
de 19 pasan**. La que falla
(`test_p_superadmin_puede_entrar_en_modo_soporte`) es un **bug
preexistente, ajeno a este cambio** — lo confirmé corriendo la misma
prueba contra el proyecto original sin tocar nada, y ya fallaba ahí:
el middleware de "modo soporte" del Superadministrador
(`tenants.middleware.EmpresaMiddleware`) nunca llegó a leer
`session['soporte_empresa_id']`, así que lo redirige a su panel
incluso estando en modo soporte. No lo corregí por estar fuera del
alcance de este pedido (autenticación/multiempresa), pero queda
documentado por si quieres que lo revise en otra sesión.

`python manage.py check` no reporta ningún problema.

## 7. Configuración que debes realizar tú

**Correo saliente (SMTP)** — sin esto, el proyecto usa el backend de
consola (los códigos se imprimen en el log del servidor, nadie los
recibe de verdad). En el `.env` del servidor de producción:

```
EMAIL_HOST=smtp.tu-proveedor.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_usuario_smtp
EMAIL_HOST_PASSWORD=tu_password_smtp
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@tudominio.com
```

Si ya tenías esto configurado para el módulo de Contabilidad
(`security/services.py`, que usa el mismo mecanismo), no hace falta
nada adicional — el login nuevo reutiliza la misma configuración.

**Usuarios sin correo**: si en producción tienes usuarios creados
antes de este cambio sin correo electrónico, no van a poder iniciar
sesión (el correo es ahora el único identificador de login).
Revísalos antes de desplegar:

```python
python manage.py shell -c "
from accounts.models import CustomUser
print(list(CustomUser.objects.filter(email='').values_list('username', flat=True)))
"
```

**Correos duplicados**: si dos usuarios comparten el mismo correo
(sin distinguir mayúsculas), ninguno de los dos podrá iniciar sesión
(por diseño — no revela cuál de los dos es, y no elige uno al azar).
Revísalos también antes de desplegar:

```python
python manage.py shell -c "
from django.db.models import Count
from django.db.models.functions import Lower
from accounts.models import CustomUser
print(list(CustomUser.objects.annotate(e=Lower('email')).values('e').annotate(c=Count('id')).filter(c__gt=1)))
"
```

En la base de datos que me enviaste, verifiqué los 3 usuarios
existentes: los tres tienen correo y no hay ninguno duplicado.
