<script>
	export let show = false;
	export let title = "";
	export let maxWidth = "600px";
	export let onClose = () => {};
	function handleOverlayClick() {
		onClose();
	}
</script>
{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={handleOverlayClick}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal" style="max-width: {maxWidth}" on:click|stopPropagation>
			<div class="modal-header">
				<h2>{title}</h2>
				<button type="button" class="close-btn" on:click={onClose}>×</button>
			</div>
			<slot />
		</div>
	</div>
{/if}
<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
		overflow-y: auto;
		padding: 1rem 0;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}
	.modal-overlay::-webkit-scrollbar {
		display: none;
	}
	.modal {
		background: white;
		border-radius: 16px;
		padding: 0;
		width: 90%;
		max-height: 90vh;
		overflow: hidden;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalAppear 0.3s ease-out;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	@keyframes modalAppear {
		from {
			opacity: 0;
			transform: scale(0.9) translateY(-20px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}
	.modal-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}
	.modal-header h2 {
		margin: 0;
		color: white;
		font-size: 1.5rem;
		font-weight: 600;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		word-break: break-word;
		line-height: 1.3;
	}
	.close-btn {
		background: none;
		border: none;
		color: white;
		font-size: 28px;
		cursor: pointer;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: all 0.3s ease;
		padding: 0;
		line-height: 1;
	}
	.close-btn:hover {
		background: rgba(255, 255, 255, 0.2);
	}
	@media (max-width: 768px) {
		.modal {
			width: 95vw;
			max-width: none;
			max-height: 95vh;
			margin: 0.5rem;
		}
		.modal-header {
			padding: 1rem 1.25rem;
		}
		.modal-header h2 {
			font-size: 1.25rem;
		}
	}
</style>
