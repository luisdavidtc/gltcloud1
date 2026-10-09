# Archivos modificados/creados — GLT ERP Cloud

⚠️ Trabajé sobre la copia del proyecto en la **raíz** del ZIP (`/erp`, la que
tiene `manage.py` en su nivel superior). El ZIP original traía **otra copia
completa anidada** en `erp/erp/` con diferencias reales (ej. módulo de
Contabilidad ya activo vs. "Próximamente"); no la toqué. Confírmame si esa
carpeta es una copia vieja a ignorar o si en realidad es la que usas, para
replicar los cambios ahí también.

## 1. Título de pestañas (ERP Celulares → GLT Cloud)
Se cambió únicamente el texto dentro de `<title>` / `{% block title %}` en
43 plantillas (no se tocó el nombre de marca del sidebar, que sigue usando
`company_config.nombre_comercial`).

## 2. Campo `digito_verificacion` en `Client`
- `clients/models.py` — nuevo campo `digito_verificacion` (máx. 1 carácter, opcional).
- `clients/migrations/0006_client_digito_verificacion.py` — migración nueva, lista para `python manage.py migrate`.
- `clients/forms.py` — `ClientForm` actualizado (campo opcional, widget con `maxlength=1`).

## 3 y 4. Campo DV condicional (Persona Jurídica + NIT)
Se muestra junto a "Documento" y se oculta/limpia automáticamente en
cualquier otro caso, en:
- `templates/clients/client_form.html` (Clientes: crear/editar) — con JS inline en `{% block extra_js %}`.
- `templates/sales/sale_form.html` (modal "Nuevo cliente" desde Ventas) — lógica en `static/js/sale_form.js`.

## 5 y 6. Botón "Nuevo cliente" → modal AJAX (módulo Clientes)
- `templates/clients/client_list.html` — el botón ahora abre un modal Bootstrap
  (`#modalNuevoClienteLista`) en vez de redirigir; el listado (`#tablaClientesBody`
  y `#paginacionClientes`) se refresca por AJAX al guardar, sin recargar la página.
- `static/js/client_list.js` (nuevo) — maneja el modal: toggle Natural/Jurídica,
  envío AJAX contra `clients:client_create_ajax` (la vista existente, sin duplicar
  lógica de backend) y refresco del listado.
- `static/js/clients_modal.js` (nuevo) — utilidades **compartidas** entre el modal
  de Ventas y el nuevo modal de Clientes (toggle del campo DV + envío AJAX con
  manejo de errores), para no duplicar esa lógica dos veces.
- `static/js/sale_form.js` — refactorizado para usar `clients_modal.js` en vez de
  tener su propia copia de esa lógica; el comportamiento del modal de Ventas
  no cambió.

## Pendiente de tu lado / próxima verificación
No alcancé a correr en este entorno `python manage.py makemigrations --check`
ni `python manage.py check` contra tu `settings.py` real (usa Postgres). Antes
de desplegar, corre:

```bash
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py migrate
```
