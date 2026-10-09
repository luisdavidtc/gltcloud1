# Fase 2 — Sidebar (Rediseño visual GLT ERP Cloud)

## Archivo modificado
- `static/css/styles.css` — **solo CSS**, cero cambios en `base.html`, cero cambios
  en `.py`, urls, vistas o lógica de permisos/módulos. El HTML del sidebar (con toda
  su lógica `{% if %}` de módulos activos y roles) queda exactamente igual.

## Qué cambió visualmente
1. **Paleta**: el sidebar ahora usa los tokens de marca de la Fase 1
   (`--erp-brand-900` #0F2F3A petróleo, `--erp-brand-accent` #0FB9B1 turquesa) en vez
   de los colores anteriores (#0d3b38 / #17a398). Los *nombres* de las variables CSS
   (`--erp-sidebar-bg`, `--erp-sidebar-active`, etc.) se mantuvieron igual — solo
   cambié su valor — así que no hay que tocar nada más en el proyecto.
2. **Links del menú**: pasaron de franja izquierda + fondo cuadrado a "pills"
   redondeadas (radio 0.6rem) con más aire entre ellas, estilo Notion/Linear.
3. **Estado activo**: ahora es un pill turquesa sólido con texto oscuro y sombra
   suave (antes era un tinte translúcido con borde izquierdo).
4. **Submenús**: en vez de un fondo negro plano, ahora tienen una guía vertical
   sutil (línea a la izquierda) y quedan indentados — más limpio, menos "cajas
   dentro de cajas".
5. **Badge "Próximamente"**: ahora es una píldora (border-radius completo) en vez
   de un rectángulo con esquinas leves.
6. **Marca (logo + nombre)** y **footer**: más espaciado, borde inferior/superior
   más sutil, mismo contenido.
7. **Fondo del sidebar sobre el contenido**: sombra lateral más suave y profunda
   (ver `box-shadow` del `.erp-sidebar`).
8. El botón circular flotante que abre/cierra el sidebar (`.sidebar-toggle`) hereda
   automáticamente el nuevo turquesa (usa la misma variable), así que no necesitó
   cambios propios.

## Lo que NO se tocó
- Estructura HTML del sidebar (`templates/base.html`): mismos `{% url %}`, mismos
  `{% if %}` de permisos y módulos activos, mismos IDs (`erpSidebar`, `submenuCaja`,
  etc.) que usa `sidebar.js`.
- `sidebar.js`, `cash_register.js`, y el resto del JS: siguen funcionando igual,
  ninguna clase que ellos usan (`.show`, `.collapse`, `data-bs-toggle`) cambió de
  nombre ni de comportamiento.
- El submenú sigue siendo un `collapse` de Bootstrap normal (no lo convertí en
  cards todavía — eso es la Fase 3).

## Cómo probarlo
Reemplaza solo `static/css/styles.css` (o usa el zip completo). Todo el sidebar
debería verse con la nueva paleta petróleo/turquesa y los links como pills
redondeados, pero cada clic, cada submenú y cada permiso deben comportarse
exactamente igual que antes.
