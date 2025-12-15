#!/usr/bin/env python3
"""
Script de diagnóstico para verificar imports y routing en producción
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, '/home/micaela/giga/back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giga.settings')

try:
    import django
    django.setup()
    print("✅ Django setup exitoso")
    
    # Verificar imports de personas.views
    print("\n🔍 Verificando imports de personas.views...")
    from personas import views as personas_views
    print("✅ personas.views importado correctamente")
    
    # Verificar que las funciones existen
    funciones_organigrama = [
        'get_organigrama',
        'save_organigrama', 
        'get_organigrama_historial',
        'restore_organigrama',
        'sincronizar_organigrama_manual'
    ]
    
    print("\n🔍 Verificando funciones de organigrama...")
    for func_name in funciones_organigrama:
        if hasattr(personas_views, func_name):
            print(f"  ✅ {func_name} existe")
        else:
            print(f"  ❌ {func_name} NO EXISTE")
    
    # Verificar imports de asistencia.views
    print("\n🔍 Verificando imports de asistencia.views...")
    from asistencia import views as asistencia_views
    print("✅ asistencia.views importado correctamente")
    
    # Verificar función de estado
    if hasattr(asistencia_views, 'obtener_estado_asistencia'):
        print("  ✅ obtener_estado_asistencia existe")
    else:
        print("  ❌ obtener_estado_asistencia NO EXISTE")
    
    # Verificar URLs
    print("\n🔍 Verificando configuración de URLs...")
    from django.urls import get_resolver
    from django.urls.resolvers import URLPattern, URLResolver
    
    def list_urls(lis, acc=None):
        if acc is None:
            acc = []
        if not lis:
            return
        l = lis[0]
        if isinstance(l, URLPattern):
            yield acc + [str(l.pattern)]
        elif isinstance(l, URLResolver):
            yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
        yield from list_urls(lis[1:], acc)
    
    resolver = get_resolver()
    urls_organigrama = []
    urls_asistencia = []
    
    for url in list_urls(resolver.url_patterns):
        url_str = ''.join(url)
        if 'organigrama' in url_str:
            urls_organigrama.append(url_str)
        if 'asistencia' in url_str and 'estado' in url_str:
            urls_asistencia.append(url_str)
    
    print("\n📋 URLs de organigrama encontradas:")
    if urls_organigrama:
        for url in urls_organigrama:
            print(f"  - {url}")
    else:
        print("  ❌ NO se encontraron URLs de organigrama")
    
    print("\n📋 URLs de asistencia/estado encontradas:")
    if urls_asistencia:
        for url in urls_asistencia:
            print(f"  - {url}")
    else:
        print("  ❌ NO se encontraron URLs de asistencia/estado")
    
    print("\n✅ Diagnóstico completado")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
