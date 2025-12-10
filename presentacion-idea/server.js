const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname); // siempre relativo a este archivo

const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

function sendFile(res, filePath, contentType) {
    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 - File Not Found</h1>');
            } else {
                console.error('File read error:', error);
                res.writeHead(500, { 'Content-Type': 'text/html' });
                res.end(`<h1>500 - Server Error</h1><pre>${error.message}</pre>`);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
}

const server = http.createServer((req, res) => {
    try {
        console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);

        // health check rápido
        if (req.url === '/_health') {
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            return res.end('ok');
        }

        // Normalizar y proteger ruta contra path traversal
        let safeUrl = decodeURIComponent(req.url.split('?')[0]);
        if (safeUrl.includes('\0')) {
            res.writeHead(400);
            return res.end('Bad Request');
        }

        let requestedPath = safeUrl === '/' ? '/index.html' : safeUrl;
        const filePath = path.join(PUBLIC_DIR, requestedPath);
        if (!filePath.startsWith(PUBLIC_DIR)) { // protección extra
            res.writeHead(403);
            return res.end('Forbidden');
        }

        const extname = String(path.extname(filePath)).toLowerCase();
        const contentType = mimeTypes[extname] || 'application/octet-stream';

        sendFile(res, filePath, contentType);
    } catch (err) {
        console.error('Unhandled request error:', err);
        res.writeHead(500, { 'Content-Type': 'text/html' });
        res.end('<h1>500 - Server Error</h1>');
    }
});

process.on('uncaughtException', (err) => {
    console.error('Uncaught exception:', err);
    // Opcional: process.exit(1);
});
process.on('unhandledRejection', (reason) => {
    console.error('Unhandled rejection:', reason);
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Servidor de presentación GIGA corriendo en puerto ${PORT}`);
    console.log(`🌐 Acceso: http://0.0.0.0:${PORT}`);
});
