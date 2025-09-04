import { Outlet, Link, NavLink } from "react-router-dom";

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-neutral-200/60 dark:border-neutral-800/60">
        <div className="container-page py-4 flex items-center justify-between">
          <Link to="/" className="font-semibold tracking-tight title-gradient text-xl">
            AI‑Researcher
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `px-2 py-1 rounded-md transition-colors ${isActive ? "bg-primary/10 text-primary" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`
              }
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/research/start"
              className={({ isActive }) =>
                `px-2 py-1 rounded-md transition-colors ${isActive ? "bg-primary/10 text-primary" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`
              }
            >
              Research
            </NavLink>
            <NavLink
              to="/paper/start"
              className={({ isActive }) =>
                `px-2 py-1 rounded-md transition-colors ${isActive ? "bg-primary/10 text-primary" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`
              }
            >
              Paper
            </NavLink>
            <NavLink
              to="/config"
              className={({ isActive }) =>
                `px-2 py-1 rounded-md transition-colors ${isActive ? "bg-primary/10 text-primary" : "hover:bg-neutral-100 dark:hover:bg-neutral-800"}`
              }
            >
              Config
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="container-page py-8">
        <Outlet />
      </main>
      <footer className="border-t border-neutral-200/60 dark:border-neutral-800/60">
        <div className="container-page py-6 text-sm text-muted">
          Bauhaus 2.0 — psychological minimalism, adaptive geometry, functional ornament.
        </div>
      </footer>
    </div>
  );
}

export default App;
