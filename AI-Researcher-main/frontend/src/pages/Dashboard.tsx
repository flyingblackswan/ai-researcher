import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight title-gradient">
          Bauhaus 2.0 Interface
        </h1>
        <p className="text-sm text-muted max-w-2xl">
          Psychological minimalism, adaptive geometry, and functional ornament.
          Start a research workflow, generate a paper, or configure environment.
        </p>
      </header>

      <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card to="/research/start" title="Start Research" desc="Detailed Idea or Reference-Based flows with adaptive disclosure" accent="primary" />
        <Card to="/paper/start" title="Generate Paper" desc="Create a paper from completed research artifacts" accent="secondary" />
        <Card to="/config" title="Config" desc="View and edit environment variables (masked where appropriate)" accent="accent" />
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Recent Jobs</h2>
        <div className="text-sm text-muted">
          No recent jobs yet. Start a flow to see live updates here.
        </div>
      </section>
    </div>
  );
}

function Card(props: { to: string; title: string; desc: string; accent: "primary" | "secondary" | "accent" }) {
  const { to, title, desc, accent } = props;
  const accentClass =
    accent === "primary"
      ? "ring-1 ring-primary/20 hover:ring-primary/40"
      : accent === "secondary"
      ? "ring-1 ring-secondary/20 hover:ring-secondary/40"
      : "ring-1 ring-accent/20 hover:ring-accent/40";

  return (
    <Link to={to} className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 rounded-lg">
      <motion.div
        whileHover={{ y: -2 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className={`card ${accentClass}`}
      >
        <div className="space-y-2">
          <h3 className="text-base font-semibold">{title}</h3>
          <p className="text-sm text-muted">{desc}</p>
        </div>
      </motion.div>
    </Link>
  );
}
