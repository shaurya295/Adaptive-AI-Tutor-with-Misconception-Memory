import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Builds into frontend_web/gamified, which the FastAPI server serves at /gamified/.
export default defineConfig({
  base: '/gamified/',
  plugins: [react()],
  build: {
    outDir: '../../frontend_web/gamified',
    emptyOutDir: true,
  },
});
