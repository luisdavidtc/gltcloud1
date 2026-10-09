# Cotizaciones · entrega aditiva para GLT Cloud

## Alcance y estado
Código fuente base, no sustitución completa del ERP. Se revisó erp_modulos_por_empresa.zip
(core/modulos.py, core/permissions.py, accounts/decorators.py, inventory/models.py,
clients/models.py, sales/models.py) y pos_interfaz_parche.zip (sales/views.py y formulario).
No hay Django instalado en este entorno: no se ejecutaron migraciones, ORM, plantillas ni SMTP.
La conversión necesita aplicar TODOS los hooks de integracion/pos_backend.py.txt y los fragmentos
HTML/JS. Hasta entonces no habilitar la conversión a usuarios. No se suministran archivos completos
para reemplazar sales/views.py ni base.html porque podrían sobrescribir cambios recientes.
El bloqueo SQLite reportado anteriormente sigue pendiente de diagnóstico.

## Instalación
1. Respaldar código y BD. Probar en una copia, no producción.
2. Copiar cotizaciones/, templates/cotizaciones/, static/css/cotizaciones-tailwind.css,
   static/js/cotizaciones.js. No copiar integracion/ como aplicación.
3. INSTALLED_APPS: agregar 'cotizaciones.apps.CotizacionesConfig'.
4. erp_config/urls.py: agregar path('cotizaciones/', include('cotizaciones.urls')).
5. Crear migraciones en TU entorno, con el grafo real de dependencias:
   python manage.py makemigrations cotizaciones
   python manage.py migrate --plan
   python manage.py migrate
   python manage.py check
   python manage.py test cotizaciones
   Guardar las migraciones generadas en el repositorio antes de desplegar.
   No se incluyen migraciones fabricadas: django-simple-history también genera tablas históricas.
6. python manage.py registrar_cotizaciones
   Activa 'cotizaciones' por empresa desde el Superadministrador. No activa módulos automáticamente.
   Para mantener el catálogo futuro agrega ('cotizaciones','Cotizaciones','bi-file-earmark-text')
   a MODULOS_BASE en platform_admin/management/commands/seed_modulos.py.
   NO usar --activar-en-empresas para este registro.
7. Integrar sidebar.html, pos_template.html, pos_javascript.js y pos_backend.py.txt.
8. Asignar permisos a los grupos/usuarios según la política vigente. Los administradores de empresa
   mantienen el bypass existente; vendedores requieren permisos granulares.
   Crear requiere add_cotizacion; lista/detalle/PDF requieren view_cotizacion;
   editar change_cotizacion; aprobar aprobar_cotizacion; convertir convertir_cotizacion;
   correo enviar_cotizacion. Convertir/editar también requieren view_cotizacion en los servicios.
9. Si usas collectstatic en tu despliegue, ejecutarlo. Reiniciar servidor y recargar navegador.

## Flujo e integridad
Cotizar no requiere caja ni reserva stock. Consecutivo por empresa mediante contador único + UPDATE
atómico. No se usa MAX+1. Cantidades enteras positivas, precios no negativos, descuento 0..100.
Cliente y producto validados por tablas de disponibilidad activa, no por su empresa creadora.
IVA histórico por línea; precios ya incluyen IVA. Por defecto gravados al 19%, exentos/excluidos a 0.
Nunca sumar 19% al total que ya lo incluye. Totales calculados con Decimal en servidor.
Pendiente se puede editar/aprobar/rechazar. Aprobada queda bloqueada para edición; rechazada no se
convierte. Vencimiento es derivado de fecha_validez y bloquea conversión. Convertida es inmutable.
Se preserva auditoría de documento y líneas con django-simple-history; envíos con log separado.
Cambio de impuesto antes de venta obliga a revisar la cotización (no facturar silenciosamente).
La validez usa timezone.localdate(): el proyecto debe activar la zona horaria de empresa si hay
empresas en distintas zonas, como hace el flujo diario de caja instalado.

## Conversión
Botón POST -> POS precargado. Venta real SOLO al confirmar pago, con caja del día y permisos de ventas.
Bloquear cotización antes de crear venta. Tomar cliente, líneas/precios y descuento desde BD.
Guardar venta/pagos/inventario/caja y marcar cotización convertida en la MISMA transacción.
OneToOne de venta + bloqueo/estado impiden doble conversión en bases con bloqueo de fila.
SQLite no implementa select_for_update y sigue siendo de escritor único: probar concurrencia y
manejar OperationalError con rollback/mensaje; NO reintentar un cobro completo ciegamente.
No se cambia la tecnología ni se afirma que este módulo corrige database is locked.

## Gmail SMTP
Usar el backend de Django existente. Configuración ejemplo a integrar en settings (no sobrescribir):
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 15
Usar contraseña de aplicación de una cuenta autorizada con verificación en dos pasos, si la cuenta
lo permite; algunas cuentas administradas requieren otra política/OAuth. No contraseña principal.
No guardar secretos en Git ni enviarlos en el ZIP. Esta base usa remitente de plataforma autorizado
con nombre de empresa en asunto; no inventa credenciales Gmail por tenant. Para remitentes propios
por empresa implementar almacenamiento seguro independiente antes de ofrecerlo.
SMTP se ejecuta fuera de transacciones de venta; adjunta PDF. 'Enviado' significa aceptación SMTP,
no garantía de entrega al buzón. En esta base el envío es síncrono; para volumen, usar cola existente.
Limitar frecuencia de envíos por usuario/empresa en el middleware o infraestructura vigente.

## Tailwind
El ERP existente utiliza Bootstrap. Prefijo tw- y preflight deshabilitado evitan colisiones.
Se incluye CSS mínimo compatible para funcionar sin Node: no se afirma que fue compilado con Tailwind.
Para generar CSS real con Tailwind 3 en tu entorno:
 npx tailwindcss@3 -c tailwind_cotizaciones/tailwind.config.cjs -i tailwind_cotizaciones/input.css -o static/css/cotizaciones-tailwind.css --minify
No añadir CDN runtime global. UI: tarjetas, tabla responsive, estados, buscador con debounce,
filas dinámicas/formset y borrado mediante DELETE. El catálogo de impuestos del JS es informativo:
en filas cargadas por edición o selección manual puede mostrar 'Se confirma al guardar'.
El cliente usa selector existente; añadir autocomplete paginado por ClienteEmpresa para catálogos
muy grandes. Esta es una interfaz base, no una réplica completa del POS.

## Pruebas pendientes en Django
- Flag apagado: lista/detalle/búsqueda/PDF y POST de convertir/correo bloqueados.
- Sin permisos de acción: 403 aunque el módulo esté activo.
- Empresa A nunca consulta/edita/envía/convierte documento de B por ID manipulado.
- Cliente/producto compartido activo permitido; disponibilidad inactiva rechazada.
- Cantidad 0/negativa/decimal, NaN, precio negativo y descuento >100 rechazados.
- Precio 119000 gravado: total119000/IVA19000; exento no genera IVA; descuento10%:107100/17100.
- Crear/editar no altera stock, caja ni ventas. POST inválido conserva errores.
- Vencida/rechazada no se convierte. Caja cerrada o de ayer bloquea cobro.
- Pago mixto válido usa flujo existente; pago insuficiente revierte todo y conserva cotización.
- Doble confirmación concurrente genera una venta o error controlado, nunca dos.
- Sin stock al confirmar: rollback; cotización continúa sin venta.
- PDF multipágina y nombres largos/acentos; SMTP correcto/incorrecto registra resultado.
- Caja diaria y POS anteriores siguen funcionando (regresión).
