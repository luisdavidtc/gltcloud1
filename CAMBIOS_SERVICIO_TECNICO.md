# Rediseño UX/UI del módulo de Servicio Técnico — Nueva orden

## Alcance de esta entrega

Solo se tocó la pantalla **"Nueva orden de servicio"** (`/servicio/nueva/`),
como confirmaste. No se tocó `order_detail.html`, `order_list.html` ni
`order_print.html` — esos siguen exactamente igual.

## 0. Bug del comentario visible (arreglado en el mensaje anterior)

`{# ... #}` de Django solo comenta una línea; el comentario de varias
líneas que tenías se imprimía como texto. Se cambió a `{% comment %}...
{% endcomment %}` (si soporta multilínea) en `templates/repairs/order_form.html`.

## 1. Modal "+ Agregar equipo"

**Archivos:** `repairs/models.py`, `repairs/forms.py`, `repairs/views.py`,
`repairs/migrations/0009_repairorder_equipo_ux.py`,
`templates/repairs/order_form.html`, `static/js/order_form.js`,
`static/css/repairs.css`

- El formulario ya no muestra los campos del equipo desde el inicio.
  Aparece un botón **"+ Agregar equipo"** que abre un modal Bootstrap
  (nunca `window.prompt()`).
- Dentro del modal, en dos columnas: Marca, Modelo, Color, IMEI 1,
  IMEI 2 (opcional), Número de serie, Patrón/PIN/Contraseña, Estado
  físico, Accesorios entregados — más el campo "Equipo" (tipo de
  dispositivo) que ya existía, y "Diagnóstico inicial"/"Observaciones"
  a ancho completo.
- Campos nuevos en `RepairOrder`: `color`, `imei2`, `numero_serie`,
  `patron_acceso`, `accesorios_entregados`, `estado_fisico` — todos
  opcionales, migración aditiva.
- **Nota técnica:** los campos reales del formulario Django viven una
  sola vez en el HTML y un script los *mueve* (no los clona) dentro del
  modal al cargar la página. Así el modal es la única fuente de verdad
  — no hay que sincronizar nada manualmente al guardar, y no hay
  riesgo de ids duplicados.
- **Decisión que tomé sin preguntarte** (para no frenarte, pero avísame
  si la quieres distinta): el campo "Observaciones" que antes vivía
  suelto en la pantalla principal ahora vive dentro del modal, como
  parte de la información del equipo — no se duplicó el campo.

## 2. Guardar equipo → tarjeta resumen

- "Guardar equipo" es un botón `type="button"` (no envía el formulario):
  valida que "Equipo" no esté vacío, arma la tarjeta resumen con los
  datos ya escritos, y cierra el modal — todo en el navegador, sin
  ningún request al servidor (la orden todavía no existe hasta que
  presionas "Crear orden").
- Tarjeta resumen con ícono, título (marca + modelo), IMEI, color,
  clave, accesorios, diagnóstico inicial, estado físico, insignias rojas
  por cada ítem del checklist marcado como dañado, y miniaturas de las
  fotos adjuntadas.
- Botón "Editar información" reabre el mismo modal con todo lo que ya
  habías escrito (porque son los mismos campos, no una copia).

## 3. Checklist de estado físico

- 6 casillas (Pantalla, Cámara, Tapa/Carcasa, Botones, Micrófono,
  Parlante) como campos booleanos nuevos en el modelo — "marcado" =
  se reportó daño/observación en ese ítem.
- Se resaltan en rojo al marcarlas y aparecen como insignias en la
  tarjeta resumen.

## 4. Fotos del equipo

- Dos botones: "Tomar fotografía" (abre la cámara en celular/tablet vía
  `capture="environment"`) y "Adjuntar imágenes" (selector múltiple).
- Las fotos se acumulan en una vista previa con miniaturas y botón para
  quitar cada una, y viajan con el mismo formulario (`fotos_equipo`) al
  presionar "Crear orden" — se guardan como `RepairEvidence` (el mismo
  modelo que ya usabas para evidencias en el detalle de la orden, no se
  creó un modelo nuevo). Quedan visibles para el cliente por defecto
  (`visibilidad='cliente'`), para que sirvan de respaldo del estado de
  entrega; si prefieres que sean internas por defecto, es un solo valor
  que cambio en `repairs/views.py`.

## 5. Indicador visual del estado de la orden

- Stepper horizontal (Recibido → Diagnóstico → En reparación → Listo
  para entregar → Entregado) arriba del formulario. En "Nueva orden"
  siempre resalta "Recibido" (es el único estado posible al crear); el
  resto del recorrido se sigue controlando desde el detalle de la
  orden, que ya tenía su propio selector de transición de estado —
  no se tocó esa parte.

## 6. Atajos de teclado

- **F2**: salta al selector de Cliente.
- **F9**: si el modal de equipo está abierto, actúa como "Guardar
  equipo"; si no, envía el formulario completo ("Crear orden").
- **Esc**: cierra el modal (comportamiento nativo de Bootstrap, no
  hizo falta código adicional).

## 7. Diseño

- Mismo Design System del ERP: `--erp-radius-lg`, sombras suaves,
  colores corporativos (se reutilizan las variables ya definidas en
  `design-system.css`), iconos Bootstrap Icons, animación de entrada
  del modal igual a la que ya usa el modal de "Confirmar Venta" del
  módulo de Ventas.
- Grillas de 2 columnas en escritorio, se acomodan solas en una columna
  en pantallas angostas (Bootstrap `col-md-6` + el checklist con
  `auto-fit`, sin reglas nuevas de responsive que romper).

## Migración nueva (aplicar con `python manage.py migrate`)

- `repairs.0009_repairorder_equipo_ux` — aditiva, no borra ni renombra
  nada existente.

## Verificaciones hechas antes de esta entrega

- `python manage.py check` → sin errores.
- Migración aplicada de cero (`migrate` completo) → sin errores.
- Formulario probado en `shell`: guardado de una orden completa con
  checklist y datos del equipo → `checklist_danos` devuelve
  correctamente `['Pantalla']`.
- Sin ids de campo duplicados en el HTML renderizado (verificado
  programáticamente, los 18 campos que se mueven al modal aparecen
  una sola vez cada uno).
- `node --check` sobre `order_form.js`.
- Balance de tags Django (`{% block %}`, `{% if %}`, `{% for %}`,
  `{% comment %}`) y de `<div>` en `order_form.html`.

## Pendiente de tu lado

- Probar visualmente el modal y la cámara en un celular/tablet real
  (el `capture="environment"` no lo pude probar fuera de un navegador
  con cámara).
- Decirme si quieres que este mismo patrón (modal + tarjeta resumen)
  se extienda también al detalle/edición de una orden existente — hoy
  solo aplica a "Nueva orden", como pediste.
