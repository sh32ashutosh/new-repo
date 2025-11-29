import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
  plugins: [
    react(),
    // This plugin automatically polyfills all Node.js modules for the browser
    nodePolyfills({
      // Include specific modules that simple-peer needs
      include: ['util', 'events', 'stream', 'path', 'buffer', 'process'],
      globals: {
        Buffer: true,
        global: true,
        process: true,
      },
      protocolImports: true,
    }),
  ],
  define: {
    // Fallback for some older libraries
    'global': 'window',
  },
})