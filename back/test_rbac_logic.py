#!/usr/bin/env python3
"""
Script de pruebas RBAC para verificar la lógica de permisos
Ejecutar: docker-compose exec backend python /app/test_rbac_logic.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giga.settings')
sys.path.insert(0, '/app')
django.setup()

from common.permissions import obtener_areas_jerarquia, obtener_rol_agente
from personas.models import Agente, Area, Rol

print("="*50)
print("PRUEBAS DE LÓGICA RBAC - SISTEMA GIGA")
print("="*50)
print()

# Contadores
total = 0
passed = 0
failed = 0

def test(name, condition, expected=True):
    global total, passed, failed
    total += 1
    
    print(f"Prueba {total}: {name}... ", end="")
    
    if condition == expected:
        print("✓ PASS")
        passed += 1
        return True
    else:
        print(f"✗ FAIL (Esperado: {expected}, Obtenido: {condition})")
        failed += 1
        return False

# PRUEBA 1: Módulos se importan correctamente
print("1. PRUEBAS DE IMPORTACIÓN")
print("-" * 50)

try:
    from common.permissions import (
        IsAuthenticatedGIGA, IsAdministrador, IsJefaturaOrAbove,
        obtener_agente_sesion, obtener_rol_agente, obtener_areas_jerarquia
    )
    test("Módulos RBAC importados", True)
except Exception as e:
    test(f"Módulos RBAC importados", False)
    print(f"  Error: {e}")

print()

# PRUEBA 2: Función obtener_areas_jerarquia con agente sin área
print("2. PRUEBAS DE obtener_areas_jerarquia()")
print("-" * 50)

class MockAgente:
    id_area = None

resultado = obtener_areas_jerarquia(MockAgente())
test("Agente sin área retorna []", resultado == [])

print()

# PRUEBA 3: Verificar datos en la base de datos
print("3. PRUEBAS DE DATOS EN BD")
print("-" * 50)

try:
    total_agentes = Agente.objects.count()
    total_roles = Rol.objects.count()
    total_areas = Area.objects.count()
    
    print(f"  Total agentes: {total_agentes}")
    print(f"  Total roles: {total_roles}")
    print(f"  Total áreas: {total_areas}")
    
    test("BD tiene agentes", total_agentes > 0)
    test("BD tiene roles", total_roles > 0)
    test("BD tiene áreas", total_areas > 0)
except Exception as e:
    print(f"  Error consultando BD: {e}")
    test("BD accesible", False)

print()

# PRUEBA 4: Verificar roles existentes
print("4. PRUEBAS DE ROLES")
print("-" * 50)

try:
    roles = Rol.objects.all().values_list('nombre', flat=True)
    print(f"  Roles en sistema: {list(roles)}")
    
    # Verificar que existan los roles principales
    roles_esperados = ['Administrador', 'Director', 'Jefatura', 'Agente']
    for rol in roles_esperados:
        existe = Rol.objects.filter(nombre=rol).exists()
        test(f"Rol '{rol}' existe", existe)
except Exception as e:
    print(f"  Error: {e}")

print()

# PRUEBA 5: Lógica de obtener_rol_agente
print("5. PRUEBAS DE obtener_rol_agente()")
print("-" * 50)

try:
    agente_test = Agente.objects.first()
    if agente_test:
        rol = obtener_rol_agente(agente_test)
        print(f"  Agente de prueba: {agente_test.nombre} {agente_test.apellido}")
        print(f"  Rol obtenido: {rol}")
        test("obtener_rol_agente() funciona", rol is not None)
    else:
        print("  No hay agentes para probar")
        test("obtener_rol_agente() funciona", False)
except Exception as e:
    print(f"  Error: {e}")
    test("obtener_rol_agente() funciona", False)

print()

# RESUMEN
print("="*50)
print("RESUMEN DE PRUEBAS")
print("="*50)
print(f"Total: {total}")
print(f"✓ Exitosas: {passed}")
print(f"✗ Fallidas: {failed}")
print()

if failed == 0:
    print("✓ TODAS LAS PRUEBAS PASARON")
    sys.exit(0)
else:
    print(f"✗ {failed} PRUEBAS FALLARON")
    sys.exit(1)
