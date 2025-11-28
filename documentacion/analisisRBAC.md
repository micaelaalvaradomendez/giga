# Sistema GIGA - Análisis de Control de Acceso Basado en Roles (RBAC)
## Filtros y Permisos por Rol: Definidos vs Implementados

---

## 📋 Resumen Ejecutivo

Este documento analiza el **Control de Acceso Basado en Roles (RBAC)** del sistema GIGA, identificando qué filtros y restricciones de datos **deben estar implementados** según la documentación y cuáles **están realmente implementados** en el código actual.

**Hallazgo Crítico**: Existe una **brecha significativa** entre los permisos definidos por rol en la documentación y la implementación actual, donde la mayoría de los endpoints utilizan `permission_classes = [AllowAny]` sin filtrado por rol.

---

## 🎭 Roles del Sistema

### Jerarquía de Roles Definida

```
Administrador (Máximo acceso)
    ↓
Director (Acceso completo a división)
    ↓
Jefatura (Acceso a área específica)
    ↓
Agente Avanzado (Acceso extendido a datos del área)
    ↓
Agente (Acceso básico a datos propios)
```

---

## 📊 Matriz de Permisos por Caso de Uso

### Según Documentación Original

| Caso de Uso | Agente | Agente Avanzado | Jefatura | Director | Admin |
|-------------|--------|-----------------|----------|----------|-------|
| **CU1** - Autenticar Usuario | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU2.a** - Crear Agente | ❌ | ❌ | ❌ | ❌ | ✅ |
| **CU2.b** - Editar Agente | ❌ | ❌ | ❌ | ❌ | ✅ |
| **CU2.c** - Dar de baja Agente | ❌ | ❌ | ❌ | ❌ | ✅ |
| **CU3** - Auditar Operaciones | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU4** - Registrar Asistencia | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU5** - Generar Cronograma | ❌ | ❌ | ✅ | ✅ | ✅ |
| **CU6** - Validar Cronograma | ❌ | ❌ | ✅ | ✅ | ✅ |
| **CU7** - Publicar Cronograma | ❌ | ❌ | ✅ | ✅ | ✅ |
| **CU8** - Generar Reportes | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU9** - Notificar Incidencias | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU10** - Configurar Parámetros | ❌ | ❌ | ❌ | ❌ | ✅ |
| **CU11** - Consultar Convenio IA | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CU12** - Gestionar Licencias | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔍 Análisis Detallado por Módulo

## 1. Módulo de Asistencia

### 1.1. Registrar Asistencia (CU4)

#### **DEFINIDO**: Filtros y Permisos Requeridos

**Agente**:
- ✅ Puede: Marcar su propia asistencia (entrada/salida)
- ❌ No puede: Ver asistencias de otros agentes
- ❌ No puede: Modificar asistencias
- **Filtro requerido**: `id_agente = agente_actual`

**Agente Avanzado**:
- ✅ Puede: Marcar asistencia propia
- ✅ Puede: Ver asistencias de su área
- ❌ No puede: Modificar asistencias de otros
- **Filtro requerido**: `id_area = area_agente_actual`

**Jefatura**:
- ✅ Puede: Ver todas las asistencias de su área
- ✅ Puede: Corregir asistencias de su área
- ✅ Puede: Ver reporte de ausentismo
- **Filtro requerido**: `id_area = area_jefatura` (incluyendo sub-áreas)

**Director**:
- ✅ Puede: Ver asistencias de todas las áreas bajo su dirección
- ✅ Puede: Corregir asistencias de su división
- **Filtro requerido**: `id_area IN (areas_bajo_direccion)`

**Administrador**:
- ✅ Acceso completo sin filtros

#### **IMPLEMENTADO**: Estado Actual

**Endpoints de Asistencia**:

```python
# asistencia/views.py
@permission_classes([AllowAny])  # ❌ PROBLEMA: Sin autenticación
def marcar_entrada(request):
    # ❌ FALTA: Validar que agente solo marque su propia asistencia
    # ❌ FALTA: Prevenir suplantación de identidad
    ...

@permission_classes([AllowAny])  # ❌ PROBLEMA: Sin autenticación
def marcar_salida(request):
    # ❌ FALTA: Validación de rol
    ...

@permission_classes([AllowAny])  # ❌ PROBLEMA
def listar_asistencias(request):
    # ❌ FALTA: Filtro por rol
    # Debería filtrar:
    # - Agente: solo sus asistencias
    # - Agente Avanzado: asistencias de su área
    # - Jefatura: asistencias de su área y sub-áreas
    # - Director: asistencias de su división
    # - Admin: todas
    ...
```

**Problemas Identificados**:
- ❌ No hay validación de autenticación (`AllowAny`)
- ❌ No hay filtros por rol en consultas
- ❌ Cualquier usuario puede ver todas las asistencias
- ❌ No hay restricciones sobre quién puede corregir

#### **DEBE IMPLEMENTARSE**:

```python
# EJEMPLO DE IMPLEMENTACIÓN REQUERIDA
@permission_classes([IsAuthenticated])
def listar_asistencias(request):
    agente = request.user.agente
    rol = get_agente_rol(agente)
    
    queryset = Asistencia.objects.all()
    
    if rol == 'agente':
        # Solo sus propias asistencias
        queryset = queryset.filter(id_agente=agente)
    
    elif rol == 'agente_avanzado':
        # Asistencias de su área
        queryset = queryset.filter(id_area=agente.id_area)
    
    elif rol == 'jefatura':
        # Asistencias de su área y sub-áreas
        areas = [agente.id_area.id_area]
        areas.extend(obtener_subareas(agente.id_area))
        queryset = queryset.filter(id_area__in=areas)
    
    elif rol == 'director':
        # Asistencias de áreas bajo su dirección
        areas_dirigidas = obtener_areas_direccion(agente)
        queryset = queryset.filter(id_area__in=areas_dirigidas)
    
    # Admin: sin filtro (queryset completo)
    
    return Response(serializer.data)
```

---

### 1.2. Gestionar Licencias (CU12)

#### **DEFINIDO**: Filtros y Permisos Requeridos

**Agente**:
- ✅ Puede: Solicitar sus propias licencias
- ✅ Puede: Ver el estado de sus licencias
- ❌ No puede: Ver licencias de otros
- ❌ No puede: Aprobar/rechazar
- **Filtro requerido**: `id_agente = agente_actual`

**Jefatura**:
- ✅ Puede: Solicitar licencias propias
- ✅ Puede: Ver licencias de su área
- ✅ Puede: Aprobar/rechazar licencias de agentes de su área
- ❌ No puede: Aprobar/rechazar licencias de otros jefes
- **Filtros requeridos**:
  - Ver: `id_agente.id_area = area_jefatura`
  - Aprobar: `id_agente.id_area = area_jefatura AND id_agente.rol != 'jefatura'`

**Director**:
- ✅ Puede: Ver licencias de áreas bajo su dirección
- ✅ Puede: Aprobar/rechazar licencias de jefaturas
- **Filtros requeridos**:
  - Ver: `id_agente.id_area IN (areas_direccion)`
  - Aprobar: `solicitada_por.rol IN ('jefatura', 'agente', 'agente_avanzado')`

**Administrador**:
- ✅ Ver y aprobar todas las licencias sin restricciones

#### **IMPLEMENTADO**: Estado Actual

**Endpoints de Licencias**:

```python
# asistencia/views.py (inferido, no visible completamente)
@permission_classes([AllowAny])
def listar_licencias(request):
    # ❌ FALTA: Filtro por rol
    # Actualmente retorna TODAS las licencias
    ...

@permission_classes([AllowAny])
def aprobar_licencia(request, pk):
    # ❌ FALTA: Validación de jerarquía
    # Cualquiera puede aprobar cualquier licencia
    ...
```

**Problemas Identificados**:
- ❌ No hay filtros por rol al listar licencias
- ❌ No hay validación jerárquica en aprobaciones
- ❌ Agente puede ver licencias de toda la organización

#### **DEBE IMPLEMENTARSE**:

**Endpoint**: `GET /asistencia/licencias/`
- Filtrar licencias según rol del usuario autenticado

**Endpoint**: `PATCH /asistencia/licencias/{id}/aprobar/`
- Validar que el aprobador tenga jerarquía sobre el solicitante
- Jefatura solo puede aprobar licencias de agentes de su área
- Director solo puede aprobar licencias de jefaturas
- Admin puede aprobar todas

---

## 2. Módulo de Guardias

### 2.1. Generar Cronograma (CU5)

#### **DEFINIDO**: Filtros y Permisos Requeridos

**Jefatura**:
- ✅ Puede: Crear cronogramas para su área
- ❌ No puede: Crear cronogramas para otras áreas
- ❌ No puede: Auto-aprobar (requiere aprobación de Director/Admin)
- **Filtro requerido**: `id_area = area_jefatura`

**Director**:
- ✅ Puede: Crear cronogramas para áreas bajo su dirección
- ❌ No puede: Auto-aprobar (requiere aprobación de Admin, excepto para agentes)
- **Filtro requerido**: `id_area IN (areas_direccion)`

**Administrador**:
- ✅ Puede: Crear cronogramas para cualquier área
- ✅ Puede: Auto-aprobar (no requiere workflow)
- **Sin filtros**

#### **IMPLEMENTADO**: Estado Actual

**Endpoint**: `POST /guardias/cronogramas/crear_con_guardias/`

```python
# guardias/views.py - líneas 386-628
permission_classes = [IsAuthenticated]

def crear_con_guardias(self, request):
    # ✅ Implementado: Validación de rol del creador
    rol_creador = get_agente_rol(agente_creador)
    
    # ✅ Implementado: Auto-aprobación para admin
    if rol_creador.lower() == 'administrador':
        estado_inicial = 'publicada'
    else:
        estado_inicial = 'pendiente'
    
    # ❌ FALTA: Validación de que solo puede crear para su área
    # Actualmente permite crear cronograma para cualquier área
```

**Problemas Identificados**:
- 🟡 Workflow de aprobación está implementado
- ❌ No hay validación de que Jefatura solo pueda crear para su área
- ❌ No hay validación de que Director solo pueda crear para áreas bajo su dirección

#### **DEBE IMPLEMENTARSE**:

```python
# Agregar validación en crear_con_guardias
id_area = request.data.get('id_area')
agente_area = agente_creador.id_area.id_area

if rol_creador == 'jefatura':
    if id_area != agente_area:
        return Response({
            'error': 'Jefatura solo puede crear cronogramas para su propia área'
        }, status=400)

elif rol_creador == 'director':
    areas_permitidas = obtener_areas_bajo_direccion(agente_creador)
    if id_area not in areas_permitidas:
        return Response({
            'error': 'Director solo puede crear cronogramas para áreas bajo su dirección'
        }, status=400)
```

---

### 2.2. Validar/Aprobar Cronogramas (CU6)

#### **DEFINIDO**: Filtros y Permisos Requeridos

**Jefatura**:
- ✅ Puede: Aprobar cronogramas creados por agentes de su área
- ❌ No puede: Aprobar cronogramas de otros jefes
- **Filtro requerido**: Listar pendientes donde `creado_por.id_area = area_jefatura AND creado_por.rol = 'agente'`

**Director**:
- ✅ Puede: Aprobar cronogramas creados por jefaturas
- **Filtro requerido**: Listar pendientes donde `creado_por.rol = 'jefatura' AND creado_por.id_area IN (areas_direccion)`

**Administrador**:
- ✅ Puede: Aprobar cualquier cronograma

#### **IMPLEMENTADO**: Estado Actual

**Endpoint**: `GET /guardias/cronogramas/pendientes/`

```python
# guardias/views.py - líneas 1137-1189
permission_classes = [IsAuthenticated]

def pendientes(self, request):
    # ✅ Implementado: Obtención de rol del agente
    rol_agente = get_agente_rol(agente)
    
    # ✅ Implementado: Filtro por jerarquía de aprobación
    for cronograma in cronogramas_pendientes:
        if cronograma.creado_por_rol:
            roles_permitidos = get_approval_hierarchy(cronograma.creado_por_rol)
            if rol_agente.lower() in roles_permitidos:
                cronogramas_pendientes.append(cronograma)
    
    # ✅ BIEN IMPLEMENTADO: Filtrado por jerarquía
```

**Endpoint**: `PATCH /guardias/cronogramas/{id}/aprobar/`

```python
# guardias/views.py - líneas 901-1000
permission_classes = [IsAuthenticated]

def aprobar(self, request, pk=None):
    # ✅ Implementado: Validación de jerarquía
    if not puede_aprobar(cronograma, rol_aprobador):
        return Response({'error': 'No tiene permisos...'}, 400)
    
    # ✅ BIEN IMPLEMENTADO
```

**Estado**: ✅ **BIEN IMPLEMENTADO** - Las aprobaciones tienen validación jerárquica correcta

---

### 2.3. Consultar Guardias Propias

#### **DEFINIDO**: Filtros Requeridos (No explícito en CU, pero lógico)

**Agente**:
- ✅ Puede: Ver sus propias guardias asignadas
- ❌ No puede: Ver guardias de otros agentes
- **Filtro requerido**: `id_agente = agente_actual`

**Agente Avanzado**:
- ✅ Puede: Ver guardias de todos los agentes de su área
- **Filtro requerido**: `id_agente.id_area = area_agente`

**Jefatura**:
- ✅ Puede: Ver guardias de su área y sub-áreas
- **Filtro requerido**: `id_agente.id_area IN (area_y_subareas)`

**Director**:
- ✅ Puede: Ver guardias de áreas bajo su dirección
- **Filtro requerido**: `id_agente.id_area IN (areas_direccion)`

**Administrador**:
- ✅ Ver todas las guardias

#### **IMPLEMENTADO**: Estado Actual

**Endpoint**: `GET /guardias/guardias/`

```python
# guardias/views.py
class GuardiaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # ❌ FALTA: Filtro por rol del usuario
        # Actualmente retorna TODAS las guardias
        queryset = Guardia.objects.all()
        
        # Solo tiene filtros por query params, no por rol
        agente_id = self.request.query_params.get('agente')
        if agente_id:
            queryset = queryset.filter(id_agente=agente_id)
```

**Problemas Identificados**:
- ❌ No hay filtro automático por rol
- ❌ Agente puede consultar guardias de otros agentes manualmente modificando `?agente=X`
- ❌ No hay restricciones de visibilidad por jerarquía

#### **DEBE IMPLEMENTARSE**:

```python
def get_queryset(self):
    agente = self.request.user.agente
    rol = get_agente_rol(agente)
    queryset = Guardia.objects.all()
    
    if rol == 'agente':
        # Solo sus guardias
        queryset = queryset.filter(id_agente=agente)
    
    elif rol == 'agente_avanzado':
        # Guardias de su área
        queryset = queryset.filter(id_agente__id_area=agente.id_area)
    
    elif rol == 'jefatura':
        # Guardias de área y sub-áreas
        areas = obtener_area_y_subareas(agente.id_area)
        queryset = queryset.filter(id_agente__id_area__in=areas)
    
    elif rol == 'director':
        # Guardias de áreas bajo dirección
        areas = obtener_areas_direccion(agente)
        queryset = queryset.filter(id_agente__id_area__in=areas)
    
    # Admin: sin filtro
    
    # Permitir filtros adicionales por query params
    # pero solo dentro del conjunto permitido
    return queryset
```

---

### 2.4. Compensaciones

#### **DEFINIDO**: Filtros y Permisos (Por inferencia de lógica de negocio)

**Agente**:
- ✅ Puede: Solicitar compensaciones para sus propias guardias
- ✅ Puede: Ver estado de sus compensaciones
- ❌ No puede: Ver compensaciones de otros
- **Filtro requerido**: `id_agente = agente_actual`

**Jefatura**:
- ✅ Puede: Ver compensaciones de agentes de su área
- ✅ Puede: Aprobar/rechazar compensaciones de su área
- **Filtro requerido**: `id_agente.id_area = area_jefatura`

**Director**:
- ✅ Puede: Ver compensaciones de áreas bajo su dirección
- ✅ Puede: Aprobar compensaciones de jefaturas
- **Filtro requerido**: `id_agente.id_area IN (areas_direccion)`

**Administrador**:
- ✅ Acceso completo

#### **IMPLEMENTADO**: Estado Actual

**Endpoint**: `GET /guardias/compensaciones/`

```python
# guardias/views.py
class HoraCompensacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = HoraCompensacion.objects.all()
    
    # ❌ FALTA: Filtro por rol en get_queryset
    # Retorna TODAS las compensaciones
```

**Problemas Identificados**:
- ❌ No hay filtro por rol
- ❌ Agente puede ver compensaciones de toda la organización

#### **DEBE IMPLEMENTARSE**:

Agregar `get_queryset()` con filtros por rol similares al ejemplo anterior.

---

## 3. Módulo de Personas

### 3.1. Gestión de Agentes (CU2.a, CU2.b, CU2.c)

#### **DEFINIDO**: Filtros y Permisos Requeridos

**Solo Administrador**:
- ✅ Puede: Crear, editar, dar de baja agentes
- ✅ Puede: Ver todos los agentes

**Otros roles**:
- ❌ No pueden: Crear/editar/eliminar agentes
- ✅ Pueden: Ver agentes de su área (para asignación de guardias, etc.)

#### **IMPLEMENTADO**: Estado Actual

```python
# personas/views.py
@permission_classes([AllowAny])  # ❌ PROBLEMA CRÍTICO
def crear_agente(request):
    # ❌ Sin validación de rol
    # Cualquiera puede crear agentes
    ...

@permission_classes([AllowAny])  # ❌ PROBLEMA CRÍTICO
def editar_agente(request, id):
    # ❌ Sin validación de rol
    ...

@permission_classes([AllowAny])  # ❌ PROBLEMA CRÍTICO
def dar_baja_agente(request, id):
    # ❌ Sin validación de rol
    ...
```

**Problemas Identificados**:
- ❌ **CRÍTICO**: Endpoints sin autenticación
- ❌ **CRÍTICO**: Sin validación de rol administrador
- ❌ Cualquiera puede crear/modificar/eliminar agentes

#### **DEBE IMPLEMENTARSE**:

```python
@permission_classes([IsAuthenticated])
def crear_agente(request):
    agente = request.user.agente
    rol = get_agente_rol(agente)
    
    if rol != 'administrador':
        return Response({
            'error': 'Solo administradores pueden crear agentes'
        }, status=403)
    
    # Continuar con creación
    ...
```

---

### 3.2. Consultar Listado de Agentes

#### **DEFINIDO**: Filtros Requeridos

**Agente**:
- ✅ Puede: Ver agentes de su área (para contexto)
- **Filtro requerido**: `id_area = area_agente`

**Jefatura**:
- ✅ Puede: Ver agentes de su área y sub-áreas
- **Filtro requerido**: `id_area IN (area_y_subareas)`

**Director**:
- ✅ Puede: Ver agentes de áreas bajo su dirección
- **Filtro requerido**: `id_area IN (areas_direccion)`

**Administrador**:
- ✅ Ver todos los agentes

#### **IMPLEMENTADO**: Estado Actual

```python
# personas/views.py
@permission_classes([AllowAny])  # ❌ PROBLEMA
def listar_agentes(request):
    # ❌ FALTA: Filtro por rol
    # Retorna TODOS los agentes
    agentes = Agente.objects.all()
    ...
```

**Debe implementarse**: Filtrado por rol en queryset

---

## 4. Módulo de Auditoría (CU3)

### **DEFINIDO**: Filtros y Permisos Requeridos

**Agente**:
- ✅ Puede: Ver su propia auditoría (acciones que él realizó)
- **Filtro requerido**: `id_agente = agente_actual`

**Agente Avanzado**:
- ✅ Puede: Ver auditoría de acciones en su área
- **Filtro requerido**: `Registros relacionados con área del agente`

**Jefatura**:
- ✅ Puede: Ver auditoría de su área
- **Filtro requerido**: Registros de tablas relacionadas con su área

**Director**:
- ✅ Puede: Ver auditoría de áreas bajo su dirección

**Administrador**:
- ✅ Ver toda la auditoría

### **IMPLEMENTADO**: Estado Actual

```python
# auditoria/views.py
class AuditoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    # ❌ FALTA: Filtro por rol
    # Retorna TODOS los logs de auditoría
```

**Debe implementarse**: Filtrado por rol en auditoría

---

## 5. Módulo de Reportes (CU8)

### **DEFINIDO**: Filtros y Permisos Requeridos

**Agente**:
- ✅ Puede: Generar reportes propios (guardias, asistencias, licencias)
- ❌ No puede: Generar reportes de otros
- **Filtro requerido**: `id_agente = agente_actual`

**Jefatura**:
- ✅ Puede: Generar reportes de su área
- **Filtro requerido**: `id_agente.id_area IN (area_y_subareas)`

**Director**:
- ✅ Puede: Generar reportes de su división
- **Filtro requerido**: `id_agente.id_area IN (areas_direccion)`

**Administrador**:
- ✅ Generar cualquier reporte

### **IMPLEMENTADO**: Estado Actual

```python
# guardias/views.py
@action(detail=False, methods=['post'], permission_classes=[AllowAny])
def exportar_pdf(self, request):
    # ❌ PROBLEMA CRÍTICO: Sin autenticación
    # ❌ FALTA: Filtro por rol en datos exportados
    # ❌ Actualmente usa datos hardcodeados
    ...
```

**Problemas Identificados**:
- ❌ Endpoints de exportación sin autenticación
- ❌ No hay filtros por rol en los datos a exportar
- ❌ Agente podría solicitar reporte de toda la organización

---

## 📊 Resumen de Brechas por Módulo

### Estado de Implementación de Filtros RBAC

| Módulo | Autenticación | Filtros por Rol | Estado |
|--------|---------------|-----------------|--------|
| **Asistencia** | ❌ AllowAny | ❌ No implementado | 🔴 Crítico |
| **Licencias** | ❌ AllowAny | ❌ No implementado | 🔴 Crítico |
| **Guardias - Consulta** | ✅ IsAuthenticated | ❌ No implementado | 🟡 Parcial |
| **Guardias - Creación** | ✅ IsAuthenticated | ❌ Validación parcial | 🟡 Parcial |
| **Guardias - Aprobación** | ✅ IsAuthenticated | ✅ Implementado | ✅ Completo |
| **Compensaciones** | ✅ IsAuthenticated | ❌ No implementado | 🟡 Parcial |
| **Personas** | ❌ AllowAny | ❌ No implementado | 🔴 Crítico |
| **Auditoría** | ✅ IsAuthenticated | ❌ No implementado | 🟡 Parcial |
| **Reportes** | ❌ AllowAny | ❌ No implementado | 🔴 Crítico |

---

## 🛠️ Plan de Implementación de Filtros RBAC

### Prioridad Crítica 🔴

#### 1. **Reactivar Autenticación en Todos los Endpoints**

**Ubicación**: Todos los módulos

**Cambio Requerido**:
```python
# ANTES:
@permission_classes([AllowAny])

# DESPUÉS:
@permission_classes([IsAuthenticated])
```

**Archivos a Modificar**:
- `personas/views.py` - ~25 endpoints
- `asistencia/views.py` - ~10 endpoints
- `guardias/views.py` - 3 endpoints de exportación
- `auditoria/views.py` - 1 endpoint

**Esfuerzo**: 2-3 horas  
**Impacto**: Crítico para seguridad

---

#### 2. **Implementar Filtros por Rol en Gestión de Agentes**

**Ubicación**: `personas/views.py`

**Endpoints Críticos**:
- `POST /personas/agentes/` - Crear agente
- `PUT/PATCH /personas/agentes/{id}/` - Editar agente
- `DELETE /personas/agentes/{id}/` - Dar de baja

**Implementación Requerida**:
```python
def validar_rol_administrador(agente):
    rol = get_agente_rol(agente)
    if rol != 'administrador':
        raise PermissionDenied('Solo administradores pueden realizar esta acción')
```

**Esfuerzo**: 3-4 horas  
**Impacto**: Crítico - Previene manipulación de usuarios

---

#### 3. **Implementar Filtros en Consultas de Asistencia**

**Ubicación**: `asistencia/views.py`

**Endpoints**:
- `GET /asistencia/asistencias/`
- `GET /asistencia/asistencias/por_agente/`
- `GET /asistencia/asistencias/resumen_mensual/`

**Implementación**:
- Agregar `get_queryset()` con filtros por rol
- Validar parámetros contra permisos del rol

**Esfuerzo**: 4-5 horas  
**Impacto**: Alto - Privacidad de datos de asistencia

---

### Prioridad Alta 🟡

#### 4. **Implementar Filtros en Consultas de Guardias**

**Ubicación**: `guardias/views.py` - `GuardiaViewSet`

**Método a Modificar**: `get_queryset()`

**Esfuerzo**: 3-4 horas  
**Impacto**: Alto - Visibilidad de datos sensibles

---

#### 5. **Implementar Filtros en Licencias**

**Ubicación**: `asistencia/views.py` (módulo de licencias)

**Endpoints**:
- `GET /asistencia/licencias/`
- `PATCH /asistencia/licencias/{id}/aprobar/`

**Implementación**:
- Filtros por jerarquía en listado
- Validación de jerarquía en aprobaciones

**Esfuerzo**: 4-5 horas  
**Impacto**: Alto - Workflow de aprobación

---

#### 6. **Implementar Filtros en Compensaciones**

**Ubicación**: `guardias/views.py` - `HoraCompensacionViewSet`

**Implementación**: Similar a guardias y licencias

**Esfuerzo**: 3-4 horas  
**Impacto**: Medio-Alto

---

#### 7. **Implementar Validación de Área en Creación de Cronogramas**

**Ubicación**: `guardias/views.py` - `crear_con_guardias()`

**Validación Requerida**:
- Jefatura solo puede crear para su área
- Director solo para áreas bajo su dirección

**Esfuerzo**: 2-3 horas  
**Impacto**: Alto - Previene creación indebida

---

### Prioridad Media 🟢

#### 8. **Implementar Filtros en Auditoría**

**Ubicación**: `auditoria/views.py`

**Esfuerzo**: 3-4 horas  
**Impacto**: Medio

---

#### 9. **Implementar Filtros en Reportes**

**Ubicación**: `guardias/views.py` - Métodos de exportación

**Dependencia**: Primero completar CU8 (Generar Reportes)

**Esfuerzo**: 5-6 horas  
**Impacto**: Medio (dependiente de completar reportes primero)

---

#### 10. **Implementar Filtros en Listado de Agentes**

**Ubicación**: `personas/views.py` - `listar_agentes()`

**Esfuerzo**: 2-3 horas  
**Impacto**: Medio

---

## 📋 Checklist de Implementación

### Fase 1: Seguridad Básica (Sprint 4 - Semana 1)

- [ ] Cambiar todos los `permission_classes = [AllowAny]` a `IsAuthenticated`
- [ ] Implementar validación de rol administrador en gestión de agentes
- [ ] Testing de autenticación en todos los endpoints

### Fase 2: Filtros Críticos (Sprint 4 - Semana 2)

- [ ] Implementar filtros RBAC en asistencias
- [ ] Implementar filtros RBAC en guardias (consulta)
- [ ] Implementar validación de área en creación de cronogramas
- [ ] Implementar filtros RBAC en licencias

### Fase 3: Filtros Complementarios (Sprint 5)

- [ ] Implementar filtros RBAC en compensaciones
- [ ] Implementar filtros RBAC en auditoría
- [ ] Implementar filtros RBAC en listado de agentes
- [ ] Implementar filtros RBAC en reportes (cuando estén completos)

### Fase 4: Testing y Validación

- [ ] Testing de permisos por cada rol
- [ ] Testing de intentos de acceso no autorizado
- [ ] Validación de que cada rol solo ve datos permitidos
- [ ] Documentación de permisos implementados

---

## 🔧 Función Utilitaria Recomendada

### Crear Helper para Filtrado Automático

```python
# Ubicación sugerida: personas/utils.py o nuevo archivo common/rbac.py

def obtener_queryset_filtrado_por_rol(queryset, agente_actual, campo_agente='id_agente', campo_area='id_area'):
    \"\"\"
    Filtra un queryset según el rol del agente actual.
    
    Args:
        queryset: QuerySet a filtrar
        agente_actual: Agente autenticado
        campo_agente: Campo del modelo que referencia al agente
        campo_area: Campo del modelo que referencia al área
    
    Returns:
        QuerySet filtrado según rol
    \"\"\"
    from guardias.utils import get_agente_rol
    
    rol = get_agente_rol(agente_actual)
    
    if rol == 'administrador':
        return queryset  # Sin filtro
    
    if rol == 'agente':
        # Solo registros propios
        filtro = {campo_agente: agente_actual}
        return queryset.filter(**filtro)
    
    if rol == 'agente_avanzado':
        # Registros de su área
        filtro = {f\"{campo_agente}__{campo_area}\": agente_actual.id_area}
        return queryset.filter(**filtro)
    
    if rol == 'jefatura':
        # Registros de área y sub-áreas
        areas = obtener_area_y_subareas(agente_actual.id_area)
        filtro = {f\"{campo_agente}__{campo_area}__in\": areas}
        return queryset.filter(**filtro)
    
    if rol == 'director':
        # Registros de áreas bajo dirección
        areas = obtener_areas_bajo_direccion(agente_actual)
        filtro = {f\"{campo_agente}__{campo_area}__in\": areas}
        return queryset.filter(**filtro)
    
    # Por defecto, solo registros propios
    filtro = {campo_agente: agente_actual}
    return queryset.filter(**filtro)


def obtener_area_y_subareas(area):
    \"\"\"Retorna lista de IDs de área y todas sus sub-áreas\"\"\"
    from personas.models import Area
    
    areas = [area.id_area]
    subareas = Area.objects.filter(id_area_padre=area, activa=True)
    
    for subarea in subareas:
        areas.extend(obtener_area_y_subareas(subarea))
    
    return areas


def obtener_areas_bajo_direccion(agente_director):
    \"\"\"Retorna áreas bajo la dirección de un director\"\"\"
    # Esta lógica dependerá de cómo esté modelada la relación
    # Por ahora, simplificado como área del director y sub-áreas
    return obtener_area_y_subareas(agente_director.id_area)
```

### Uso en ViewSets:

```python
class AsistenciaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        agente_actual = self.request.user.agente
        queryset = Asistencia.objects.all()
        
        # Aplicar filtro automático por rol
        return obtener_queryset_filtrado_por_rol(
            queryset, 
            agente_actual,
            campo_agente='id_agente',
            campo_area='id_area'
        )
```

---

## ✅ Conclusión

El sistema GIGA tiene **definidos claramente los roles y permisos** en su documentación, pero existe una **brecha significativa entre lo definido y lo implementado**:

### Hallazgos Críticos:

1. **❌ CRÍTICO**: Mayoría de endpoints con `AllowAny` (sin autenticación)
2. **❌ CRÍTICO**: Gestión de agentes sin validación de rol administrador
3. **❌ ALTO**: No hay filtros RBAC en consultas de datos sensibles
4. **❌ ALTO**: Agentes pueden ver datos de toda la organización
5. **✅ POSITIVO**: Workflow de aprobación de cronogramas SÍ tiene validación jerárquica

### Impacto:

- **Seguridad**: Vulnerabilidad crítica por falta de autenticación
- **Privacidad**: Exposición de datos sensibles entre roles
- **Integridad**: Riesgo de manipulación no autorizada de datos

### Recomendación:

**Priorizar Fase 1 y Fase 2** (Semanas 1-2 de Sprint 4) para alcanzar un nivel mínimo de seguridad antes de despliegue a producción.

**Esfuerzo Total Estimado**: 35-45 horas de desarrollo + testing

**Estado Objetivo**: 🟢 Sistema con RBAC completo y seguro
