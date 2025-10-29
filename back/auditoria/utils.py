"""
Utilidades para registrar eventos de auditoría
"""
from .models import Auditoria
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def registrar_auditoria(usuario, nombre_tabla, pk_afectada, accion, valor_previo=None, valor_nuevo=None):
    """
    Registrar un evento de auditoría
    
    Args:
        usuario: Usuario que realizó la acción (puede ser un ID o instancia)
        nombre_tabla: Nombre de la tabla/modelo afectado
        pk_afectada: ID del registro afectado
        accion: Tipo de acción ('create', 'update', 'delete')
        valor_previo: Valores anteriores del registro (opcional)
        valor_nuevo: Nuevos valores del registro (opcional)
    """
    try:
        # Convertir usuario a instancia si es necesario
        if isinstance(usuario, (str, int)):
            try:
                usuario = User.objects.get(id=usuario)
            except User.DoesNotExist:
                usuario = None
        
        # Crear el registro de auditoría
        auditoria = Auditoria.objects.create(
            creado_por=usuario,
            actualizado_por=usuario,
            nombre_tabla=nombre_tabla,
            pk_afectada=str(pk_afectada),
            accion=accion,
            valor_previo=valor_previo,
            valor_nuevo=valor_nuevo
        )
        
        return auditoria
        
    except Exception as e:
        # Log del error pero no fallar la operación principal
        print(f"Error registrando auditoría: {e}")
        return None

def registrar_creacion(usuario, instancia, campos_auditados=None):
    """
    Registrar la creación de un registro
    
    Args:
        usuario: Usuario que creó el registro
        instancia: Instancia del modelo creado
        campos_auditados: Lista de campos a auditar (opcional, por defecto todos)
    """
    nombre_tabla = instancia._meta.model_name
    pk_afectada = instancia.pk
    
    # Obtener valores del registro creado
    valor_nuevo = {}
    if campos_auditados:
        for campo in campos_auditados:
            if hasattr(instancia, campo):
                valor_nuevo[campo] = str(getattr(instancia, campo))
    else:
        # Auditar todos los campos excepto los internos
        for field in instancia._meta.fields:
            if not field.name.startswith('_'):
                valor_nuevo[field.name] = str(getattr(instancia, field.name))
    
    return registrar_auditoria(
        usuario=usuario,
        nombre_tabla=nombre_tabla,
        pk_afectada=pk_afectada,
        accion='create',
        valor_previo=None,
        valor_nuevo=valor_nuevo
    )

def registrar_actualizacion(usuario, instancia, valores_anteriores, campos_auditados=None):
    """
    Registrar la actualización de un registro
    
    Args:
        usuario: Usuario que actualizó el registro
        instancia: Instancia del modelo actualizado
        valores_anteriores: Diccionario con los valores anteriores
        campos_auditados: Lista de campos a auditar (opcional)
    """
    nombre_tabla = instancia._meta.model_name
    pk_afectada = instancia.pk
    
    # Obtener valores nuevos y anteriores solo de campos modificados
    valor_previo = {}
    valor_nuevo = {}
    
    campos_a_revisar = campos_auditados if campos_auditados else [field.name for field in instancia._meta.fields if not field.name.startswith('_')]
    
    for campo in campos_a_revisar:
        if hasattr(instancia, campo):
            valor_actual = str(getattr(instancia, campo))
            valor_anterior = str(valores_anteriores.get(campo, ''))
            
            # Solo auditar si el valor cambió
            if valor_actual != valor_anterior:
                valor_previo[campo] = valor_anterior
                valor_nuevo[campo] = valor_actual
    
    # Solo registrar si hubo cambios
    if valor_previo or valor_nuevo:
        return registrar_auditoria(
            usuario=usuario,
            nombre_tabla=nombre_tabla,
            pk_afectada=pk_afectada,
            accion='update',
            valor_previo=valor_previo,
            valor_nuevo=valor_nuevo
        )
    
    return None

def registrar_eliminacion(usuario, instancia, campos_auditados=None):
    """
    Registrar la eliminación de un registro
    
    Args:
        usuario: Usuario que eliminó el registro
        instancia: Instancia del modelo antes de ser eliminado
        campos_auditados: Lista de campos a auditar (opcional)
    """
    nombre_tabla = instancia._meta.model_name
    pk_afectada = instancia.pk
    
    # Obtener valores del registro eliminado
    valor_previo = {}
    if campos_auditados:
        for campo in campos_auditados:
            if hasattr(instancia, campo):
                valor_previo[campo] = str(getattr(instancia, campo))
    else:
        # Auditar todos los campos excepto los internos
        for field in instancia._meta.fields:
            if not field.name.startswith('_'):
                valor_previo[field.name] = str(getattr(instancia, field.name))
    
    return registrar_auditoria(
        usuario=usuario,
        nombre_tabla=nombre_tabla,
        pk_afectada=pk_afectada,
        accion='delete',
        valor_previo=valor_previo,
        valor_nuevo=None
    )