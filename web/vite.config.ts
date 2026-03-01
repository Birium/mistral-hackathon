import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/update':      'http://localhost:8000',
      '/search':      'http://localhost:8000',
      '/sse':         'http://localhost:8000',
      '/tree':        'http://localhost:8000',
      '/transcribe':  'http://localhost:8000',
      // These paths are also used as frontend routes — only proxy API calls (non-HTML requests)
      '/file': {
        target: 'http://localhost:8000',
        bypass: (req) => req.headers.accept?.includes('text/html') ? '/index.html' : undefined,
      },
      '/inbox': {
        target: 'http://localhost:8000',
        bypass: (req) => req.headers.accept?.includes('text/html') ? '/index.html' : undefined,
      },
    }
  }
})