//########################
// frontend/vite.config.js
//########################

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],

  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('echarts') || id.includes('zrender')) {
              return 'vendor-echarts';
            }
            if (id.includes('react-router') || id.includes('react-dom') || id.includes('react/') || id.includes('scheduler')) {
              return 'vendor-react';
            }
            if (id.includes('@tanstack')) {
              return 'vendor-query';
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons';
            }
            if (id.includes('i18next')) {
              return 'vendor-i18n';
            }
          }
        }
      }
    }
  },

  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000", // ✅ FIX
        changeOrigin: true,
        secure: false,
      },
      "/ws": {
        target: "ws://localhost:8000", // ✅ FIX
        ws: true,
      },
    },
  }
});
