# Corrección de layout: el sidebar ya no invade el contenido

## Causa raíz encontrada
`static/css/styles.css` ya tenía preparado `.erp-content { margin-left: 0;
transition: margin 0.3s ease; }` — es decir, el mecanismo para "correr" el
contenido ya existía, pero **nunca se conectó** con el estado del sidebar
(abierto/cerrado). Por eso el sidebar, al aparecer, quedaba flotando encima
de todo (incluido el título de la página) en vez de empujar el contenido.

## Archivo modificado
- `static/css/styles.css` — **solo CSS**, cero cambios en `base.html`,
  `sidebar.js`, ni en el pequeño script inline que togglea `.show` (ese
  script sigue haciendo exactamente lo mismo que hacía antes).

## Qué se agregó
```css
@media (min-width: 768px) {
    .erp-sidebar.show ~ .erp-content,
    .erp-sidebar:hover ~ .erp-content {
        margin-left: var(--erp-sidebar-width);
    }
}
```
Esto reacciona a los **mismos** estados que ya usa el sidebar hoy (la clase
`.show` que togglea el botón hamburguesa, y el `:hover` que ya usaba el
"peek" al pasar el mouse por el borde) — no inventé un estado nuevo, solo
completé la conexión que faltaba. Como `.erp-navbar` vive *dentro* de
`.erp-content`, el título, el selector de usuario, etc. se mueven
automáticamente junto con el resto (tu punto 5), sin tener que tocar nada
de eso por separado.

## Ancho del sidebar
Ya estaba en `--erp-sidebar-width: 280px` (dentro del rango 260-290px que
pediste), así que no lo cambié. Sí agregué una variante para tablet:

```css
@media (min-width: 768px) and (max-width: 991.98px) {
    :root { --erp-sidebar-width: 240px; }
}
```
Una sola variable controla el ancho del propio sidebar Y el margen que
reserva el contenido — si mañana cambias el número, todo se ajusta solo
(tu punto 8).

## Responsive (tu punto 6)
- **Escritorio (≥992px)**: contenido se desplaza (arriba).
- **Tablet (768-991px)**: mismo comportamiento, sidebar más angosto (240px).
- **Móvil (<768px)**: overlay puro — el contenido **no** se desplaza (la
  regla de arriba está condicionada a `min-width:768px`, así que en móvil
  simplemente no aplica), y el sidebar ocupa como máximo el 85% del ancho
  de pantalla para no tapar el 100%. También oculté el fondo oscuro
  (`.sidebar-backdrop`) en pantallas ≥768px: es un recurso pensado para
  cuando el sidebar flota encima del contenido (móvil); en escritorio/tablet
  ya no hace falta oscurecer nada porque el contenido se corre solo.

## Animación
Sincronicé la duración del sidebar y del contenido a **280ms** (dentro de
tu rango de 250-300ms), mismo `ease`, para que se sientan como una sola
pieza moviéndose junta, no dos animaciones independientes.

## Lo que NO se tocó
- Colores, iconos, tipografía, componentes de Bootstrap.
- `sidebar.js` (recuerda qué submenú quedó abierto) — intacto.
- El script inline que abre/cierra el sidebar con el botón hamburguesa —
  intacto, sigue togglando exactamente las mismas clases (`.show`) de
  siempre.
- Ninguna lógica de negocio, vista, o funcionalidad del ERP.
