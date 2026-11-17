import { defineConfig } from 'vite';

// Builds into frontend_web/gamified, which the FastAPI server serves at /gamified/.
export default defineConfig({
  base: '/gamified/',
  build: {
    outDir: '../../frontend_web/gamified',
    emptyOutDir: true,
  },
});
