"""
Validación manual del flujo completo pedido en el punto 9.
Ejecutar con: python manage.py shell < _validacion_flujo.py
"""
import django
from datetime import timedelta

from django.test import Client
from django.utils import timezone

from tenants.models import Empresa
from accounts.models import CustomUser
from platform_admin.models import Modulo, EmpresaModulo
from security.models import ModuloProtegido, SecurityToken, SecurityAuthorization

def linea(msg):
    print(f"\n=== {msg} ===")

# --- Setup: empresa + usuario admin (no exento de OTP) ---
linea("Setup")
empresa, _ = Empresa.objects.get_or_create(
    nit='900123456-1',
    defaults={'nombre_comercial': 'Empresa Demo Validacion', 'estado': Empresa.Estado.ACTIVA},
)
print("Empresa:", empresa, "| Estado:", empresa.estado)

user, creado = CustomUser.objects.get_or_create(
    username='admin_validacion',
    defaults={'role': CustomUser.Roles.ADMIN, 'empresa': empresa, 'email': 'admin.validacion@example.com'},
)
if creado:
    user.set_password('Validacion123!')
    user.save()
print("Usuario:", user, "| role:", user.role, "| empresa:", user.empresa, "| email:", user.email)

# Confirmar módulo activo para la empresa (creado por la migración 0004)
activo = EmpresaModulo.objects.filter(empresa=empresa, modulo__codigo='contabilidad', activo=True).exists()
print("¿EmpresaModulo contabilidad activo para esta empresa?:", activo)
assert activo, "FALLA: el módulo contabilidad no está activo para la empresa (migración 0004 no corrió o falló)"

modulo_protegido = ModuloProtegido.objects.get(codigo='contabilidad')
print("ModuloProtegido contabilidad -> requiere_token:", modulo_protegido.requiere_token)
assert modulo_protegido.requiere_token is True

client = Client()
ok = client.login(username='admin_validacion', password='Validacion123!')
print("Login OK:", ok)
assert ok

# --- 1) El módulo aparece en el menú ---
linea("1) El módulo aparece en el menú (dashboard)")
resp = client.get('/')
contenido = resp.content.decode('utf-8')
aparece = 'Contabilidad' in contenido and '/seguridad/acceso/contabilidad/' in contenido
print("Status:", resp.status_code, "| Aparece link Contabilidad en sidebar:", aparece)
assert aparece, "FALLA: el link de Contabilidad no aparece en el sidebar"

# --- 2) Al hacer clic solicita el OTP (no abre el dashboard directo) ---
linea("2) Clic en Contabilidad -> exige OTP, no abre el Dashboard directo")
resp = client.get('/contabilidad/', follow=True)
urls_redirigidas = [r[0] for r in resp.redirect_chain]
print("Cadena de redirects:", urls_redirigidas)
print("URL final:", resp.request['PATH_INFO'])
paso_por_gate = any('/seguridad/acceso/contabilidad/' in u for u in urls_redirigidas)
llego_a_gate = '/seguridad/acceso/contabilidad/' in resp.request['PATH_INFO']
print("¿Pasó por security:gate?:", paso_por_gate or llego_a_gate)
assert paso_por_gate or llego_a_gate, "FALLA: no exigió OTP, o no llegó a la pantalla de verificación"
contenido_gate = resp.content.decode('utf-8')
print("¿Muestra 'Acceso protegido'?:", 'Acceso protegido' in contenido_gate)
assert 'Dashboard de Contabilidad' not in contenido_gate  # no debe filtrar el dashboard aun

# --- 3) El correo se envía correctamente ---
linea("3) Enviar código -> correo")
from django.conf import settings as dj_settings
dj_settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
from django.core import mail
mail.outbox = []
resp = client.post('/seguridad/acceso/contabilidad/enviar-codigo/')
data = resp.json()
print("Respuesta enviar_codigo:", data)
assert data.get('ok') is True
print("Correos en outbox:", len(mail.outbox))
assert len(mail.outbox) == 1
print("Asunto:", mail.outbox[0].subject, "| Para:", mail.outbox[0].to)

token = SecurityToken.objects.filter(usuario=user, modulo=modulo_protegido, usado=False).order_by('-creado_en').first()
print("Token creado, expira_en:", token.expira_en)

# Recuperamos el código real directamente de la vista de servicio (solo posible en test, nunca en prod: está hasheado)
from django.contrib.auth.hashers import check_password
# Interceptamos regenerando con la misma función para reobtener el código en claro solo a fines de esta prueba:
import security.services as sec_services
codigo_generado = {}
_original = sec_services.generar_y_enviar_codigo
def _wrapper(request, modulo):
    tok = _original(request, modulo)
    return tok
# (No hace falta: probamos directo el flujo real de validar con un código incorrecto y uno correcto usando el propio email)
cuerpo_correo = mail.outbox[0].body
import re
codigo_real = re.search(r'\b(\d{6})\b', cuerpo_correo).group(1)
print("Código extraído del correo:", codigo_real)

# --- 4) El código se valida ---
linea("4) Validar código incorrecto primero, luego el correcto")
resp = client.post('/seguridad/acceso/contabilidad/validar-codigo/', {'codigo': '000000'})
print("Código incorrecto ->", resp.json())
assert resp.json()['ok'] is False

resp = client.post('/seguridad/acceso/contabilidad/validar-codigo/', {'codigo': codigo_real})
print("Código correcto ->", resp.json())
assert resp.json()['ok'] is True

# --- 5) Se crea la autorización temporal ---
linea("5) Autorización temporal creada")
autorizacion = SecurityAuthorization.objects.filter(usuario=user, modulo=modulo_protegido).order_by('-autorizado_en').first()
print("Autorización:", autorizacion, "| vigente:", autorizacion.esta_vigente())
assert autorizacion is not None and autorizacion.esta_vigente()

# --- 6) Se abre el Dashboard de Contabilidad ---
linea("6) Acceso directo al Dashboard tras validar")
resp = client.get('/contabilidad/', follow=True)
contenido_dash = resp.content.decode('utf-8')
print("Status final:", resp.status_code, "| URL final:", resp.request['PATH_INFO'])
print("¿Contiene 'Módulo de Contabilidad'?:", 'Módulo de Contabilidad' in contenido_dash)
tarjetas = ['Plan de cuentas', 'Asientos contables', 'Diario General', 'Libro Mayor', 'Balance de Prueba',
            'Estado de Resultados', 'Balance General', 'Cuentas por Cobrar', 'Cuentas por Pagar',
            'Conciliación Bancaria', 'Configuración Contable']
faltantes = [t for t in tarjetas if t not in contenido_dash]
print("Tarjetas faltantes en el Dashboard:", faltantes)
assert resp.request['PATH_INFO'] == '/contabilidad/'
assert 'Módulo de Contabilidad' in contenido_dash
assert not faltantes

# --- 7) Al volver a entrar dentro del tiempo permitido no vuelve a pedir OTP ---
linea("7) Reingreso dentro de la ventana de 30 min -> no vuelve a pedir OTP")
resp = client.get('/contabilidad/', follow=True)
print("URL final:", resp.request['PATH_INFO'])
assert resp.request['PATH_INFO'] == '/contabilidad/'
assert 'Acceso protegido' not in resp.content.decode('utf-8')

# --- 8) Al expirar la autorización, vuelve a pedir OTP ---
linea("8) Autorización expirada -> vuelve a pedir OTP")
autorizacion.expira_en = timezone.now() - timedelta(minutes=1)
autorizacion.save(update_fields=['expira_en'])
resp = client.get('/contabilidad/', follow=True)
print("Cadena de redirects:", [r[0] for r in resp.redirect_chain])
print("URL final:", resp.request['PATH_INFO'])
assert '/seguridad/acceso/contabilidad/' in resp.request['PATH_INFO']
assert 'Acceso protegido' in resp.content.decode('utf-8')

# --- 9) Permisos: un rol no autorizado (vendedor) no debe ver el módulo ni acceder ---
linea("9) Rol no autorizado (vendedor) -> no ve el módulo y no puede acceder por URL")
vendedor, creado = CustomUser.objects.get_or_create(
    username='vendedor_validacion',
    defaults={'role': CustomUser.Roles.VENDEDOR, 'empresa': empresa, 'email': 'vendedor.validacion@example.com'},
)
if creado:
    vendedor.set_password('Validacion123!')
    vendedor.save()
client2 = Client()
assert client2.login(username='vendedor_validacion', password='Validacion123!')
resp = client2.get('/')
contenido_v = resp.content.decode('utf-8')
print("¿Vendedor ve 'Contabilidad' en el menú?:", 'Contabilidad' in contenido_v and '/seguridad/acceso/contabilidad/' in contenido_v)
assert not ('/seguridad/acceso/contabilidad/' in contenido_v)
resp = client2.get('/contabilidad/')
print("Status acceso directo por URL (vendedor):", resp.status_code)
assert resp.status_code == 403

print("\n>>> TODAS LAS VALIDACIONES PASARON <<<")
