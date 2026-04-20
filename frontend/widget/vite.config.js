import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync } from 'fs'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-index',
      closeBundle() {
        copyFileSync('public/index.html', 'dist/index.html')
      }
    }
  ],
  server: {
    port: 3001
  },
  build: {
    lib: {
      entry: 'src/main.jsx',
      name: 'LeadFlowWidget',
      fileName: 'widget',
      formats: ['iife']
    },
    rollupOptions: {
      output: {
        assetFileNames: 'widget.[ext]'
      }
    }
  }
})
