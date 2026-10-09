# Fase 1 — Design Tokens (Rediseño visual GLT ERP Cloud)

## Archivos modificados
1. `templates/base.html` — se agregó la fuente **Inter** (además de Poppins, que se deja
   por compatibilidad) desde Google Fonts.
2. `static/css/design-system.css` — se agregaron tokens nuevos, **sin borrar ni redefinir
   nada existente**:
   - `--erp-font-family` ahora usa Inter como principal.
   - `--erp-radius-xl` (16px) para las futuras cards de módulos (Fase 3).
   - `--erp-shadow-card-hover` para el efecto hover tipo Notion/Linear.
   - Paleta de marca nueva: `--erp-brand-900` (#0F2F3A petróleo), `--erp-brand-800`
     (hover), `--erp-brand-accent` (#0FB9B1 turquesa), `--erp-app-bg` (#F6F8FA),
     `--erp-card-bg`, `--erp-card-border`, `--erp-text-muted-cool`.
   - Tokens para etiquetas de atajos de teclado: `--erp-kbd-bg`, `--erp-kbd-border`,
     `--erp-kbd-text`, y la clase `.erp-kbd` lista para usar en la Fase 4.
   - Clase `.erp-card` reutilizable (fondo blanco, radio 16px, sombra suave, hover con
     elevación) — base para el panel de cards de módulo de la Fase 3.
   - `.erp-content` ahora usa `--erp-app-bg` (#F6F8FA) como fondo del panel principal.

## Lo que NO se tocó
- `static/css/styles.css` (donde vive hoy el CSS estructural del sidebar: ancho, colapso,
  hover-zone, etc.) — eso es la Fase 2.
- Ningún archivo `.py`, url, modelo, vista, formulario ni lógica de permisos/módulos.
- Los colores de `branding_config` (`--erp-color-primario`, etc.) por empresa: siguen
  intactos y funcionando igual.

## Cómo probarlo
Solo reemplaza `templates/base.html` y `static/css/design-system.css` en tu proyecto
(o copia el proyecto completo del zip). Debería verse igual que antes, salvo:
- La tipografía general cambia sutilmente a Inter.
- El fondo del área de contenido pasa a un gris muy claro (#F6F8FA) en vez del que tuviera antes.
Nada más cambia todavía — el sidebar, las cards por módulo y los atajos vienen en las siguientes fases.
