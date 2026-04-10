import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

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
      },
      '/users': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/products': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/receipts': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/inventory': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})