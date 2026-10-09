# Corrección del módulo de Compras — integración menú ↔ vistas reales

## 1. Menú lateral (`templates/base.html`)
- "Nueva compra" → ahora apunta a `{% url 'purchases:purchase_create' %}` (antes no existía este ítem en el menú).
- "Historial de compras" → ahora apunta a `{% url 'purchases:purchase_list' %}` (antes `core:en_desarrollo`).
- Título del módulo: "Compras" → **"Gestión de Compras"** (tu sugerencia de la Fase 1).
- Arreglé también el permiso de visibilidad: antes el submenú de Compras solo
  se mostraba a `admin`/`vendedor` (copiado de Ventas por error, nunca se
  había corregido); ahora incluye el rol `compras` que sí existe en tu
  sistema de usuarios.

**Nota honesta — no lo cambié y te explico por qué:** "Órdenes de compra" y
"Recepción de mercancía" siguen apuntando a `core:en_desarrollo`. No es un
olvido: son funcionalidades que en la Fase 1 acordamos **explícitamente**
dejar fuera del alcance de esta v1 ("No implementar todavía: ... Órdenes de
compra ... Recepción de mercancía"). Construirlas ahora habría sido
contradecir esa decisión. Si quieres que las active ya, dímelo y las
priorizamos como una fase nueva — pero preferí avisarte en vez de dejarlas
"medio construidas" para que el menú no mostrara "Próximamente".

También quité "Gastos" del submenú: no es parte del modelo de datos de
`purchases` (no hay `Gasto` en este módulo) y no tenía ninguna vista real
detrás, ni siquiera en el diseño original.

## 2. Vista principal: `purchase_list` (nueva)
En `purchases/views.py`. Incluye exactamente lo que pediste:
- Número de compra, fecha, proveedor, estado (con color), total, usuario.
- Búsqueda por proveedor (razón social o nombre comercial), número de
  factura del proveedor, o número interno de compra (`C-00007` o solo `7`).
- Filtros por estado y por rango de fechas.
- Paginación (20 por página).
- Acciones: **Ver** (siempre), **Editar** y **Anular** (solo si sigue en
  BORRADOR — ver punto 3).

## 3. Completé dos vistas que faltaban para que el flujo cerrara bien
No estaban en el pedido original palabra por palabra, pero sin ellas el
botón "Editar" y "Anular" de tu propio listado no habrían tenido a dónde
apuntar:
- **Editar un borrador**: `purchase_create` ahora acepta un `pk` opcional
  (`/compras/<id>/editar/`) y reutiliza el mismo formulario y la misma
  lógica de guardado — nada nuevo, solo permite volver a abrir algo que ya
  se podía "guardar como borrador" pero antes no se podía retomar.
- **Anular un borrador**: `/compras/<id>/anular/` — solo funciona sobre
  compras en BORRADOR. Es seguro porque un borrador nunca tocó inventario
  ni caja (eso solo pasa al **confirmar**). Anular una compra ya
  **confirmada** es una operación distinta y más delicada (hay que revertir
  stock, caja y/o cuenta por pagar) — la dejé fuera de esta corrección para
  no salirme del alcance ya aprobado; si la quieres, la puedo construir como
  su propia fase, espejo de `cashregister.services.reversar_venta_en_caja`.

## 4. URLs (`purchases/urls.py`)
```
""              → purchase_list   (pantalla principal del módulo)
"nueva/"        → purchase_create
"<pk>/editar/"  → purchase_create (mismo view, modo edición)
"<pk>/anular/"  → purchase_borrador_anular
"<pk>/"         → purchase_detail
"api/..."       → provider_search / product_search
```
`purchase_create` y `purchase_detail` originales **no cambiaron de firma**
para quien ya los estuviera usando sin `pk` (crear) — se mantiene 100%
compatible.

## 5. Templates
- `templates/purchases/purchase_list.html` (nuevo): breadcrumb, buscador,
  filtros, tabla responsive, paginación, botón "Nueva compra" — mismo
  Design System del resto del ERP (`erp-card`, `pos.css`).
- `purchase_form.html` y `purchase_detail.html`: agregué breadcrumb y
  botones cruzados (Historial ↔ Nueva compra ↔ Editar) para que la
  navegación entre las 3 pantallas sea consistente.

## 6. Verificación realizada
- Sintaxis Python válida en los archivos tocados (`py_compile`).
- Balance de tags Django (`{% if %}`/`{% for %}`/etc.) verificado
  programáticamente en los 4 templates tocados — todos coinciden.
- Revisé que ningún otro template del ERP tuviera enlaces sueltos a
  `compras-*` vía `core:en_desarrollo` (grep completo del proyecto) — no
  quedó ninguno salvo los 2 que se dejan a propósito (punto 1).
- No pude levantar el servidor Django en este entorno (sin acceso a
  internet para instalar Django) — te pido que corras una prueba manual
  real: crear una compra de contado con caja abierta y una a crédito,
  confirmar que aparecen en el listado, que el stock del producto sube, y
  que el movimiento de caja/cuenta por pagar queda registrado.

## 7. Auditoría final — estado real
- ✅ No quedan enlaces a `core:en_desarrollo` para Nueva compra ni Historial.
- ⚠️ Sí quedan 2 enlaces a `core:en_desarrollo` (Órdenes de compra,
  Recepción de mercancía) — **a propósito**, ver nota del punto 1.
- ✅ Todas las rutas de `purchases` (list/create/edit/anular/detail/APIs)
  están registradas y no chocan entre sí.
- ✅ El módulo queda operable de punta a punta: crear → aparece en el
  listado → ver detalle → (si es borrador) editar o anular.
