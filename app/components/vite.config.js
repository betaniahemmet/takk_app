import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: __dirname, // ✅ So Vite knows where "project root" is
  publicDir: 'public', // access to image
  plugins: [react()],
  build: {
  outDir: path.resolve(__dirname, '../../dist'), // ✅ Absolute path = clean
  emptyOutDir: true, // ✅ Prevents warning
  assetsDir: 'assets',
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      '/log': 'http://localhost:5000',
      '/admin': 'http://localhost:5000',
      '/get-admin-settings': 'http://localhost:5000',
    },
  },
});
