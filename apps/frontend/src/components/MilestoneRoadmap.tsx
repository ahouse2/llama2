import { Separator } from "@radix-ui/react-separator";

interface Milestone {
  title: string;
  description: string;
  items: string[];
}

interface Props {
  milestones: Milestone[];
}

function MilestoneRoadmap({ milestones }: Props) {
  return (
    <section className="roadmap">
      <header className="roadmap-header">
        <p className="roadmap-kicker">Strategic Trajectory</p>
        <h2 className="roadmap-title">From monorepo mastery to courtroom virtuosity.</h2>
        <p className="roadmap-body">
          Every milestone below is grounded in the TRD and engineered for executional certainty. Phase 1 unlocks disciplined
          delivery so that subsequent phases can compound intelligence and experience innovations without friction.
        </p>
      </header>
      <Separator decorative className="h-px w-full bg-brand-primary/30" />
      <div className="roadmap-grid">
        {milestones.map((milestone) => (
          <article key={milestone.title} className="roadmap-card">
            <div>
              <h3 className="roadmap-card-title">{milestone.title}</h3>
              <p className="roadmap-card-body">{milestone.description}</p>
            </div>
            <ul className="roadmap-card-list">
              {milestone.items.map((item) => (
                <li key={item} className="roadmap-card-list-item">
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

export default MilestoneRoadmap;
