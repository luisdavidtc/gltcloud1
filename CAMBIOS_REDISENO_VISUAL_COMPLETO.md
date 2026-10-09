# Rediseño visual completo — GLT Cloud ERP

Referencia visual: TrendyAdmin (https://bootstrapmade.com/demo/TrendyAdmin/)
Tipo de cambio: **100% visual (CSS + 5 líneas de markup decorativo + 1 script aislado). Cero cambios de lógica, modelos, migraciones, vistas, URLs, permisos o autenticación.**

## 1. Archivos modificados

| Archivo | Qué cambió |
|---|---|
| `static/css/design-system.css` | Se ampliaron los tokens (`:root`): nueva escala de color de marca (petróleo, turquesa, azul tecnológico), superficies, bordes, radio "pill", anillo de foco. Se agregó un **puente hacia las variables nativas de Bootstrap 5.3** (`--bs-primary`, `--bs-border-radius`, `--bs-box-shadow`, etc.) que reskinea automáticamente botones, badges, alerts, etc. en toda la app. Se agregó el bloque `[data-bs-theme="dark"]` con la paleta de modo oscuro (preparado, no activo por defecto). **Nada de lo anterior se eliminó** — solo se agregó contenido nuevo al final del `:root` existente. |
| `static/css/styles.css` | Sidebar: logo con "chip" turquesa, ajuste de tokens. Navbar: usa `--erp-card-bg` (compatible con modo oscuro). KPI cards: bordes, sombra y tipografía alineadas al nuevo sistema. Se quitaron 2 bloques (`.card`, `.table thead th`) que quedaron **duplicados** ahora que `components.css` los define de forma global (se elimina así la duplicación de CSS que pedías evitar). Se agregó el estilo del botón de modo oscuro. |
| `templates/base.html` | Se agregó `<link>` a `components.css`, `data-bs-theme="light"` explícito en `<html>`, el botón `#erpThemeToggle` (nuevo, opcional) y el `<script src="js/theme.js">`. Ningún ID, name, url, bloque o script existente fue tocado. |
| `templates/accounts/login.html` | Se agregó el `<link>` a `components.css`. Sin cambios de estructura ni de campos del formulario. |
| `templates/accounts/verificar_totp.html` | Igual: solo se agregó el `<link>` a `components.css`. |
| `templates/accounts/cambiar_password_obligatorio.html` | Igual: solo se agregó el `<link>` a `components.css`. |
| `templates/platform_admin/base_superadmin.html` | Igual: solo se agregó el `<link>` a `components.css`, para que el panel de Superadministrador reciba el mismo rediseño. |

## 2. Archivos nuevos

| Archivo | Para qué |
|---|---|
| `static/css/components.css` | **El sistema de diseño global reutilizable que pediste.** Reskinea, usando únicamente selectores estándar de Bootstrap (`.btn`, `.card`, `.table`, `.form-control`, `.modal-content`, `.alert`, `.badge`, `.dropdown-menu`, `.pagination`, `.nav-tabs`...), los 8 componentes que listaste (botones, cards, tablas, formularios, modales, alertas, badges, dropdowns, paginación) más animaciones discretas y scrollbars finos. Al ser selectores globales, **se aplica automáticamente a las 85 plantillas del proyecto sin tener que tocar cada una**, y evita que cada módulo reinvente su propio botón/card/tabla. |
| `static/js/theme.js` | Toggle de modo claro/oscuro. Aislado por completo: solo lee/escribe `data-bs-theme` en `<html>` y el botón `#erpThemeToggle`; no depende de ningún otro script ni interfiere con `sidebar.js`, `toasts.js`, `cash_register.js`, etc. El modo claro sigue siendo el predeterminado en cada carga nueva de página. |
| `.gitignore` | Se agregó para no versionar `__pycache__`/`.pyc` (higiene del repo; no afecta la app). |

## 3. Resumen de los cambios visuales

- **Paleta**: petróleo oscuro (`#0F2F3A`) + turquesa (`#0FB9B1`) como acentos de marca del *shell* (sidebar, botones primarios, focos, badges), azul tecnológico (`#2B6CF6`) como color de apoyo/información, blancos y grises neutros para el contenido — tal como pediste.
- **Botones**: radios más generosos, sombra suave en el primario, elevación sutil en hover, estados focus/disabled consistentes en todos los `btn-*` de Bootstrap.
- **Cards**: bordes redondeados (16px), sombra suave, cabeceras/pies alineados al mismo radio.
- **Tablas**: encabezados en mayúsculas con tracking, fila con highlight turquesa suave en hover, celdas con más aire.
- **Formularios**: inputs con radio moderno, borde y anillo de foco turquesa, placeholders y estados disabled coherentes.
- **Modales**: sin borde duro, sombra grande, animación de entrada sutil (escala + desplazamiento).
- **Alertas**: fondos "subtle" en vez de colores planos, coherentes con success/warning/danger/info.
- **Badges/estados**: forma "pill", tipografía en mayúsculas con tracking.
- **Dropdowns**: sombra, radio, hover turquesa suave.
- **Paginación**: botones redondeados, estado activo en turquesa.
- **Sidebar**: logo con "chip" de acento; se mantiene 100% el comportamiento existente (hover-reveal + toggle en móvil vía `#sidebarToggle`/`#erpSidebar`/`#sidebarBackdrop`).
- **Navbar**: fondo ahora sensible al token de superficie (listo para modo oscuro); nuevo botón de tema.
- **KPIs**: bordes, sombra y tipografía renovados sin tocar el markup que arma cada card desde el backend.
- **Login**: ya tenía un diseño *split-screen* premium (columna oscura turquesa + formulario); ahora comparte el mismo sistema de componentes global (inputs/alerts) que el resto del ERP.
- **Responsive**: se preservó intacto el comportamiento existente (sidebar overlay en móvil, ancho reducido en tablet); el nuevo CSS es 100% compatible con esos breakpoints.
- **Modo oscuro**: paleta completa preparada en `[data-bs-theme="dark"]` + toggle funcional en la navbar (`#erpThemeToggle`). Claro sigue siendo el modo por defecto en cada carga, como pediste.
- **Animaciones**: fade-in sutil en cards, transición de modal, respeta `prefers-reduced-motion`.

**No es un simple cambio de colores**: el salto viene de la combinación de radios más grandes y consistentes, sombras en capas, tipografía con mejor jerarquía, estados hover/focus cuidados en absolutamente todos los componentes interactivos, y un sistema de botón/card/tabla/badge unificado en un solo archivo reutilizable — el mismo enfoque de TrendyAdmin.

## 4. Confirmación: backend, modelos y migraciones intactos

- `git diff` confirma que **no se tocó ningún archivo `.py`**, ninguna carpeta `migrations/`, ni `models.py`, `views.py`, `urls.py`, `forms.py` de ningún app (`sales`, `inventory`, `purchases`, `cashregister`, `clients`, `providers`, `repairs`, `accounting`, `security`, `tenants`, `platform_admin`, `company`, `reports`, `dashboard`, `accounts`).
- Todos los `id`, `name`, clases funcionales (`.nav-link`, `.erp-submenu`, `.kpi-card`, etc.) y atributos `data-*` usados por `sidebar.js`, `toasts.js`, `cash_register.js`, `sale_form.js`, `purchase_form.js`, `order_form.js`, `client_list.js`, `clients_modal.js`, `security_gate.js`, `product_form.js`, `cash_movements.js` se dejaron exactamente igual.
- El reskin se logró casi en su totalidad por CSS puro (variables de Bootstrap 5.3 + selectores estándar), lo que permitió cubrir sidebar, navbar, dashboard, KPIs, tablas, formularios, botones, modales, alertas, badges, dropdowns, paginación y login **en las 85 plantillas** sin editar cada una individualmente.

## 5. Resultado de las pruebas

```
$ python manage.py check
System check identified no issues (0 silenced).

$ python manage.py test sales repairs inventory clients tenants accounts dashboard
Ran 20 tests in 20.885s
FAILED (failures=1)
```

- El único test que falla (`tenants.tests.SuperadminTests.test_p_superadmin_puede_entrar_en_modo_soporte`) **ya fallaba exactamente igual antes de este rediseño** (se verificó corriendo la suite sobre el código original, sin los cambios visuales). No está relacionado con CSS/HTML/JS — es un problema preexistente de redirección en la vista de modo soporte, ajeno a este trabajo.
- `python manage.py collectstatic --dry-run` corrió sin errores (160 archivos estáticos, incluyendo los 2 nuevos).
- Se verificó además que las plantillas modificadas (`base.html`, `login.html`, `verificar_totp.html`, `cambiar_password_obligatorio.html`, `base_superadmin.html`) compilan sin errores de sintaxis Django.
