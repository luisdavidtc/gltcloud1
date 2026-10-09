# ERP Celulares

Sistema ERP (MVP) para una empresa de **venta y reparación de celulares**, desarrollado con **Django** y soporte para **PostgreSQL** (con SQLite por defecto para pruebas).

## Características

- 🔐 **Autenticación y roles**: login/logout, gestión de usuarios con 3 roles (Administrador, Vendedor, Técnico) y control de acceso por rol.
- 📊 **Dashboard** con KPIs **reales** conectados a la base de datos (ventas del día/mes, ganancia del mes, equipos en reparación, inventario bajo y facturas emitidas) y un **gráfico de ventas de los últimos 7 días** (Chart.js).
- 👥 **Módulo de Clientes**: CRUD completo con búsqueda.
- 📦 **Módulo de Inventario**: productos y categorías (CRUD) con alertas de stock bajo, búsqueda y filtros.
- 🛒 **Módulo de Ventas**: creación de ventas con formulario dinámico (búsqueda de clientes y productos con autocompletado), cálculo automático de subtotal, descuentos, IVA (19%), total y ganancia en tiempo real, descuento de stock al confirmar, listado con filtros por fecha/estado, detalle y **anulación con devolución de stock**.
- 🔧 **Módulo de Servicio Técnico**: órdenes de reparación con número auto-generado, datos del equipo (marca, modelo, IMEI), falla y diagnóstico, repuestos del inventario (descuentan stock) o manuales, cálculo de costo de repuestos + mano de obra + IVA, y **workflow de estados** con validación de transiciones (recibido → diagnóstico → esperando repuestos → en reparación → reparado → entregado).
- 🎨 **Interfaz profesional tipo ERP** con Bootstrap 5, Bootstrap Icons, menú lateral fijo y diseño responsive.

> **Nota:** Los módulos de Facturación, Compras, Gastos, Proveedores y Reportes están previstos para fases posteriores.

## Tecnologías

- Python 3.11+ · Django 5.1
- PostgreSQL / SQLite
- HTML5, CSS3, JavaScript
- Bootstrap 5 + Bootstrap Icons (arquitectura MVT)

## Estructura del proyecto

```
celulares_erp/
├── erp_config/          # Configuración del proyecto
├── accounts/            # Autenticación y gestión de usuarios
├── dashboard/           # Panel principal con KPIs
├── clients/             # Módulo de clientes
├── inventory/           # Módulo de inventario (productos y categorías)
├── sales/               # Módulo de ventas (Sale, SaleItem)
├── repairs/             # Módulo de servicio técnico (RepairOrder, RepairPart)
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos (CSS, JS, imágenes)
├── media/               # Archivos subidos (imágenes de productos)
├── requirements.txt
└── manage.py
```

## Instalación

### 1. Clonar / descargar el proyecto

```bash
cd celulares_erp
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

Copia el archivo de ejemplo y ajústalo:

```bash
cp .env.example .env
```

Por defecto se usa **SQLite**. Para usar **PostgreSQL**, edita `.env`:

```env
DB_ENGINE=postgresql
DB_NAME=celulares_erp
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

> Antes de migrar con PostgreSQL, crea la base de datos:
> ```sql
> CREATE DATABASE celulares_erp;
> ```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Cargar datos iniciales

Crea el usuario administrador y las categorías de ejemplo:

```bash
python manage.py init_data
```

Esto crea:
- Usuario **admin** / contraseña **admin123** (rol Administrador)
- Categorías: Smartphones, Accesorios, Repuestos

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

Abre tu navegador en **http://localhost:8000** e inicia sesión con `admin` / `admin123`.

## Credenciales por defecto

| Usuario | Contraseña | Rol           |
|---------|------------|---------------|
| admin   | admin123   | Administrador |

> ⚠️ Cambia esta contraseña en un entorno de producción.

## Roles y permisos

- **Administrador**: acceso total (Ventas, Servicio Técnico, Inventario, Clientes, gestión de usuarios/Configuración).
- **Vendedor**: acceso a **Ventas** y **Clientes** (crear/editar).
- **Técnico**: acceso a **Servicio Técnico** y **Clientes** (solo consulta).

## Licencia

Proyecto interno · 2026 ERP Celulares.
