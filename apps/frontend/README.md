# Frontend Application — Discovery Intelligence Console

This React + Vite workspace powers the legal discovery intelligence console. It ships with Tailwind CSS for rapid, composable styling and Radix UI primitives for accessible component interactions.

## Stack Overview
- **Build tool:** Vite 5 with the React SWC plugin for lightning-fast HMR and builds.
- **Language:** TypeScript with strict compiler rules.
- **Styling:** Tailwind CSS with a dark-first palette tuned for litigation analytics.
- **UI Primitives:** Radix UI (Toast, Avatar) to ensure accessible interactions out of the box.
- **Testing:** Vitest with Testing Library and jest-dom matchers.
- **Linting & Formatting:** ESLint (TypeScript + React Hooks + React Refresh rules) and Prettier.

## Getting Started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```
   The app is served on [`http://localhost:5173`](http://localhost:5173).
3. Run the test suite:
   ```bash
   npm test
   ```
4. Type-check and lint:
   ```bash
   npm run typecheck
   npm run lint
   ```
5. Format source files:
   ```bash
   npm run format:write
   ```

## Architectural Notes
- Component modules live in `src/components`. Compose UI primitives within feature-specific subdirectories.
- Tailwind configuration is centralized in `tailwind.config.ts`; shared tokens belong in the `extend` section.
- Radix UI toasts are orchestrated via the `ToastDemo` component, demonstrating the pattern for asynchronous status surfaces.

## Production Builds
Generate an optimized bundle with:
```bash
npm run build
```
The static artifacts emit to `dist/` and can be hosted on any modern CDN or static host.
