import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			out: 'build',
			precompress: false,
			envPrefix: ''
		}),
		alias: {
			$lib: 'src/lib'
		},
		// Configuración para mejorar la compatibilidad SSR
		ssr: {
			// No externalizar ningún paquete de $lib
			noExternal: process.env.NODE_ENV === 'production' ? ['$lib'] : []
		}
	},
	vitePlugin: {
		experimental: {
			inspector: {
				holdMode: true
			}
		}
	}
};

export default config;
