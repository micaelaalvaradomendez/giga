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
				target: 'http://giga-django:8000',
				changeOrigin: true,
				secure: false
			},
			'/admin': {
				target: 'http://giga-django:8000',
				changeOrigin: true,
				secure: false
			},
			'/static': {
				target: 'http://giga-django:8000',
				changeOrigin: true,
				secure: false
			}
		}
	}
});
