# Simplificación del submenú de Facturación

## Archivo modificado
- `templates/base.html` — solo el bloque `submenuFacturacion` dentro del sidebar.
  Nada de `.py`, urls, vistas, modelos ni permisos.

## Antes (7 ítems)
Punto de Venta (POS) · Remisiones (Próximamente) · Factura electrónica (Próximamente)
· Despachos (Próximamente) · Pendientes por facturar (Próximamente) · Historial
· Cotizaciones (Próximamente) · Notas crédito (Próximamente)

## Ahora (3 ítems)
1. **Remisiones** → apunta a `sales:sale_create` (la MISMA vista que antes se
   llamaba "Punto de Venta (POS)"). No se creó ninguna vista nueva ni se movió
   nada: solo se le cambió el nombre y el ícono (de carrito a camión) porque hoy
   eso es lo que realmente le entregas al cliente.
2. **Factura electrónica** → se queda igual, sigue como "Próximamente"
   (`core:en_desarrollo`).
3. **Historial** → apunta a `sales:sale_list`, igual que antes.

## Lo que se quitó del menú (no de la base de datos)
- Remisiones (el placeholder viejo "Próximamente" — ya no aplica, porque ahora
  Remisiones apunta a la venta real).
- Despachos, Pendientes por facturar, Cotizaciones, Notas crédito — eran
  placeholders sin funcionalidad ("Próximamente"). Las quité del menú para
  reducir ruido, tal como pediste. Sus URLs (`core:en_desarrollo` con esos
  slugs) siguen existiendo en el sistema por si más adelante las quieres
  reactivar — solo dejaron de estar enlazadas desde el sidebar.

## Nota para tu consistencia (no lo cambié, solo te lo señalo)
El botón "Nueva venta" que aparece en `templates/sales/sale_list.html` y en
`templates/dashboard/index.html` sigue diciendo "Nueva venta" (no "Nueva
remisión"). Apunta a la misma vista `sale_create`, así que funciona igual —
pero si quieres que el lenguaje sea 100% consistente en toda la app, dímelo y
lo ajusto también.
