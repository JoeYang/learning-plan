import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Serves from this skill directory, but allows importing CSS tokens from the
// sibling axiom-design skill via `../axiom-design/colors_and_type.css`.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      // Allow Vite to serve files from the parent .claude/skills/ dir so that
      // axiom-design tokens load without copying.
      allow: ['..', '../axiom-design'],
    },
  },
});
