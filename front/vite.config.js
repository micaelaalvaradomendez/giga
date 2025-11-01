import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5173,
		strictPort: true,
		hmr: {
			host: 'localhost',
			port: 5173
		},
		proxy: {
			'/api': {
				target: process.env.VITE_API_BASE || 'http://localhost:8000',
				changeOrigin: true,
				secure: false,
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Sending Request to the Target:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
					});
				},
			}
		}
	},
	preview: {
		host: '0.0.0.0',
		port: 3000,
		strictPort: true
	},
	build: {
		target: 'esnext',
		sourcemap: true
	}
});
