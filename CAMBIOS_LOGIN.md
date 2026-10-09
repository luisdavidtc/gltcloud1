# Rediseño del Login — GLT Cloud ERP

## Archivos
- `templates/accounts/login.html` — reescrito completo.
- `static/css/login.css` — nuevo, usa exclusivamente los tokens ya definidos
  en `design-system.css` (Fase 1 del rediseño): paleta petróleo/turquesa,
  radios, sombras, tipografía Inter. No define colores nuevos.

## Cero cambios de backend (verificado)
- `accounts/views.py::login_view` — sin tocar.
- `accounts/forms.py::LoginForm` — sin tocar.
- `accounts/urls.py` — sin tocar.
- El `<form method="post">` sigue usando `{{ form.username }}` y
  `{{ form.password }}` tal cual los renderiza Django — mismos `name=`,
  mismo `id=`, misma validación, mismo CSRF. `login_view` no se enteró de
  que el HTML cambió.

## Distribución (40/60, como pediste)
- **Izquierda (40%)**: fondo oscuro petróleo con gradiente + un patrón sutil
  de puntos (CSS puro, sin foto — más abajo explico por qué), logo GLT
  Cloud arriba, "Bienvenido a GLT Cloud" + subtítulo, y la grilla de 6
  módulos con ícono (Facturación, Inventario, Compras, Ventas, Clientes,
  Reportes).
- **Derecha (60%)**: fondo blanco, todo centrado, título "Bienvenido al
  Sistema POS GLT Cloud", subtítulo, formulario con íconos en los campos,
  mostrar/ocultar contraseña, checkbox Recordarme, enlace de contraseña,
  botón grande turquesa "Ingresar al sistema", versión del sistema, y el
  footer de derechos de autor.

## Por qué no usé una foto de fondo
Pediste "imagen de fondo relacionada con tecnología" — no tengo una foto
tuya con licencia para eso, y generar/buscar una imagen de stock para
incrustarla en tu producto comercial no es algo que pueda hacer con
garantías de derechos de uso. En su lugar hice un fondo 100% CSS
(gradiente + patrón de puntos + un resplandor turquesa sutil) que da la
misma sensación "tech/premium" sin depender de ningún archivo externo. Si
tienes una foto con licencia que quieras usar, la puedo incorporar como
`background-image` en dos líneas de CSS.

## Dos elementos que pediste pero son solo visuales por ahora (con tu regla de "no tocar backend", así debía ser)
- **"Recordarme"**: el checkbox está ahí, pero `LoginForm` no tiene ese
  campo, así que hoy no extiende la duración de la sesión. Si lo quieres
  funcional, es un cambio pequeño y aditivo a `LoginForm` (un campo
  opcional) + una línea en `login_view` para ajustar
  `request.session.set_expiry(...)` — dime y lo hago como su propia tarea.
- **"¿Olvidó su contraseña?"**: el enlace está ahí (`href="#"`), pero no
  existe todavía un flujo de recuperación de contraseña en el proyecto
  (no hay URL ni vista para eso). Mismo trato: lo dejo visible tal como
  lo pediste, pero no inventé una ruta falsa.

## Accesibilidad
- Autofocus en Usuario: ya lo traía `LoginForm` (`'autofocus': True` en el
  widget), se mantiene intacto.
- Enter envía el formulario: comportamiento nativo del navegador, no se
  interceptó con JS en ningún campo.
- Tab sigue el orden natural del DOM (usuario → contraseña → botón
  mostrar/ocultar con `tabindex="-1"` para no interrumpir el flujo →
  recordarme → olvidó contraseña → enviar).
- El único JS agregado es el toggle de mostrar/ocultar contraseña (cambia
  `type="password"` ↔ `type="text"`) — no interfiere con la validación ni
  con el envío del formulario.

## Responsive
Debajo de 860px el layout pasa de 2 columnas a apilado (el panel oscuro
arriba, más compacto, formulario abajo) — probado en el CSS con un solo
media query, sin duplicar reglas.

## Actualización: foto de fondo real
Agregaste una foto (tablet POS en un restaurante) y pediste usarla — la
guardé en `static/img/login-bg.jpg` y actualicé `static/css/login.css`:
- El panel izquierdo ahora usa esa foto como `background-image`.
- Encima va el overlay oscuro degradado (petróleo, ~90-96% de opacidad)
  que ya pedías en el brief original, para que el texto siga siendo
  perfectamente legible.
- Quité el patrón de puntos decorativo que había puesto como sustituto:
  con una foto real de por medio, esa capa extra ensuciaba la imagen en
  vez de sumar. El resplandor turquesa de la esquina inferior se mantiene.

Nota técnica: los archivos `.css` no pasan por el motor de plantillas de
Django, así que la ruta a la imagen es relativa (`../img/login-bg.jpg`,
resuelta por el navegador desde la ubicación del propio CSS) en vez de usar
`{% static %}` — el resultado visual es el mismo, solo cambia cómo se
referencia el archivo.

## Actualización: "¿Olvidó su contraseña?" abre soporte por WhatsApp
El enlace ahora abre un modal (Bootstrap, sin backend) con un botón que
lleva directo a WhatsApp: `https://wa.me/573024971675` con un mensaje
pre-escrito. El número que diste (3024971675) se guardó en formato
internacional (+57) para que el enlace `wa.me` funcione tanto en celular
como en computador. Cero cambios de backend — sigue siendo 100% frontend.
