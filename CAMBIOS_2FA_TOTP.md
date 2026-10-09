# Migración del segundo factor: correo electrónico → TOTP (Google Authenticator)

Este documento resume el reemplazo del segundo factor de autenticación
del ERP, para quien despliegue estos cambios o los revise más adelante.

## 1. Qué cambió

| Antes | Ahora |
|---|---|
| Al entrar a un módulo protegido (solo Contabilidad tenía `requiere_token=True`), la app `security` enviaba un código de 6 dígitos por correo (`security/services.py`, `enviar_codigo`) que el usuario debía ingresar en `security:gate`. | Al iniciar sesión (`accounts:login`), si el usuario activó el 2FA en su perfil, se le pide un código TOTP de 6 dígitos generado por su app autenticadora (Google Authenticator, Microsoft Authenticator, Authy, 2FAS o Aegis). Sin conexión a internet ni envío de correos. |
| El 2FA no era una opción del usuario: lo activaba un administrador por módulo, desde `security:config`. | Cada usuario activa/desactiva su propio 2FA desde **Mi perfil y seguridad** (menú del usuario, arriba a la derecha). |
| No existían códigos de recuperación. | Al activar el 2FA se generan 10 códigos de recuperación de un solo uso (descargables en PDF). |

## 2. Por qué el flujo por correo no se borró, se desactivó

`security/migrations/0004_disable_email_otp.py` es una migración de
**datos** (no de esquema): pone `requiere_token=False` en todos los
`ModuloProtegido` — incluido `contabilidad`, que era el único en
`True`. El propio código de `security/views.py` (`gate`) y
`security/decorators.py` (`requiere_acceso_seguro`) ya comprueban
`requiere_verificacion()` antes de pedir cualquier código: con
`requiere_token=False`, esa comprobación siempre da `False` y el
usuario pasa directo. En la práctica, **el flujo por correo queda
completamente inactivo**: nunca se envía ni se pide un código de esa
forma.

No se borró el modelo `SecurityToken`, las vistas, ni las plantillas
de `security` porque:
1. Se conserva el historial de auditoría ya generado
   (`SecurityAccessLog`), visible desde el admin y desde las pantallas
   de Auditoría/Historial de esa app.
2. La migración es reversible sin pérdida de datos.
3. Un administrador podría, en teoría, reactivar la protección de un
   módulo puntual desde `security:config` — si tu equipo prefiere que
   esa pantalla deje de existir del todo, es un cambio adicional
   sencillo (avísame y lo hago).

Si en algún momento quieres eliminar el código de `security` por
completo en vez de solo desactivarlo, es un cambio aparte — dímelo y
lo preparo con su propia migración de reversión de esquema.

## 3. Archivos nuevos/modificados

**Nuevos:**
- `accounts/totp.py` — cifrado del secreto (Fernet), generación/verificación TOTP (pyotp), códigos de recuperación.
- `accounts/views_totp.py` — vistas de activar/desactivar/regenerar 2FA y códigos de recuperación.
- `accounts/twofactor_pdf.py` — PDF de códigos de recuperación (reutiliza `core/pdf.py`).
- `accounts/company_display.py` — helper mínimo para el nombre de empresa en el PDF.
- `accounts/migrations/0005_two_factor_auth.py` — campos nuevos en `CustomUser` + modelo `TwoFactorAuditLog`.
- `security/migrations/0004_disable_email_otp.py` — desactiva el flujo por correo (ver sección 2).
- `templates/accounts/verificar_totp.html`, `perfil_seguridad.html`, `activar_totp.html`, `codigos_recuperacion.html`.
- `static/css/twofactor.css`.

**Modificados:**
- `accounts/models.py` — campos `two_factor_enabled`, `two_factor_secret`, `two_factor_confirmed_at`, `two_factor_recovery_codes`, `last_totp_login`, `failed_totp_attempts`, `locked_until` en `CustomUser`; nuevo modelo `TwoFactorAuditLog`.
- `accounts/views.py` — `login_view` ahora es de dos pasos; nueva vista `verificar_totp_login`.
- `accounts/forms.py` — `CodigoTOTPForm`, `VerificarLoginForm`.
- `accounts/urls.py`, `accounts/admin.py`.
- `erp_config/settings.py` — `TOTP_ENCRYPTION_KEY`.
- `requirements.txt` — se agregan `pyotp` y `cryptography`.
- `templates/base.html` — un único enlace nuevo en el menú del usuario: "Mi perfil y seguridad". No se tocó el sidebar, ni los colores, ni la tipografía, ni ningún otro módulo.

## 4. Cómo desplegarlo

```bash
pip install -r requirements.txt
python manage.py migrate
```

No hace falta ninguna variable de entorno nueva para que funcione: si
no defines `TOTP_ENCRYPTION_KEY` en tu `.env`, se deriva
automáticamente de tu `SECRET_KEY` (ver comentario en
`erp_config/settings.py`). **Buena práctica recomendada** para
producción: define tu propia clave, independiente de `SECRET_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# agrega el resultado a tu .env:
# TOTP_ENCRYPTION_KEY=<lo que imprimió el comando>
```

⚠️ Si cambias `TOTP_ENCRYPTION_KEY` después de que algún usuario ya
activó su 2FA, sus secretos guardados dejarán de poder descifrarse
(tendrán que desactivar y volver a activar el 2FA). Defínela una vez,
al principio, y no la cambies luego.

## 5. Buenas prácticas de seguridad ya implementadas

- **Secreto cifrado, nunca en texto plano** (`accounts.totp.cifrar_secreto`, Fernet/AES).
- **Códigos de recuperación con hash irreversible** (`django.contrib.auth.hashers`), igual que una contraseña — nunca se guarda el código en texto plano, solo se muestra una vez.
- **Nunca se guarda el código TOTP de 6 dígitos** en ningún lado (ni en sesión ni en base de datos): se valida al vuelo contra el secreto.
- **Ventana de tolerancia ±30 segundos** (`valid_window=1` en pyotp).
- **Protección de fuerza bruta**: 5 intentos fallidos → bloqueo de 15 minutos (`accounts.totp.MAX_INTENTOS_TOTP` / `MINUTOS_BLOQUEO_TOTP`).
- **Auditoría** de activaciones, desactivaciones, logins correctos/incorrectos y uso de códigos de recuperación (`TwoFactorAuditLog`, visible en el admin y en "Últimos eventos" del perfil).
- **Confirmación de contraseña** para desactivar el 2FA (evita que una sesión abierta desatendida alcance para quitar la protección).
- Librería estándar para TOTP (`pyotp`, RFC 6238) — no se implementó el algoritmo a mano.

## 6. Lo que quedó fuera de alcance (marcado explícitamente como opcional en el pedido)

- **"Ver dispositivos confiables"**: se dejó como elemento visual "Próximamente" en el perfil de seguridad. Implementarlo de verdad (recordar un dispositivo para no pedir 2FA en cada login desde él) es una función aparte, con su propio diseño de cookies/tokens de dispositivo — puedo construirla en una siguiente iteración si la necesitas.

## 7. Importante: no se pudo ejecutar `migrate` en este entorno

Este entorno de trabajo no tiene Django instalado (es un contenedor
aislado para editar archivos, no el servidor del ERP), así que no fue
posible correr `makemigrations`/`migrate` ni levantar el servidor para
probar el flujo de punta a punta. Las migraciones se escribieron a
mano siguiendo exactamente el estilo y la estructura de las
migraciones ya generadas por Django en este proyecto. **Antes de
usarlo con usuarios reales**, corre `python manage.py migrate` en tu
entorno real y prueba el flujo completo (activar, escanear QR con una
app real, cerrar sesión, volver a entrar, probar un código de
recuperación) en un ambiente de pruebas primero.
