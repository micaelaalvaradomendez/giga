"""
Utilidades para cálculo de plus salarial y gestión de cronogramas.
Aprovecha la lógica existente en la base de datos.
"""

from django.db import connection, models
from django.utils import timezone
from datetime import datetime, date, time
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CalculadoraPlus:
    """Calculadora de plus salarial usando funciones SQL existentes"""
    
    @staticmethod
    def calcular_plus_mensual(agente_id, mes, anio):
        """
        Calcula el plus mensual para un agente usando la función SQL.
        Retorna el porcentaje de plus aplicable.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT calcular_plus_agente(%s, %s, %s)",
                    [agente_id, mes, anio]
                )
                resultado = cursor.fetchone()
                return resultado[0] if resultado and resultado[0] else Decimal('0.0')
        except Exception as e:
            logger.error(f"Error calculando plus para agente {agente_id}: {e}")
            return Decimal('0.0')
    
    @staticmethod
    def evaluar_reglas_plus(horas_efectivas, area_id=None):
        """
        Evalúa las reglas de plus vigentes para determinar el porcentaje aplicable.
        """
        from .models import ReglaPlus
        
        reglas = ReglaPlus.objects.filter(
            activa=True,
            vigente_desde__lte=date.today()
        ).filter(
            models.Q(vigente_hasta__isnull=True) | 
            models.Q(vigente_hasta__gte=date.today())
        ).order_by('-porcentaje_plus')
        
        for regla in reglas:
            if horas_efectivas >= regla.horas_minimas_mensuales:
                return regla.porcentaje_plus
        
        return Decimal('0.0')
    
    @staticmethod
    def generar_asignaciones_plus(mes, anio):
        """
        Genera automáticamente las asignaciones de plus para todos los agentes 
        en el período especificado.
        """
        from .models import ResumenGuardiaMes
        from personas.models import Agente
        
        agentes_procesados = 0
        asignaciones_creadas = 0
        
        # Obtener todos los agentes activos
        agentes = Agente.objects.filter(activo=True)
        
        for agente in agentes:
            try:
                # Obtener o crear resumen del mes
                resumen, created = ResumenGuardiaMes.objects.get_or_create(
                    id_agente=agente,
                    mes=mes,
                    anio=anio,
                    defaults={
                        'horas_efectivas': Decimal('0.0'),
                        'porcentaje_plus': Decimal('0.0'),
                        'estado_plus': 'pendiente'
                    }
                )
                
                # Calcular plus automáticamente
                if resumen.calcular_plus_automatico():
                    resumen.save()
                    asignaciones_creadas += 1
                
                agentes_procesados += 1
                
            except Exception as e:
                logger.error(f"Error procesando agente {agente.id_agente}: {e}")
                continue
        
        return {
            'agentes_procesados': agentes_procesados,
            'asignaciones_creadas': asignaciones_creadas,
            'periodo': f"{mes}/{anio}"
        }


class PlanificadorCronograma:
    """Planificador automático de cronogramas aprovechando la estructura existente"""
    
    @staticmethod
    def planificar_automatico(area_id, fecha_inicio, fecha_fin, agentes_ids=None):
        """
        Planifica automáticamente guardias para un período determinado.
        """
        from .models import Cronograma, Guardia
        from personas.models import Agente, Area
        
        try:
            area = Area.objects.get(id_area=area_id)
            
            # Crear cronograma base
            cronograma = Cronograma.objects.create(
                id_area=area,
                tipo='automatico',
                hora_inicio=time(8, 0),  # 8:00 AM por defecto
                hora_fin=time(20, 0),    # 8:00 PM por defecto
                estado='generada',
                fecha_creacion=date.today()
            )
            
            # Si no se especifican agentes, usar todos los activos del área
            if not agentes_ids:
                agentes = Agente.objects.filter(id_area=area, activo=True)
            else:
                agentes = Agente.objects.filter(id_agente__in=agentes_ids, activo=True)
            
            # Distribuir guardias de manera equitativa
            guardias_creadas = PlanificadorCronograma._distribuir_guardias(
                cronograma, agentes, fecha_inicio, fecha_fin
            )
            
            return {
                'cronograma_id': cronograma.id_cronograma,
                'guardias_creadas': guardias_creadas,
                'agentes_asignados': len(agentes),
                'periodo': f"{fecha_inicio} - {fecha_fin}"
            }
            
        except Exception as e:
            logger.error(f"Error en planificación automática: {e}")
            return None
    
    @staticmethod
    def _distribuir_guardias(cronograma, agentes, fecha_inicio, fecha_fin):
        """Distribuye las guardias de manera equitativa entre los agentes"""
        from .models import Guardia
        from datetime import timedelta
        
        guardias_creadas = 0
        fecha_actual = fecha_inicio
        agente_index = 0
        
        while fecha_actual <= fecha_fin:
            # Verificar si es feriado
            if not ValidadorHorarios.es_feriado(fecha_actual):
                agente = agentes[agente_index % len(agentes)]
                
                # Crear guardia
                Guardia.objects.create(
                    id_cronograma=cronograma,
                    id_agente=agente,
                    fecha=fecha_actual,
                    hora_inicio=cronograma.hora_inicio,
                    hora_fin=cronograma.hora_fin,
                    tipo='automatica',
                    estado='programada',
                    activa=True,
                    horas_planificadas=8  # 8 horas por defecto
                )
                
                guardias_creadas += 1
                agente_index += 1
            
            fecha_actual += timedelta(days=1)
        
        return guardias_creadas
    
    @staticmethod
    def validar_disponibilidad(agente_id, fecha_hora):
        """
        Valida si un agente está disponible para una guardia específica.
        """
        from asistencia.models import Licencia
        from .models import Guardia
        
        fecha = fecha_hora.date() if isinstance(fecha_hora, datetime) else fecha_hora
        
        # Verificar licencias
        licencias_activas = Licencia.objects.filter(
            id_agente_id=agente_id,
            fecha_desde__lte=fecha,
            fecha_hasta__gte=fecha,
            estado='aprobada'
        ).exists()
        
        if licencias_activas:
            return False, "Agente con licencia aprobada"
        
        # Verificar guardias existentes
        guardias_existentes = Guardia.objects.filter(
            id_agente_id=agente_id,
            fecha=fecha,
            activa=True
        ).exists()
        
        if guardias_existentes:
            return False, "Agente ya tiene guardia asignada"
        
        return True, "Agente disponible"


class ValidadorHorarios:
    """Validador de horarios usando parámetros de área y feriados"""
    
    @staticmethod
    def validar_ventana_horaria(agente_id, timestamp, tipo_marca):
        """
        Valida si una marca está dentro de la ventana horaria permitida.
        """
        from .models import ParametrosArea
        from personas.models import Agente
        
        try:
            agente = Agente.objects.get(id_agente=agente_id)
            
            # Obtener parámetros vigentes del área
            parametros = ParametrosArea.objects.filter(
                id_area=agente.id_area,
                activo=True,
                vigente_desde__lte=timestamp.date()
            ).filter(
                models.Q(vigente_hasta__isnull=True) | 
                models.Q(vigente_hasta__gte=timestamp.date())
            ).first()
            
            if not parametros:
                return True, "Sin parámetros configurados"
            
            hora_marca = timestamp.time()
            
            if tipo_marca == 'entrada':
                if parametros.ventana_entrada_inicio <= hora_marca <= parametros.ventana_entrada_fin:
                    return True, "Entrada en horario"
                else:
                    return False, f"Entrada fuera de ventana ({parametros.ventana_entrada_inicio}-{parametros.ventana_entrada_fin})"
            
            elif tipo_marca == 'salida':
                if parametros.ventana_salida_inicio <= hora_marca <= parametros.ventana_salida_fin:
                    return True, "Salida en horario"
                else:
                    return False, f"Salida fuera de ventana ({parametros.ventana_salida_inicio}-{parametros.ventana_salida_fin})"
            
            return False, "Tipo de marca no reconocido"
            
        except Exception as e:
            logger.error(f"Error validando ventana horaria: {e}")
            return False, "Error en validación"
    
    @staticmethod
    def es_feriado(fecha):
        """Verifica si una fecha es feriado usando la función SQL"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT es_feriado(%s)", [fecha])
                resultado = cursor.fetchone()
                return resultado[0] if resultado else False
        except Exception as e:
            logger.error(f"Error verificando feriado: {e}")
            return False
    
    @staticmethod
    def obtener_parametros_area(area_id, fecha_consulta=None):
        """Obtiene los parámetros vigentes de un área usando la función SQL"""
        if not fecha_consulta:
            fecha_consulta = date.today()
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM obtener_parametros_area(%s, %s)",
                    [area_id, fecha_consulta]
                )
                resultado = cursor.fetchone()
                if resultado:
                    return {
                        'ventana_entrada_inicio': resultado[0],
                        'ventana_entrada_fin': resultado[1],
                        'ventana_salida_inicio': resultado[2],
                        'ventana_salida_fin': resultado[3],
                        'tolerancia_entrada_min': resultado[4],
                        'tolerancia_salida_min': resultado[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo parámetros de área: {e}")
            return None


class NotificacionManager:
    """Gestor de notificaciones para cronogramas y plus"""
    
    @staticmethod
    def notificar_cronograma_publicado(cronograma_id):
        """Notifica cuando un cronograma es publicado"""
        # TODO: Implementar sistema de notificaciones
        logger.info(f"Cronograma {cronograma_id} publicado")
        return True
    
    @staticmethod
    def notificar_plus_calculado(resumen_id):
        """Notifica cuando se calcula un plus"""
        # TODO: Implementar sistema de notificaciones
        logger.info(f"Plus calculado para resumen {resumen_id}")
        return True
    
    @staticmethod
    def notificar_guardia_asignada(guardia_id):
        """Notifica cuando se asigna una nueva guardia"""
        # TODO: Implementar sistema de notificaciones
        logger.info(f"Guardia {guardia_id} asignada")
        return True