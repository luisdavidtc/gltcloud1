# Cambios posteriores a la entrega de sucursales

## Métodos de pago con saldo (BANCO BANCOLOMBIA, ADDI, BANCO BBVA, CAJA MAYOR)
- Cada método de pago lleva un libro de movimientos y un saldo (`company.models.MovimientoMetodoPago`, lógica en `company/tesoreria.py`).
- Configuración → Métodos de pago: saldo por método y botón **Movimientos** (por fecha, saldo acumulado, filtros, movimientos manuales). Vista: `company/views_tesoreria.py`.
- Al cerrar una caja (manual o automático) se acreditan los saldos vía señal `post_save` de `CashSession` (conectada en `company/apps.py`): cada método recibe lo vendido y CAJA MAYOR recibe el efectivo neto del día (saldo final − saldo inicial).
- Compras de contado: campo "Pagar con" (`Compra.metodo_pago`); con un método que lleva saldo se descuenta de ese saldo, sin exigir caja abierta. Sin método o con Efectivo, flujo de caja de siempre. Saldo insuficiente = la compra no se confirma.
- CAJA MAYOR no se ofrece en el POS (`PaymentMethod.activos_de`). "CREDITOS" es el método de sistema `credito` ya existente.
- Migraciones: `company.0010`, `company.0011` (crea los 4 métodos en las empresas existentes), `purchases.0003`.
- Pruebas: `company/tests_tesoreria.py`, `purchases/tests_metodo_pago.py`.

## Login con correo + clave (sin OTP)
- `accounts/views.py::login_view` y `templates/accounts/login.html`. Mensaje único de error, límite de intentos (5 por correo+IP en 15 min, `MAX_INTENTOS_CLAVE`), auditoría en `LoginAccessLog`.
- Las vistas OTP (`login_verificar`, `login_reenviar_codigo`) siguen en el código pero el login ya no las usa.
- Pruebas: `accounts/tests_login_password.py`; `tenants/tests.py` adaptado al nuevo login.

## Pendiente (decisión abierta)
Un producto recibido por traslado en una sucursal que no lo tiene no aparece en su POS: `sales/views.py` (`product_search`, `sale_create`), `inventory/views.py` y `purchases/views.py` filtran por `Product.empresa` (dueño). Hay que decidir entre catálogo único compartido o copia propia por sucursal, y qué precio de venta tendrá el producto nuevo.

## Cómo probar
`python manage.py check`, `python manage.py makemigrations --check` y
`python manage.py test accounts accounting cashregister clients company core cotizaciones dashboard dian_einvoicing inventory localization platform_admin providers purchases repairs reports sales security tenants`
(no uses `manage.py test` sin argumentos: falla por scripts sueltos `test_*_aislado.py` de la raíz).
Antes de usar: `python manage.py migrate` (probado sobre una copia de tu base).
