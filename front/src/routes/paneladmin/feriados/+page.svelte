<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
    import CalendarioBase from '$lib/componentes/calendarioBase.svelte';
    import ModalGestionFeriado from '$lib/componentes/ModalGestionFeriado.svelte';
	import { feriadosController } from '$lib/paneladmin/controllers';

	// Stores del controlador  
	const { feriados, loading, error, success, modalGestionFeriado } = feriadosController;

	// Inicializar el controlador
	onMount(async () => {
		console.log('🔄 Componente montado, iniciando controlador de feriados...');
		try {
			await feriadosController.init();
			console.log('✅ Controlador de feriados inicializado exitosamente');
		} catch (err) {
			console.error('❌ Error inicializando controlador de feriados:', err);
			if (err.message === 'Usuario no autenticado') {
				goto('/');
				return;
			}
		}
	});

	function handleDayClick(event) {
		const { date, isFeriado } = event.detail;
		const selectedDate = date.toISOString().split('T')[0];
		const feriado = feriadosController.getFeriadoByDate(selectedDate);
		
		feriadosController.openModal(selectedDate, feriado);
	}

	function closeModal() {
		feriadosController.closeModal();
	}
	
</script>

<div class="admin-page-container">
    <div class="page-header">
        <h1>Gestión de Feriados</h1>
		{#if $error}
			<div class="error-message">{$error}</div>
		{/if}
		{#if $success}
			<div class="success-message">{$success}</div>
		{/if}
    </div>

	<div class="calendar-wrapper">
		{#if $loading}
			<div class="loading">Cargando feriados...</div>
		{:else}
			<CalendarioBase feriados={$feriados} on:dayclick={handleDayClick} />
		{/if}
	</div>
</div>

<ModalGestionFeriado 
	bind:isOpen={$modalGestionFeriado.isOpen}
	feriado={$modalGestionFeriado.feriado}
	selectedDate={$modalGestionFeriado.selectedDate}
	isSaving={$modalGestionFeriado.isSaving}
	isDeleting={$modalGestionFeriado.isDeleting}
	{feriadosController}
	on:close={closeModal}
/>

<style>
    .admin-page-container {
        width: 80%;
        max-width: 1000px;
        margin: 0 auto;
    }

    .page-header {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap; 
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #e79043, #d17a2e);
        border-radius: 12px;
    }

    .error-message {
        background-color: #fee;
        color: #c33;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #fcc;
        margin-top: 0.5rem;
        width: 100%;
    }

    .success-message {
        background-color: #efe;
        color: #363;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #cfc;
        margin-top: 0.5rem;
        width: 100%;
    }

    .loading {
        text-align: center;
        padding: 2rem;
        font-style: italic;
        color: #666;
    }

    .page-header h1 {
        margin: 0;
        color: #333; 
        font-size: 2rem;
        font-weight: 600;
    }

    .calendar-wrapper {
        width: 100%;
        margin-top: 20px;
    }
</style>
