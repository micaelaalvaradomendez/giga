<script>
	export let message = "Cargando...";
	export let size = "medium"; // "small", "medium", "large"
	export let color = "#3b82f6"; // Color principal del spinner
</script>

<div class="loading-container">
	<div class="spinner {size}" style="--spinner-color: {color}"></div>
	{#if message}
		<p class="message">{message}</p>
	{/if}
</div>

<style>
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem 1rem;
		gap: 1rem;
	}

	.spinner {
		border: 4px solid #f3f4f6;
		border-top: 4px solid var(--spinner-color);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.spinner.small {
		width: 24px;
		height: 24px;
		border-width: 3px;
	}

	.spinner.medium {
		width: 48px;
		height: 48px;
		border-width: 4px;
	}

	.spinner.large {
		width: 64px;
		height: 64px;
		border-width: 5px;
	}

	.message {
		color: #6b7280;
		font-size: 1rem;
		margin: 0;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}
</style>
