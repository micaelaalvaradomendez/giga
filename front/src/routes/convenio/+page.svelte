<script>
	import { convenioIaService } from "$lib/services.js";

	let pregunta = "";
	let respuesta = "";
	let loading = false;
	let error = "";

	async function consultar() {
		error = "";
		respuesta = "";
		if (!pregunta.trim()) return;
		loading = true;
		try {
			const resultado =
				await convenioIaService.consultarConvenio(pregunta);
			respuesta =
				resultado.respuesta ||
				resultado.message ||
				JSON.stringify(resultado);
		} catch (e) {
			error = e?.message || "Error consultando el convenio.";
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Consultas al Convenio Colectivo de Trabajo - Sistema GIGA</title>
</svelte:head>

<div class="page">
	<section class="hero">
		<div class="hero-inner">
			<div>
				<h1>Consultas al Convenio Colectivo de Trabajo</h1>
				<p>Respuestas estrictamente desde el convenio vigente.</p>
			</div>
		</div>
	</section>

	<div class="page-wrapper">
		<section class="container-pregunta">
			<div class="card">
				<textarea
					id="pregunta"
					class="textarea"
					rows="5"
					bind:value={pregunta}
					placeholder="Realice una pregunta acerca del convenio de trabajo:"
					on:keydown={(e) =>
						(e.ctrlKey || e.metaKey) &&
						e.key === "Enter" &&
						consultar()}
				></textarea>

				<div class="actions">
					<button
						class="button"
						on:click|preventDefault={consultar}
						disabled={loading || !pregunta.trim()}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							class="sparkle"
						>
							<path
								class="path"
								stroke-linejoin="round"
								stroke-linecap="round"
								stroke="#fff"
								fill="#fff"
								d="M14.187 8.096L15 5.25L15.813 8.096C16.0231 8.83114 16.4171 9.50062 16.9577 10.0413C17.4984 10.5819 18.1679 10.9759 18.903 11.186L21.75 12L18.904 12.813C18.1689 13.0231 17.4994 13.4171 16.9587 13.9577C16.4181 14.4984 16.0241 15.1679 15.814 15.903L15 18.75L14.187 15.904C13.9769 15.1689 13.5829 14.4994 13.0423 13.9587C12.5016 13.4181 11.8321 13.0241 11.097 12.814L8.25 12L11.096 11.187C11.8311 10.9769 12.5006 10.5829 13.0413 10.0423C13.5819 9.50162 13.9759 8.83214 14.186 8.097L14.187 8.096Z"
							></path>
							<path
								class="path"
								stroke-linejoin="round"
								stroke-linecap="round"
								stroke="#fff"
								fill="#fff"
								d="M6 14.25L5.741 15.285C5.59267 15.8785 5.28579 16.4206 4.85319 16.8532C4.42059 17.2858 3.87853 17.5927 3.285 17.741L2.25 18L3.285 18.259C3.87853 18.4073 4.42059 18.7142 4.85319 19.1468C5.28579 19.5794 5.59267 20.1215 5.741 20.715L6 21.75L6.259 20.715C6.40725 20.1216 6.71398 19.5796 7.14639 19.147C7.5788 18.7144 8.12065 18.4075 8.714 18.259L9.75 18L8.714 17.741C8.12065 17.5925 7.5788 17.2856 7.14639 16.853C6.71398 16.4204 6.40725 15.8784 6.259 15.285L6 14.25Z"
							></path>
							<path
								class="path"
								stroke-linejoin="round"
								stroke-linecap="round"
								stroke="#fff"
								fill="#fff"
								d="M6.5 4L6.303 4.5915C6.24777 4.75718 6.15472 4.90774 6.03123 5.03123C5.90774 5.15472 5.75718 5.24777 5.5915 5.303L5 5.5L5.5915 5.697C5.75718 5.75223 5.90774 5.84528 6.03123 5.96877C6.15472 6.09226 6.24777 6.24282 6.303 6.4085L6.5 7L6.697 6.4085C6.75223 6.24282 6.84528 6.09226 6.96877 5.96877C7.09226 5.84528 7.24282 5.75223 7.4085 5.697L8 5.5L7.4085 5.303C7.24282 5.24777 7.09226 5.15472 6.96877 5.03123C6.84528 4.90774 6.75223 4.75718 6.697 4.5915L6.5 4Z"
							></path>
						</svg>
						<span class="text_button">Consultar</span>
					</button>
				</div>

				{#if error}
					<div class="alert alert-error" role="alert">{error}</div>
				{/if}
			</div>
		</section>
	</div>

	{#if loading && !respuesta}
		<section class="container">
			<div class="loader-container">
				<ul class="wave-menu">
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
					<li></li>
				</ul>
			</div>
		</section>
	{/if}
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
	.hero {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 40px 20px;
		margin: 20px 10px;
		max-width: 1200px;
		border-radius: 28px;
		overflow: hidden;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	@media (min-width: 768px) {
		.hero {
			margin: 20px auto;
		}
	}

	.hero::before {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-image: linear-gradient(
				90deg,
				rgba(255, 255, 255, 0.03) 1px,
				transparent 1px
			),
			linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
		background-size: 50px 50px;
		animation: moveLines 20s linear infinite;
	}

	.hero-inner {
		position: relative;
		z-index: 1;
		max-width: 900px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.hero h1 {
		margin: 0;
		font-weight: 800;
		font-size: 18px;
		letter-spacing: 0.2px;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: block;
		max-width: 100%;
		word-wrap: break-word;
	}

	@media (min-width: 480px) {
		.hero h1 {
			font-size: 22px;
		}
	}

	@media (min-width: 640px) {
		.hero h1 {
			font-size: 26px;
			display: inline-block;
		}
	}

	@media (min-width: 768px) {
		.hero h1 {
			font-size: 30px;
		}
	}

	.hero h1::after {
		content: "";
		position: absolute;
		width: 40%;
		height: 3px;
		bottom: 0;
		left: 0;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(255, 255, 255, 0.9),
			transparent
		);
		animation: moveLine 2s linear infinite;
	}

	.hero p {
		margin: 6px 0 0;
		opacity: 0.95;
	}
	.page-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-top: 60px;
	}

	.container-pregunta {
		max-width: 95%;
		width: 100%;
	}

	@media (min-width: 768px) {
		.container-pregunta {
			max-width: 60%;
		}
	}

	.container-pregunta .card {
		background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
		border-radius: 16px;
		overflow: hidden;
	}

	.textarea {
		width: 97%;
		max-width: 100%;
		display: flex;
		margin: 12px;
		box-sizing: border-box;
		border: 2px solid #9ac8d2;
		border-radius: 10px;
		padding: 12px 14px 12px 16px;
		font-size: 18px;
		resize: none;
		outline: none;
		background: #fff;
		border-color: #93c5fd;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
	}

	.textarea:focus {
		border: 2px solid #9ac8d2;
		box-shadow: 0 0 0 4px var(--ring);
	}

	.actions {
		width: 97%;
		display: flex;
		justify-content: flex-end;
		align-items: flex-end;
		padding: 15px;
	}

	.actions .button {
		position: relative;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 8px;
		transform-origin: center;
		padding: 1rem 2rem;
		background-color: #148ad8;
		color: #ffffff;
		border: 2px solid rgb(16, 137, 211);
		border-radius: 100px;
		font-weight: 600;
		box-shadow: 0 0 20px #6fc5ff75;
		transform: scale(calc(1 + (var(--active, 0) * 0.1)));
		transition:
			transform 0.18s cubic-bezier(0.4, 0, 0.2, 1),
			box-shadow 0.18s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.button:is(:hover, :focus-visible) {
		--active: 1;
	}
	.button:active {
		transform: scale(1);
	}

	.button .sparkle {
		position: relative;
		z-index: 10;
		width: 1.75rem;
		height: 1.75rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.button .sparkle .path {
		fill: #fff;
		stroke: #fff;
		transform-origin: center;
	}

	.button:is(:hover, :focus) .sparkle .path {
		animation: path 1.5s linear 0.5s infinite;
	}

	.sparkle .path:nth-child(1) {
		--scale_path_1: 1.2;
	}
	.sparkle .path:nth-child(2) {
		--scale_path_2: 1.2;
	}
	.sparkle .path:nth-child(3) {
		--scale_path_3: 1.2;
	}

	@keyframes path {
		0%,
		34%,
		71%,
		100% {
			transform: scale(1);
		}
		17% {
			transform: scale(var(--scale_path_1, 1));
		}
		49% {
			transform: scale(var(--scale_path_2, 1));
		}
		83% {
			transform: scale(var(--scale_path_3, 1));
		}
	}

	.button .text_button {
		position: relative;
		z-index: 10;
		font-size: 1.2rem;
		color: #ffffff;
		font-weight: 600;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
	}

	.alert {
		margin-top: 14px;
		padding: 10px 12px;
		border-radius: 10px;
		font-size: 14px;
		border: 1px solid transparent;
	}
	.alert-error {
		background: var(--error-bg);
		color: var(--error);
		border-color: #fecaca;
	}

	.container {
		max-width: 95%;
		width: 100%;
		margin: 40px auto 0;
	}

	@media (min-width: 768px) {
		.container {
			max-width: 60%;
		}
	}

	.loader-container {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 60px 20px;
	}

	.wave-menu {
		border: 4px solid #3b82f6;
		border-radius: 50px;
		width: 200px;
		height: 45px;
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 0;
		margin: 0;
		position: relative;
		background: #fff;
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
	}

	.wave-menu li {
		list-style: none;
		height: 30px;
		width: 4px;
		border-radius: 10px;
		background: #3b82f6;
		margin: 0 6px;
		padding: 0;
		animation-name: wave1;
		animation-duration: 0.3s;
		animation-iteration-count: infinite;
		animation-direction: alternate;
		transition: ease 0.2s;
	}

	.wave-menu li:nth-child(1) {
		background: #1e40af;
	}

	.wave-menu li:nth-child(2) {
		animation-name: wave2;
		animation-delay: 0.2s;
		background: #2563eb;
	}

	.wave-menu li:nth-child(3) {
		animation-name: wave3;
		animation-delay: 0.23s;
		animation-duration: 0.4s;
		background: #3b82f6;
	}

	.wave-menu li:nth-child(4) {
		animation-name: wave4;
		animation-delay: 0.1s;
		animation-duration: 0.3s;
		background: #60a5fa;
	}

	.wave-menu li:nth-child(5) {
		animation-delay: 0.5s;
		background: #3b82f6;
	}

	.wave-menu li:nth-child(6) {
		animation-name: wave2;
		animation-duration: 0.5s;
		background: #2563eb;
	}

	.wave-menu li:nth-child(7) {
		background: #3b82f6;
	}

	.wave-menu li:nth-child(8) {
		animation-name: wave4;
		animation-delay: 0.4s;
		animation-duration: 0.25s;
		background: #60a5fa;
	}

	.wave-menu li:nth-child(9) {
		animation-name: wave3;
		animation-delay: 0.15s;
		background: #2563eb;
	}

	.wave-menu li:nth-child(10) {
		background: #1e40af;
	}

	@keyframes wave1 {
		from {
			transform: scaleY(1);
		}
		to {
			transform: scaleY(0.5);
		}
	}

	@keyframes wave2 {
		from {
			transform: scaleY(0.3);
		}
		to {
			transform: scaleY(0.6);
		}
	}

	@keyframes wave3 {
		from {
			transform: scaleY(0.6);
		}
		to {
			transform: scaleY(0.8);
		}
	}

	@keyframes wave4 {
		from {
			transform: scaleY(0.2);
		}
		to {
			transform: scaleY(0.5);
		}
	}

	.container {
		width: 100%;
		margin: 0 auto;
		margin-top: 40px;
		margin-bottom: 20px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.container::-webkit-scrollbar {
		display: none;
	}

	.container .card {
		background: #ffffff;
		border-radius: 16px;
		padding: 20px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
		border: 2px solid #93c5fd;
	}

	.section-title {
		font-size: 16px;
		margin: 0 0 12px;
		font-weight: 700;
		color: #1e293b;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		letter-spacing: 0.1px;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: block;
		max-width: 100%;
		word-wrap: break-word;
	}

	@media (min-width: 480px) {
		.section-title {
			font-size: 17px;
		}
	}

	@media (min-width: 640px) {
		.section-title {
			font-size: 18px;
			display: inline-block;
		}
	}

	.section-title::after {
		content: "";
		position: absolute;
		width: 50%;
		height: 3px;
		bottom: 0;
		left: 0;
		background: linear-gradient(90deg, transparent, #3b82f6, transparent);
		animation: moveLine 2s linear infinite;
	}

	.answer {
		background: #f0f9ff;
		border-radius: 10px;
		padding: 20px;
		line-height: 1.8;
		color: #374151;
		font-size: 18px;
		white-space: pre-wrap;
		max-height: 600px;
		overflow-y: auto;
	}

	@media (min-width: 768px) {
		.answer {
			padding: 16px;
			font-size: 15px;
			line-height: 1.7;
		}
	}

	/* Estilos para el HTML renderizado en las respuestas */
	.answer :global(h3) {
		color: #1e293b;
		font-size: 17px;
		font-weight: 700;
		margin: 20px 0 8px 0;
		padding-top: 12px;
		border-top: 2px solid #e0f2fe;
	}

	.answer :global(h3:first-child) {
		margin-top: 0;
		padding-top: 0;
		border-top: none;
	}

	.answer :global(strong) {
		color: #1e293b;
		font-weight: 600;
		background: linear-gradient(120deg, #dbeafe 0%, #bfdbfe 100%);
		padding: 2px 4px;
		border-radius: 3px;
	}

	.answer :global(ul),
	.answer :global(ol) {
		margin: 12px 0;
		padding-left: 24px;
		line-height: 1.8;
	}

	.answer :global(li) {
		margin: 8px 0;
		padding-left: 4px;
	}

	.answer :global(li strong) {
		display: inline-block;
		margin-bottom: 4px;
	}

	.answer :global(p) {
		margin: 12px 0;
		line-height: 1.8;
	}

	.answer :global(p:first-child) {
		margin-top: 0;
	}

	.answer :global(p:last-child) {
		margin-bottom: 0;
	}

	.answer :global(code) {
		background: #f1f5f9;
		padding: 2px 6px;
		border-radius: 4px;
		font-size: 14px;
		color: #1e40af;
		font-family: "Courier New", monospace;
	}

	.answer :global(hr) {
		border: none;
		border-top: 2px solid #e0f2fe;
		margin: 20px 0;
	}

	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}

	@media (max-width: 768px) {
		.hero-inner {
			flex-direction: column;
			text-align: center;
			gap: 12px;
		}

		.container {
			padding: 12px;
			width: 90%;
		}

		.card {
			padding: 16px;
		}
	}
</style>
