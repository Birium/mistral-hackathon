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
      '/update': 'http://core:8000',
      '/search': 'http://core:8000',
      '/sse':    'http://core:8000',
      '/tree':   'http://core:8000',
    }
  }
})