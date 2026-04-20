import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
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
