<script>
    import CalendarioBase from '$lib/components/CalendarioBase.svelte';
    import ModalGestionFeriado from '$lib/components/ModalGestionFeriado.svelte';
	import { invalidateAll } from '$app/navigation';

	/** @type {import('./$types').PageData} */
	export let data;
	
	$: feriados = data.feriados;

	let isModalOpen = false;
	let selectedFeriado = null;
	let selectedDate = null;

	function handleDayClick(event) {
		const { date, isFeriado, feriado: feriadoData } = event.detail;
		selectedDate = date.toISOString().split('T')[0];

		if (isFeriado) {
			// Si ya hay un feriado, usamos los datos del calendario
			selectedFeriado = feriados.find(f => f.fecha === selectedDate);
		} else {
			selectedFeriado = null;
		}
		isModalOpen = true;
	}

	function closeModal() {
		isModalOpen = false;
		invalidateAll();
	}
	
</script>

<div class="admin-page-container">
    <div class="page-header">
        <h1>Gestión de Feriados</h1>
    </div>

	<div class="calendar-wrapper">
		<CalendarioBase {feriados} on:dayclick={handleDayClick} />
	</div>
</div>

<ModalGestionFeriado 
	bind:isOpen={isModalOpen}
	feriado={selectedFeriado}
	{selectedDate}
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
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap; 
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #e79043, #d17a2e);
        border-radius: 12px;
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
