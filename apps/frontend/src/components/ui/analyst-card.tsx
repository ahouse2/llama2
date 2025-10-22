import * as Avatar from "@radix-ui/react-avatar";
import { clsx } from "clsx";

const analysts: Record<string, { name: string; title: string; focus: string; color: string }> = {
  contracts: {
    name: "Elena Ward",
    title: "Contracts Strategist",
    focus: "Benchmarks clause risk and negotiates fallback playbooks.",
    color: "from-emerald-500 to-teal-500"
  },
  correspondence: {
    name: "Noah Patel",
    title: "Communications Sleuth",
    focus: "Detects sentiment pivots across counsel communications.",
    color: "from-cyan-500 to-blue-500"
  },
  filings: {
    name: "Sloane Rivers",
    title: "Litigation Analyst",
    focus: "Synthesizes docket filings into AI-assisted chronologies.",
    color: "from-indigo-500 to-purple-500"
  }
};

interface AnalystCardProps {
  dataset: string;
}

export function AnalystCard({ dataset }: AnalystCardProps): JSX.Element {
  const analyst = analysts[dataset] ?? analysts.contracts;

  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
      <div className="flex items-center gap-4">
        <Avatar.Root className="h-14 w-14 overflow-hidden rounded-full border border-slate-700">
          <Avatar.Image
            src={`https://avatars.dicebear.com/api/initials/${encodeURIComponent(analyst.name)}.svg`}
            alt={`${analyst.name} avatar`}
            className="h-full w-full object-cover"
          />
          <Avatar.Fallback className={clsx("flex h-full w-full items-center justify-center bg-gradient-to-br text-lg font-semibold text-slate-950", analyst.color)}>
            {analyst.name
              .split(" ")
              .map((segment) => segment[0])
              .join("")}
          </Avatar.Fallback>
        </Avatar.Root>
        <div>
          <p className="text-sm uppercase tracking-widest text-emerald-300">Workspace Analyst</p>
          <h3 className="text-xl font-semibold text-slate-50">{analyst.name}</h3>
          <p className="text-sm text-slate-400">{analyst.title}</p>
        </div>
      </div>
      <p className="text-sm leading-relaxed text-slate-300">{analyst.focus}</p>
    </article>
  );
}
