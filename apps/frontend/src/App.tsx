import { useState } from "react";
import { ToastDemo } from "./components/ui/toast-demo";
import { AnalystCard } from "./components/ui/analyst-card";

const dataset = [
  { id: "contracts", title: "Contracts", description: "Clause extraction across NDAs and MSAs." },
  { id: "correspondence", title: "Correspondence", description: "Email threading with sentiment overlays." },
  { id: "filings", title: "Filings", description: "Automatic case timeline synthesis from dockets." }
];

export default function App(): JSX.Element {
  const [selection, setSelection] = useState<string>(dataset[0]?.id ?? "contracts");
  const active = dataset.find((item) => item.id === selection) ?? dataset[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-8 py-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Discovery Intelligence Console</h1>
            <p className="text-sm text-slate-400">Cross-application workspace curated for rapid legal insight.</p>
          </div>
          <ToastDemo />
        </div>
      </header>
      <main className="mx-auto flex max-w-6xl flex-col gap-8 px-8 py-10 lg:flex-row">
        <nav className="basis-1/3 space-y-3">
          {dataset.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setSelection(item.id)}
              className={`w-full rounded-xl border px-5 py-4 text-left transition focus:outline-none focus:ring-2 focus:ring-emerald-400 ${
                selection === item.id
                  ? "border-emerald-400/80 bg-emerald-500/10 text-emerald-100"
                  : "border-slate-800 bg-slate-900/50 text-slate-300 hover:border-slate-700 hover:bg-slate-800/60"
              }`}
            >
              <h2 className="text-lg font-medium">{item.title}</h2>
              <p className="text-sm text-slate-400">{item.description}</p>
            </button>
          ))}
        </nav>
        <section className="basis-2/3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl shadow-slate-950/40">
            <p className="text-sm uppercase tracking-[0.3em] text-emerald-300">Active Module</p>
            <h2 className="mt-2 text-3xl font-semibold text-slate-50">{active.title}</h2>
            <p className="mt-4 text-base text-slate-300">{active.description}</p>
            <div className="mt-6">
              <AnalystCard dataset={active.id} />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
