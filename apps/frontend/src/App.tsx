import HeroPanel from "./components/HeroPanel";
import MilestoneRoadmap from "./components/MilestoneRoadmap";

const milestones = [
  {
    title: "Phase 1 — Platform Foundations",
    description:
      "Restructure the monorepo, modernize toolchains, and deliver resilient service scaffolds across backend and frontend.",
    items: [
      "Modular FastAPI core with deterministic dependency injection",
      "React + Vite client workspace with neon courtroom aesthetic",
      "Automated Justfile tasks for development and CI hooks"
    ]
  },
  {
    title: "Phase 2 — Intelligence Engines",
    description:
      "Stand up ingestion orchestrators, hybrid retrieval, and multi-agent coordination aligned with TRD directives.",
    items: [
      "Asynchronous ingestion fabric with OCR acceleration",
      "Retrieval fusion of vectors, keyword, and graph context",
      "Autogen-powered agent mesh enforcing grounding guarantees"
    ]
  },
  {
    title: "Phase 3 — Experiential Differentiators",
    description:
      "Deliver the neon courtroom experience, Trial University learning hub, and playful mock courtroom simulator.",
    items: [
      "Accessibility-forward design system and collaboration",
      "Voice + multimodal interactions with persona TTS",
      "Feedback-rich courtroom simulations with analytics"
    ]
  }
];

function App() {
  return (
    <main className="app-shell">
      <div className="app-container">
        <HeroPanel />
        <MilestoneRoadmap milestones={milestones} />
      </div>
    </main>
  );
}

export default App;
