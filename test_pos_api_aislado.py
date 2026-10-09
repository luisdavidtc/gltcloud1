"""Dobles de dependencias: no sustituye pruebas Django/browser."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

def module(name, **attrs):
    m=types.ModuleType(name); m.__dict__.update(attrs); sys.modules[name]=m; return m
class PermissionDenied(Exception): pass
class Http404(Exception): pass
class Response:
    def __init__(self,data,status=200): self.data=data;self.status_code=status
module('django');module('django.core');module('django.core.exceptions',PermissionDenied=PermissionDenied)
module('django.http',JsonResponse=Response,Http404=Http404)
lookup=MagicMock()
module('django.shortcuts',get_object_or_404=lookup)
module('django.views');module('django.views.decorators')
module('django.views.decorators.http',require_GET=lambda f:f,require_POST=lambda f:f)
module('clients');Client=MagicMock();module('clients.models',Client=Client)
module('cotizaciones');access=MagicMock();module('cotizaciones.access',exigir=access)
module('sales');save=MagicMock();module('sales.pos_documentos',guardar_documento_pos=save)
spec=importlib.util.spec_from_file_location('cotizaciones.pos_api',Path(__file__).parent/'cotizaciones/pos_api.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
class Tests(unittest.TestCase):
    def setUp(self):
        access.reset_mock(side_effect=True);access.return_value=types.SimpleNamespace(pk=3)
        lookup.reset_mock(side_effect=True);Client.reset_mock();save.reset_mock(side_effect=True)
        self.request=types.SimpleNamespace(empresa=types.SimpleNamespace(pk=3))
    def test_contact_scoped_to_company(self):
        lookup.return_value=types.SimpleNamespace(pk=7,nombre_completo='Ana',email=' ana@example.test ',celular='573001234567',telefono='')
        result=api.cliente(self.request,7)
        self.assertEqual(result.status_code,200);self.assertEqual(result.data['email'],'ana@example.test')
        Client.objects.filter.assert_called_once_with(disponibilidad__empresa=access.return_value,disponibilidad__activo=True)
    def test_permission_denied_json(self):
        access.side_effect=PermissionDenied()
        self.assertEqual(api.cliente(self.request,7).status_code,403);lookup.assert_not_called()
    def test_other_company_or_absent_not_found(self):
        lookup.side_effect=Http404()
        self.assertEqual(api.cliente(self.request,7).status_code,404)
    def test_save_delegates(self):
        save.return_value=Response({'id':1})
        self.assertEqual(api.guardar(self.request).data,{'id':1});save.assert_called_once_with(self.request)
    def test_unexpected_failure_no_secrets(self):
        save.side_effect=RuntimeError('private credentials')
        result=api.guardar(self.request)
        self.assertEqual(result.status_code,500);self.assertNotIn('credentials',str(result.data))
if __name__=='__main__': unittest.main()
