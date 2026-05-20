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
const API_PROXY_TARGET = process.env.VITE_API_PROXY || 'http://localhost:8000'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/users': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/products': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/receipts': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/inventory': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/admin': {
        target: API_PROXY_TARGET,
        changeOrigin: true,
        bypass: (req) => bypassHtml(req),
      },
      '/warehouses': {
        target: API_PROXY_TARGET,
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