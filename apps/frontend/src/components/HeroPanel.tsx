const highlights = [
  "Timeline-aware copilots with courtroom-ready citations",
  "Graph-native intelligence that surfaces contradictions in seconds",
  "Playful yet rigorous simulations to pressure-test every argument"
];

function HeroPanel() {
  return (
    <section className="hero-panel">
      <p className="hero-kicker">Phase One: Ignite the Core</p>
      <h1 className="hero-title">
        Justice Platform reinvention begins with an obsidian-solid foundation.
      </h1>
      <p className="hero-body">
        We are orchestrating a modern monorepo that treats legal discovery as an art form—balancing precision engineering with a
        touch of theatrical flair. Every component built in Phase 1 is production-caliber, observable, and wired for the
        intelligence layers that follow.
      </p>
      <ul className="hero-highlight-grid">
        {highlights.map((item) => (
          <li key={item} className="hero-highlight">
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default HeroPanel;
