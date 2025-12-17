import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 3000,
		watch: {
			usePolling: true,
			interval: 100
		},
		proxy: {
			'/api': {
				target: process.env.VITE_API_URL || 'http://localhost:8000',
				changeOrigin: true,
				secure: false,
				rewrite: (path) => path
			},
			'/admin': {
				target: process.env.VITE_API_URL || 'http://localhost:8000',
				changeOrigin: true,
				secure: false
			},
			'/static': {
				target: process.env.VITE_API_URL || 'http://localhost:8000',
				changeOrigin: true,
				secure: false
			}
		}
	},
	build: {
		// Optimizaciones para producción
		minify: 'esbuild',
		target: 'es2015',
		cssMinify: true,
		rollupOptions: {
			output: {
				// Manualmente separar chunks para mejor caching
				manualChunks: (id) => {
					// Separar dependencias de node_modules en vendor chunk
					if (id.includes('node_modules')) {
						return 'vendor';
					}
					// Separar componentes admin en chunk separado
					if (id.includes('/lib/componentes/admin/')) {
						return 'admin-components';
					}
					// Separar controladores en chunk separado
					if (id.includes('/lib/paneladmin/controllers/')) {
						return 'controllers';
					}
				}
			}
		},
		// Aumentar límite de advertencia de chunk size (500kb)
		chunkSizeWarningLimit: 500
	}
});
