import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwind from '@tailwindcss/vite';
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwind()],
  server: {
    proxy: {
        '/beans': 'http://localhost:8000', // Proxy to FastAPI backend root
    },
    watch:{
        usePolling: true
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src")
    }
  }
})
