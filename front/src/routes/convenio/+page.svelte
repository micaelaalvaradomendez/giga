<script>
	import { convenioIaService } from '$lib/services.js';

	let pregunta = '';
	let respuesta = '';
	let loading = false;
	let error = '';

	async function consultar() {
		error = '';
		respuesta = '';
		if (!pregunta.trim()) return;
		loading = true;
		try {
			const resultado = await convenioIaService.consultarConvenio(pregunta);
			respuesta = resultado.respuesta || resultado.message || JSON.stringify(resultado);
		} catch (e) {
			error = e?.message || 'Error consultando el convenio.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Convenio con IA - Sistema GIGA</title>
</svelte:head>

<div class="page">
	<!-- Hero header -->
	<section class="hero">
		<div class="hero-inner">
			<div class="hero-icon">🧠</div>
			<div>
				<h1>Convenio con IA</h1>
				<p>Respuestas estrictamente desde el convenio cargado. Sin consultas externas.</p>
			</div>
		</div>
	</section>



	<!-- Card de consulta -->
	<section class="container">
		<div class="card">
			<label class="label" for="pregunta">Tu pregunta</label>
			<textarea
				id="pregunta"
				class="textarea"
				rows="5"
				bind:value={pregunta}
				placeholder="Inserte su pregunta acerca del convenio de trabajo:"
				on:keydown={(e) => (e.ctrlKey || e.metaKey) && e.key === 'Enter' && consultar()}
			></textarea>

			<div class="actions">
				<button class="btn btn-primary" on:click|preventDefault={consultar} disabled={loading || !pregunta.trim()}>
					{#if loading}
						<span class="spinner" aria-hidden="true"></span>
					{:else}
						Consultar
					{/if}
				</button>
			</div>

			{#if error}
				<div class="alert alert-error" role="alert">{error}</div>
			{/if}
		</div>
	</section>

	{#if respuesta}
	<section class="container">
		<div class="card">
			<h2 class="section-title">Respuesta</h2>
			<div class="answer">{@html respuesta}</div>
		</div>
	</section>
	{/if}
</div>

<style>
	:root {
		--bg: #0f172a;           /* slate-900 */
		--card: #ffffff;         /* white */
		--muted: #6b7280;        /* gray-500 */
		--text: #0f172a;         /* slate-900 */
		--primary: #2563eb;      /* blue-600 */
		--primary-700: #1d4ed8;  /* blue-700 */
		--success: #047857;      /* emerald-700 */
		--error: #b91c1c;        /* red-700 */
		--error-bg: #fef2f2;     /* red-50 */
		--success-bg: #ecfdf5;   /* green-50 */
		--info-bg: #eff6ff;      /* blue-50 */
		--info: #1d4ed8;         /* blue-700 */
		--ring: rgba(37, 99, 235, 0.35);
	}

	.page {
		min-height: 100vh;
		background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
		padding-bottom: 40px;
	}

	.hero {
		background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #38bdf8 100%);
		color: white;
		padding: 32px 16px;
		margin-bottom: 16px;
		box-shadow: inset 0 -1px 0 rgba(255,255,255,0.2);
	}
	.hero-inner {
		max-width: 900px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		gap: 16px;
	}
	.hero h1 { 
		margin: 0; 
		font-weight: 800; 
		font-size: 30px; 
		letter-spacing: 0.2px; 
		font-family: 'Segoe UI', system-ui, -apple-system, 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif; 
	}
	.hero p { margin: 6px 0 0; opacity: 0.95; }
	.hero-icon { font-size: 36px; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.2)); }

	.container { max-width: 900px; margin: 0 auto; padding: 16px; }

	.card {
		background: var(--card);
		border-radius: 14px;
		box-shadow: 0 10px 25px rgba(2, 6, 23, 0.08);
		padding: 18px;
		border: 1px solid rgba(2, 6, 23, 0.06);
		overflow: hidden;
		margin-bottom: 16px;
	}

	.label { 
		font-size: 13px; 
		color: var(--muted); 
		margin-bottom: 6px; 
		display: inline-block;
		font-family: 'Segoe UI', system-ui, -apple-system, 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
	}
	.textarea {
		width: 100%;
		max-width: 100%;
		display: block;
		box-sizing: border-box;
		border: 1px solid #d1d5db;
		border-radius: 10px;
		padding: 12px 14px;
		font-size: 15px;
		resize: none;
		outline: none;
		transition: box-shadow 0.2s, border-color 0.2s;
		background: #fff;
		color: var(--text);
		font-family: 'Segoe UI', system-ui, -apple-system, 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
	}
	.textarea:focus {
		border-color: var(--primary);
		box-shadow: 0 0 0 4px var(--ring);
	}

	.actions { margin-top: 14px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
	.btn {
		border: none;
		border-radius: 10px;
		padding: 10px 16px;
		font-weight: 600;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		transition: transform 0.05s, background 0.15s, box-shadow 0.15s;
	}
	.btn:active { transform: translateY(1px); }
	.btn:disabled { opacity: 0.7; cursor: not-allowed; }
	.btn-primary { background: var(--primary); color: white; box-shadow: 0 6px 18px rgba(37,99,235,0.3); }
	.btn-primary:hover:not(:disabled) { background: var(--primary-700); }

	.alert {
		margin-top: 14px;
		padding: 10px 12px;
		border-radius: 10px;
		font-size: 14px;
		border: 1px solid transparent;
	}
	.alert-error { background: var(--error-bg); color: var(--error); border-color: #fecaca; }
	.alert-success { background: var(--success-bg); color: var(--success); border-color: #a7f3d0; }
	.alert-info { background: var(--info-bg); color: var(--info); border-color: #bfdbfe; }

	.section-title { 
		font-size: 18px; 
		margin: 4px 0 10px; 
		font-weight: 700; 
		color: var(--text);
		font-family: 'Segoe UI', system-ui, -apple-system, 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
		letter-spacing: 0.1px;
	}
	.answer { 
		white-space: pre-wrap; 
		border: 1px solid #e5e7eb; 
		border-radius: 10px; 
		padding: 12px 14px; 
		background: #fff;
		line-height: 1.6;
	}

	/* Estilos para el HTML renderizado en las respuestas */
	.answer :global(h3) {
		color: var(--text);
		font-size: 18px;
		font-weight: 700;
		margin: 0 0 4px 0;
	}

	.answer :global(strong) {
		color: var(--text);
		font-weight: 600;
	}

	.answer :global(ul), .answer :global(ol) {
		margin: 8px 0;
		padding-left: 20px;
	}

	.answer :global(li) {
		margin: 4px 0;
	}

	.spinner {
		width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.45); border-top-color: white; border-radius: 50%;
		display: inline-block; animation: spin 0.8s linear infinite;
	}
	@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

	/* Focus para accesibilidad */
	.btn:focus-visible, .textarea:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }

	/* Responsive */
	@media (max-width: 768px) {
		.hero-inner {
			flex-direction: column;
			text-align: center;
			gap: 12px;
		}
		
		.hero h1 {
			font-size: 24px;
		}
		
		.container {
			padding: 12px;
		}
		
		.card {
			padding: 16px;
		}
	}
</style>