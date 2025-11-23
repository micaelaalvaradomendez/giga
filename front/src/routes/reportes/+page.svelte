<h1>lo que va en esta pagina</h1>

<p>Aca cada usuario puede generar sus propios reportes</p>

<p> Ademas hay que considerar que rol director y jeefatura tambvien accederan a esta seccion</p>

<p> Entonces hay que considerarf que si entra jefatura puede hacer reportes de sus agentes de su misma area</p>

<p> si entra directo puede hacer reportes de jefatura + agentes de su propia area</p>

<p> implementar despues de hacer funcional al 100% paneladmin/reportes</p>

<p> para reutilizar toda la logica que se esta usando ahi</p>

<h1> mi machete </h1>

<p>
    El sistema debe permitir generar reportes aplicando filtros por rangos de fechas, área, tipo de guardia o por agente.

extensiones basadas en el rol del usuario:
    	Reporte individual (Agente): El usuario Agente solicita su propio historial.
	Reporte por equipo/área (Jefatura): El usuario Jefatura aplica filtros por su equipo.
	Reporte por dirección (Director/Administrador): El usuario Director o Administrador aplica filtros por dirección y rango de fechas.

Consideraciones para la Generación de Reportes: El objetivo principal es que el sistema GIGA pueda generar los dos tipos de documentos que se utilizan actualmente: Planillas Individuales de Guardias y Planillas Generales/Preventivas de horas operativas.

1. Replicar la Planilla Individual de Guardias: La planilla individual actual contiene la información personal del agente y su registro de guardias y novedades en un formato tabular por día.

2. Replicar la Planilla General/Preventiva: Esta planilla (ej. "PREVENTIVO MES AGOSTO 2025" o "Planilla general Dirección Observatorio Vial mes julio, 2025") organiza la información por agente en un formato de grilla.

Funcionalidades del Módulo de Reportes en GIGA: El Módulo de Reportes debe implementar la siguiente secuencia de pasos para generar un reporte eficaz:
    	Selección de Opción: El usuario selecciona "Generar reporte".
	Aplicación de Filtros (RF08): Permite al usuario aplicar los siguientes filtros obligatorios:
    		Rangos de Fechas (Inicio y Fin).
    		Área/Dirección.
    		Tipo de Guardia.
    		Agente (individual).
	Consulta y Validación: El sistema valida los filtros y consulta la información. Si no hay resultados, muestra la alerta "No se encontraron registros".
	Vista Previa: Muestra la vista previa del reporte con los resultados.
	Exportación: El usuario puede exportar a:
    		PDF: Para mantener el formato rígido y la imprimibilidad.
		Excel: Para permitir la manipulación, cálculo posterior y reuso de los datos.
	Registro de Auditoría: El sistema registra el evento de exportación y consulta en el módulo de auditoría.

Esta estructura garantiza la trazabilidad, el cumplimiento del rol (Agente solo consulta su reporte, Jefatura/Director consultan por área, etc.), y la generación de documentos que reemplazan funcionalmente a las planillas actuales.
entonces en paneladmin/reportes debe aparecer todo lo que corresponda a la persona del rol administrador
y en /reportes debe aparecer lo de los otros roles pero en funcion del rol que tenga
</p>