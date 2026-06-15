/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 8000 },
  preview: { port: 8000 },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './test/setup.js',
  },
});
