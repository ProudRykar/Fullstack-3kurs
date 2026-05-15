import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import type { Connect } from 'vite'

function bypassHtml(req: Connect.IncomingMessage): string | undefined {
  const accept = req.headers.accept || ''
  if (req.method === 'GET' && accept.includes('text/html')) {
    return '/index.html'
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/users': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/products': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/receipts': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/inventory': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/admin': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/warehouses': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
    },
  },

  // SPA fallback — serve index.html for unmatched routes
  appType: 'spa',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})