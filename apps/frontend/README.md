# Justice Platform Frontend

The Justice Platform frontend is a Vite-powered React workspace dedicated to building the neon courtroom experience. The scaffold focuses on performance, accessibility, and rapid iteration without sacrificing production readiness.

## Features

- React 18 with the SWC-powered Vite toolchain for near-instant feedback loops.
- Dark, neon-inspired base styles aligning with the experiential design direction.
- Modular component architecture ready to expand into chat, timeline, and simulation surfaces.

## Getting Started

### Install Dependencies

We recommend PNPM for workspace efficiency:

```bash
cd apps/frontend
pnpm install
```

If PNPM is unavailable, `npm install` works as well.

### Run Development Server

```bash
pnpm dev
```

The app is served at http://localhost:5173.

### Build for Production

```bash
pnpm build
```

Static assets are emitted to `dist/` for deployment behind a CDN or containerized UI tier.

## Project Layout

```
src/
  App.tsx                    # Root composition of hero and roadmap views
  main.tsx                   # React entrypoint with strict mode
  styles.css                 # Base neon courtroom styling
  components/
    HeroPanel.tsx            # Narrative hero block anchoring the strategy story
    MilestoneRoadmap.tsx     # Phase roadmap visualization
```

## Next Steps

- Integrate Tailwind CSS and Radix UI primitives per the design system directive.
- Connect to backend health endpoints and pipeline statuses for real-time dashboards.
- Establish shared type packages aligned with backend JSON schema contracts.
