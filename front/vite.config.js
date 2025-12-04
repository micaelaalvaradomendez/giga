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
	}
});
