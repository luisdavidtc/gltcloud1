"""Pruebas aisladas con dobles; no sustituyen Django, DB ni SMTP real."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from datetime import date

class PermissionDenied(Exception): pass
class ValidationError(Exception): pass

def module(name, **kwargs):
    mod=types.ModuleType(name);mod.__dict__.update(kwargs);sys.modules[name]=mod;return mod
module('django');module('django.conf',settings=types.SimpleNamespace(DEFAULT_FROM_EMAIL='erp@example.test'))
module('django.core');module('django.core.exceptions',PermissionDenied=PermissionDenied,ValidationError=ValidationError)
def validate_email(value):
    if not value or '@' not in value: raise ValidationError()
module('django.core.validators',validate_email=validate_email)
mail=MagicMock();mail.return_value.send.return_value=1
module('django.core.mail',EmailMultiAlternatives=mail)
module('cotizaciones');access=MagicMock(return_value=types.SimpleNamespace(pk=1))
module('cotizaciones.access',exigir=access)
model=MagicMock();module('cotizaciones.models',EnvioCotizacion=model)
pdf=MagicMock(return_value=b'%PDF-test');module('cotizaciones.pdf',generar_pdf=pdf)
spec=importlib.util.spec_from_file_location('cotizaciones.correo',Path(__file__).parent/'cotizaciones/correo.py')
correo=importlib.util.module_from_spec(spec);spec.loader.exec_module(correo)
class PruebasCorreo(unittest.TestCase):
    def setUp(self):
        access.reset_mock(side_effect=True); access.return_value=types.SimpleNamespace(pk=1)
        model.reset_mock();mail.reset_mock(side_effect=True);mail.return_value.send.side_effect=None;mail.return_value.send.return_value=1
        pdf.reset_mock(side_effect=True);pdf.return_value=b'%PDF-test'
        self.req=types.SimpleNamespace(user='usuario')
        self.cot=types.SimpleNamespace(pk=8,empresa_id=1,empresa=types.SimpleNamespace(nombre_comercial='ERP'),cliente=types.SimpleNamespace(email='cliente@example.test'),codigo='COT-000008',fecha_validez=date(2026,10,18))
    def test_exito_adjunta_pdf_y_registra(self):
        result=correo.enviar_cotizacion(self.req,self.cot)
        self.assertTrue(result['correo_enviado']);mail.return_value.attach.assert_called_once_with('COT-000008.pdf',b'%PDF-test','application/pdf');model.objects.create.assert_called_once()
    def test_fallo_smtp_sin_filtrar_secreto(self):
        mail.return_value.send.side_effect=OSError('password secreto')
        result=correo.enviar_cotizacion(self.req,self.cot)
        self.assertFalse(result['correo_enviado']);self.assertNotIn('secreto',str(result));self.assertEqual(model.objects.create.return_value.error,'OSError')
    def test_backend_no_confirma(self):
        mail.return_value.send.return_value=0
        self.assertFalse(correo.enviar_cotizacion(self.req,self.cot)['correo_enviado'])
    def test_sin_correo(self):
        self.cot.cliente.email=''
        self.assertFalse(correo.enviar_cotizacion(self.req,self.cot)['correo_enviado']);mail.assert_not_called()
    def test_otra_empresa_bloqueada(self):
        self.cot.empresa_id=2
        with self.assertRaises(PermissionDenied): correo.enviar_cotizacion(self.req,self.cot)
        mail.assert_not_called()
    def test_sin_permiso_no_envia(self):
        access.side_effect=PermissionDenied()
        self.assertFalse(correo.intentar_envio(self.req,self.cot)['correo_enviado']);mail.assert_not_called()
    def test_fallo_pdf_no_es_exito(self):
        pdf.side_effect=RuntimeError('fallo')
        self.assertFalse(correo.enviar_cotizacion(self.req,self.cot)['correo_enviado']);mail.assert_not_called()
if __name__=='__main__':unittest.main()
