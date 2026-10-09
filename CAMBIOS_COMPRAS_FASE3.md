# Módulo de Compras — Fase 3: Diseño visual definitivo

## Archivos modificados (solo capa visual — cero cambios de lógica)
- `templates/purchases/purchase_form.html` — reescrito con la distribución de
  3 zonas: encabezado tipo topbar (con atajos F2/F3/F8/F9), zona izquierda
  con la tabla de productos, zona derecha con las cards de Proveedor / Datos
  de la compra / Resumen financiero / Observaciones.
- `templates/purchases/purchase_detail.html` — mismo topbar oscuro, mismas
  cards del Design System.
- `static/js/purchase_form.js` — se agregó: stepper +/- de cantidad (mismo
  patrón que Remisiones), chip de proveedor seleccionado (igual que el chip
  de cliente), miniaturas de producto con el logo de GLT Cloud como
  respaldo, y atajos de teclado reales: **F2** producto, **F3** proveedor,
  **F8** guardar borrador, **F9** confirmar compra.
- **Cero archivos `.py` tocados en esta fase** — toda la lógica de
  `purchases/services.py` (Fase 2) sigue exactamente igual.

## Reutilización del Design System (como pediste, sin inventar uno nuevo)
Todo el nuevo look de Compras usa las mismas clases que ya se crearon para
Remisiones en `static/css/pos.css` — no se creó CSS nuevo:
`.erp-pos-topbar`, `.erp-pos-shortcut`, `.erp-cart-table`, `.erp-qty-stepper`,
`.erp-btn-confirmar`, `.erp-cliente-chip`, etc. Es la misma "familia visual"
en toda la app: paleta petróleo/turquesa, radios de 16px, mismas sombras.

## Decisión de diseño (con respecto al mockup que mostraste)
Mantuve una **tabla** de productos (no el grid de cards de Remisiones): en
Compras cada línea necesita varios campos editables a la vez (cantidad,
costo, descuento), y una tabla compacta es más rápida de operar por teclado
que hacer clic en cards — coherente con tu objetivo de "crear una compra
casi sin usar el mouse".

No incluí (fuera de alcance de esta fase, ya conversado):
- Card de "Costos adicionales" (flete/seguro/aduana) — es Costos de
  importación, explícitamente pospuesto para después de v1.
- Subida de adjuntos (PDF/imagen) — es la Fase 5.
- Retenciones / centro de costos — no existen en el modelo de datos de v1.

## Siguiente paso
Cuando confirmes que se ve y funciona bien, seguimos con la **Fase 4**:
Historial de compras (listado con filtros + mejoras al detalle).
