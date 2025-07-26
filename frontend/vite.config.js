import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      }
    },
  },
    allowedHosts: ['localhost', '127.0.0.1', 'dashbord.urbanmt.com.br', 'n8n-dashbord.ajljmq.easypanel.host'],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          utils: ['axios', 'date-fns']
        }
      }
    }
  }
})
