# Módulo Seguridad + Acceso por Token — GLT Cloud

Nueva app **`security`**, 100% desacoplada: no se modificó ningún
modelo, vista, URL ni migración de los módulos existentes (Ventas,
Inventario, Clientes, Compras, Servicio Técnico, Caja, Reportes,
Usuarios, etc.). Los únicos archivos compartidos que se tocaron son
los tres imprescindibles para que la app nueva exista y quede
enlazada, detallados al final de este documento.

## Qué se implementó

- **Catálogo de módulos protegidos** (`ModuloProtegido`): cada módulo
  del sidebar puede marcarse "Requiere token" / "No requiere token"
  desde Seguridad > Configuración de seguridad. Sembrado inicial
  (migración de datos `0002_seed_modulos`):

  | Módulo | Requiere token |
  |---|---|
  | Dashboard | No |
  | Ventas | No |
  | Inventario | No |
  | Clientes | No |
  | Compras | No |
  | Servicio Técnico | No |
  | Caja | No |
  | **Contabilidad** | **Sí** |

- **Flujo de acceso**: al hacer clic en Contabilidad se abre un modal
  Bootstrap ("Acceso protegido") en vez de entrar directo. El modal
  pide confirmar el envío del código, luego el código de 6 dígitos
  recibido por correo, y solo entonces redirige al módulo.

- **Código de verificación**: 6 dígitos, generado con
  `random`, guardado **cifrado** (hash irreversible PBKDF2, el mismo
  mecanismo con el que Django protege las contraseñas — nunca se
  guarda ni se puede leer en texto plano), asociado al usuario y al
  módulo, expira a los 5 minutos y es de un solo uso. Máximo 5
  intentos de validación por código antes de bloquearlo.

- **Correo HTML** con el asunto y el mensaje pedidos, usando la
  configuración SMTP que ya existe en el proyecto
  (`EMAIL_HOST`/`EMAIL_HOST_USER`/etc. de `.env`; si no hay SMTP
  configurado, cae al backend de consola como el resto del sistema).

- **Autorización temporal de 30 minutos**: una vez validado el
  código, el usuario entra a Contabilidad sin que se le vuelva a
  pedir durante ese lapso; pasado ese tiempo, se le vuelve a pedir.

- **Auditoría** (`SecurityAccessLog`): un registro por cada intento
  (código enviado, validado, incorrecto, expirado, bloqueado), con
  usuario, fecha/hora, módulo, IP, navegador y si el código fue
  correcto — visible en Seguridad > Auditoría (con filtro por
  resultado) y Seguridad > Historial de accesos (solo los concedidos).

- **Roles**: se usan los roles que ya existían en `accounts.CustomUser`
  (no se agregó ningún rol nuevo, todos ya estaban disponibles).
  - **Administrador** (`role='admin'`): debe ingresar el código, igual
    que cualquier otro rol no exento.
  - **Contador** (`role='contador'`): exento, entra sin código.
  - **Super Administrador** (`is_superuser=True` sin empresa, el
    Superadministrador de la plataforma): exento, entra sin código.

- **Menú Seguridad** (solo visible para administradores, igual que
  Reportes/Usuarios/Configuración): Configuración de seguridad,
  Historial de accesos, Tokens emitidos, Auditoría.

- **Decorador reutilizable** `security.decorators.requiere_acceso_seguro`,
  listo para proteger la vista real de Contabilidad (o cualquier otro
  módulo) el día que se implemente — hoy Contabilidad sigue siendo la
  pantalla "Próximamente" de siempre (`core:en_desarrollo`), solo que
  ahora se llega a ella pasando por el gate de seguridad.

## Modelos nuevos (app `security`, migraciones propias)

- `ModuloProtegido` — catálogo configurable.
- `SecurityToken` — código emitido (hash, expiración, usos, intentos).
- `SecurityAuthorization` — sesión temporal de 30 minutos.
- `SecurityAccessLog` — auditoría de cada intento.

## Los 3 toques a archivos compartidos (mínimos e imprescindibles)

1. `erp_config/settings.py`: se agregó `'security'` a `INSTALLED_APPS`.
2. `erp_config/urls.py`: se agregó `path('seguridad/', include('security.urls'))`.
3. `templates/base.html`:
   - El enlace de "Contabilidad" ahora apunta a `security:gate` (antes
     iba directo a `core:en_desarrollo`) — es el cambio que hace que
     el clic abra el modal en vez de entrar directo, tal como se pidió.
   - Se agregó la sección "Seguridad" al sidebar (solo administradores).

Ningún módulo de negocio existente cambió de comportamiento, URL,
modelo ni lógica.

## Verificación realizada

Se corrió `migrate` sobre el proyecto completo (todas las apps
existentes + `security`) sin errores, y se probó de punta a punta con
el test client de Django: login, apertura del modal, envío de código,
validación con código incorrecto y correcto, redirección directa en
visitas posteriores dentro de los 30 minutos, exención de Contador y
Super Administrador, bloqueo normal para otros roles, y las 4
pantallas del submenú Seguridad.
