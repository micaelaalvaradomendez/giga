"""
Utilidades para cálculo de plus salarial y gestión de cronogramas.
Aprovecha la lógica existente en la base de datos.
"""

from django.db import connection, models
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
    def calcular_plus_simplificado(agente_id, mes, anio):
        """
        Calcula el plus según las reglas del convenio colectivo:
        
        OPERATIVOS:
        - >= 8 horas  → 40% plus
        - 1-7 horas   → 20% plus
        - 0 horas     → 0% plus
        
        ADMINISTRATIVOS (y otras áreas):
        - >= 32 horas → 40% plus
        - 1-31 horas  → 20% plus
        - 0 horas     → 0% plus
        """
        try:
            from personas.models import Agente
            from django.db.models import Sum
            
            # Obtener agente y área
            agente = Agente.objects.get(id_agente=agente_id)
            area_nombre = agente.id_area.nombre.lower() if agente.id_area else ""
            
            # Determinar si es área operativa
            areas_operativas = [
                'secretaría de protección civil',
                'departamento operativo',
                'operativo',
                'emergencias',
                'rescate'
            ]
            es_area_operativa = any(op in area_nombre for op in areas_operativas)
            
            # Obtener horas de guardia en el mes
            from .models import Guardia, HoraCompensacion
            from datetime import date
            
            fecha_inicio = date(anio, mes, 1)
            if mes == 12:
                fecha_fin = date(anio + 1, 1, 1)
            else:
                fecha_fin = date(anio, mes + 1, 1)
            
            # Horas de guardias regulares
            guardias_mes = Guardia.objects.filter(
                id_agente=agente_id,
                fecha__gte=fecha_inicio,
                fecha__lt=fecha_fin,
                activa=True,
                estado='planificada'
            )
            
            total_horas_guardias = guardias_mes.aggregate(
                total=Sum('horas_efectivas')
            )['total'] or 0
            
            # Horas de compensación aprobadas
            compensaciones_aprobadas = HoraCompensacion.objects.filter(
                id_agente=agente_id,
                fecha_servicio__gte=fecha_inicio,
                fecha_servicio__lt=fecha_fin,
                estado='aprobada'
            )
            
            horas_compensacion = compensaciones_aprobadas.aggregate(
                total=Sum('horas_extra')
            )['total'] or 0
            
            # Sumar horas regulares + horas de compensación
            total_horas_completas = total_horas_guardias + horas_compensacion
            
            # APLICAR REGLAS CORREGIDAS
            if es_area_operativa:
                # ÁREA OPERATIVA
                if total_horas_completas >= 8:
                    return Decimal('40.0')
                elif total_horas_completas > 0:
                    return Decimal('20.0')
                else:
                    return Decimal('0.0')
            else:
                # ÁREA ADMINISTRATIVA (O CUALQUIER OTRA)
                if total_horas_completas >= 32:
                    return Decimal('40.0')
                elif total_horas_completas > 0:
                    return Decimal('20.0')
                else:
                    return Decimal('0.0')
                
        except Exception as e:
            logger.error(f"Error calculando plus simplificado para agente {agente_id}: {e}")
            return Decimal('0.0')
    
    @staticmethod
    def evaluar_reglas_plus(horas_efectivas, area_id=None):
        """
        Evalúa las reglas de plus vigentes para determinar el porcentaje aplicable.
        DEPRECADO: Usar calcular_plus_simplificado en su lugar.
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
    def validar_fecha_guardia(fecha):
        """
        Valida que la fecha sea apta para programar guardias.
        Las guardias solo pueden ser en fines de semana (sábado y domingo) o feriados.
        """
        from datetime import datetime
        from asistencia.views import es_dia_laborable, get_motivo_no_laborable
        
        # Usar la función de asistencia que ya considera feriados
        es_laborable = es_dia_laborable(fecha)
        
        if not es_laborable:
            # No es día laborable (es fin de semana o feriado)
            motivo = get_motivo_no_laborable(fecha)
            return True, f"Fecha válida para guardia: {motivo}"
        
        # Es día laborable (lunes a viernes normal) - no permitido para guardias
        return False, "Las guardias solo pueden programarse en fines de semana (sábado y domingo) o feriados"
    
    @staticmethod
    def validar_duracion_guardia(hora_inicio, hora_fin):
        """
        Valida que la duración de la guardia no exceda el límite normativo.
        Máximo 10 horas por día según CCT.
        """
        from datetime import datetime, timedelta
        
        # Calcular duración
        inicio = datetime.combine(datetime.today().date(), hora_inicio)
        fin = datetime.combine(datetime.today().date(), hora_fin)
        
        # Si la hora fin es menor, asume que cruza medianoche
        if fin < inicio:
            fin += timedelta(days=1)
        
        duracion = fin - inicio
        horas_duracion = duracion.total_seconds() / 3600
        
        if horas_duracion > 10:
            return False, f"La guardia excede el límite de 10 horas (duración: {horas_duracion:.1f}h)"
        
        return True, f"Duración válida: {horas_duracion:.1f} horas"
    
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
    
    @staticmethod
    def validar_horas_compensacion(hora_inicio_programada, hora_fin_programada, hora_fin_real):
        """
        Valida una solicitud de horas de compensación.
        
        Args:
            hora_inicio_programada (time): Hora de inicio programada de la guardia
            hora_fin_programada (time): Hora de fin programada de la guardia  
            hora_fin_real (time): Hora real de finalización del servicio
            
        Returns:
            tuple: (es_valida, mensaje, horas_extra)
        """
        from datetime import datetime, timedelta
        
        try:
            # Calcular duración programada
            inicio = datetime.combine(datetime.today().date(), hora_inicio_programada)
            fin_programado = datetime.combine(datetime.today().date(), hora_fin_programada)
            fin_real = datetime.combine(datetime.today().date(), hora_fin_real)
            
            # Manejar cruces de medianoche
            if fin_programado < inicio:
                fin_programado += timedelta(days=1)
            if fin_real < inicio:
                fin_real += timedelta(days=1)
            
            # Validar que la hora real sea posterior a la programada
            if fin_real <= fin_programado:
                return False, "La hora fin real debe ser posterior a la hora fin programada", 0
            
            # Calcular horas
            duracion_programada = (fin_programado - inicio).total_seconds() / 3600
            duracion_real = (fin_real - inicio).total_seconds() / 3600
            horas_extra = duracion_real - duracion_programada
            
            # Validar límites razonables
            if horas_extra > 8:
                return False, f"No se pueden registrar más de 8 horas extra por servicio (solicitadas: {horas_extra:.1f}h)", 0
            
            if duracion_real > 18:  # Máximo 18 horas de servicio total
                return False, f"El servicio total no puede exceder 18 horas (registradas: {duracion_real:.1f}h)", 0
            
            return True, f"Compensación válida: {horas_extra:.1f} horas extra", horas_extra
            
        except Exception as e:
            logger.error(f"Error validando horas de compensación: {e}")
            return False, "Error en validación de compensación", 0
    
    @staticmethod
    def calcular_valor_hora_compensacion(agente, horas_extra):
        """
        Calcula el valor monetario de las horas de compensación.
        
        Args:
            agente: Instancia del agente
            horas_extra (float): Cantidad de horas extra trabajadas
            
        Returns:
            tuple: (valor_por_hora, monto_total)
        """
        try:
            # Obtener salario base del agente (esto dependerá de cómo esté implementado)
            # Por ahora, usar un valor base de referencia
            salario_base_mensual = Decimal('500000.0')  # Valor ejemplo
            horas_mensuales_normales = Decimal('160.0')  # 20 días x 8 horas
            
            # Calcular valor hora normal
            valor_hora_normal = salario_base_mensual / horas_mensuales_normales
            
            # Las horas extra se pagan con recargo del 50%
            valor_hora_extra = valor_hora_normal * Decimal('1.5')
            
            # Calcular monto total
            monto_total = valor_hora_extra * Decimal(str(horas_extra))
            
            return valor_hora_extra, monto_total
            
        except Exception as e:
            logger.error(f"Error calculando valor de compensación: {e}")
            return Decimal('0.0'), Decimal('0.0')
    
    @staticmethod
    def puede_solicitar_compensacion(agente, fecha_servicio):
        """
        Verifica si un agente puede solicitar compensación para una fecha dada.
        
        Args:
            agente: Instancia del agente
            fecha_servicio (date): Fecha del servicio prestado
            
        Returns:
            tuple: (puede_solicitar, mensaje)
        """
        from datetime import datetime, timedelta
        
        try:
            # Verificar que no haya pasado más de 30 días
            dias_transcurridos = (datetime.now().date() - fecha_servicio).days
            if dias_transcurridos > 30:
                return False, f"No se puede solicitar compensación después de 30 días (transcurridos: {dias_transcurridos})"
            
            # Verificar que no exista ya una solicitud para esa fecha
            from .models import HoraCompensacion
            solicitud_existente = HoraCompensacion.objects.filter(
                id_agente=agente,
                fecha_servicio=fecha_servicio
            ).exists()
            
            if solicitud_existente:
                return False, "Ya existe una solicitud de compensación para esta fecha"
            
            # Verificar que el agente tenía guardia programada ese día
            from .models import Guardia
            guardia_programada = Guardia.objects.filter(
                id_agente=agente,
                fecha=fecha_servicio,
                activa=True
            ).exists()
            
            if not guardia_programada:
                return False, "No hay guardia programada para esta fecha"
            
            return True, "Puede solicitar compensación"
            
        except Exception as e:
            logger.error(f"Error verificando solicitud de compensación: {e}")
            return False, "Error en validación de solicitud"


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


# ============================================================================
# SISTEMA DE APROBACIÓN JERÁRQUICA
# ============================================================================

def get_approval_hierarchy(creado_por_rol):
    """
    Retorna qué roles pueden aprobar un cronograma según quién lo creó.
    
    Jerarquía:
    - Jefatura crea → Director o Administrador aprueba
    - Director crea → Administrador aprueba
    - Administrador crea → Auto-aprobado (no requiere aprobación)
    
    Args:
        creado_por_rol (str): Rol del agente que creó el cronograma
        
    Returns:
        list: Lista de roles que pueden aprobar
    """
    if not creado_por_rol:
        return ['administrador']
    
    rol_lower = creado_por_rol.lower().strip()
    
    if rol_lower == 'jefatura':
        return ['director', 'administrador']
    elif rol_lower == 'director':
        return ['administrador']
    elif rol_lower == 'administrador':
        return []  # Auto-aprobado, no requiere aprobación adicional
    
    # Por defecto, solo administrador puede aprobar
    return ['administrador']


def puede_aprobar(cronograma, rol_aprobador):
    """
    Verifica si un agente con un rol específico puede aprobar un cronograma.
    
    Args:
        cronograma: Instancia de Cronograma
        rol_aprobador (str): Rol del agente que intenta aprobar
        
    Returns:
        bool: True si puede aprobar, False en caso contrario
    """
    if not cronograma.creado_por_rol:
        # Si no hay rol de creador, solo administrador puede aprobar
        return rol_aprobador.lower().strip() == 'administrador'
    
    # Administrador SIEMPRE puede aprobar cualquier cronograma
    if rol_aprobador.lower().strip() == 'administrador':
        return True
    
    roles_permitidos = get_approval_hierarchy(cronograma.creado_por_rol)
    return rol_aprobador.lower().strip() in roles_permitidos


def get_agente_rol(agente):
    """
    Obtiene el rol principal de un agente.
    
    Args:
        agente: Instancia de Agente
        
    Returns:
        str: Nombre del rol (jefatura, director, administrador) o None
    """
    try:
        # Buscar asignación activa del agente
        from personas.models import AgenteRol
        asignacion = AgenteRol.objects.filter(
            id_agente=agente
        ).select_related('id_rol').first()
        
        if asignacion and asignacion.id_rol:
            rol_nombre = asignacion.id_rol.nombre.lower().strip()
            
            # Mapear roles a categorías de aprobación
            if 'admin' in rol_nombre or 'administrador' in rol_nombre:
                return 'administrador'
            elif 'director' in rol_nombre:
                return 'director'
            elif 'jefatura' in rol_nombre or 'jefe' in rol_nombre:
                return 'jefatura'
            
            # Si tiene algún rol pero no es ninguno de los anteriores,
            # retornar el nombre del rol tal cual
            return rol_nombre
        
        return None
    except Exception as e:
        logger.error(f"Error obteniendo rol del agente: {e}")
        return None


def requiere_aprobacion_rol(creado_por_rol):
    """
    Verifica si un cronograma requiere aprobación según el rol del creador.
    
    Args:
        creado_por_rol (str): Rol del agente que creó el cronograma
        
    Returns:
        bool: True si requiere aprobación, False si es auto-aprobado
    """
    if not creado_por_rol:
        return True
    
    rol_lower = creado_por_rol.lower().strip()
    
    # Solo administrador no requiere aprobación (auto-aprobado)
    return rol_lower != 'administrador'