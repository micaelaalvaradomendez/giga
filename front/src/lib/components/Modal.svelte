<script>
	import { createEventDispatcher } from 'svelte';
	import { fade } from 'svelte/transition';

	/**
	 * El título que se mostrará en la cabecera del modal.
	 * @type {string}
	 */
	export let title = 'Ventana Modal';

	const dispatch = createEventDispatcher();

	function closeModal() {
		dispatch('close');
	}
</script>

<div
	class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-75"
	on:click={closeModal}
	role="dialog"
	aria-modal="true"
	aria-labelledby="modal-title"
	transition:fade={{ duration: 150 }}
>
	<!-- Contenedor del modal -->
	<div
		class="relative mx-auto w-full max-w-2xl overflow-hidden rounded-lg bg-white shadow-xl"
		on:click|stopPropagation
		role="document"
	>
		<!-- Cabecera -->
		<div class="flex items-start justify-between border-b p-4">
			<h2 id="modal-title" class="text-lg font-semibold text-gray-800">
				{title}
			</h2>
			<button
				on:click={closeModal}
				class="text-gray-400 hover:text-gray-600"
				aria-label="Cerrar modal"
			>
				<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<div class="p-6">
			<slot />
		</div>
	</div>
</div>