import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Dashboard from "./pages/Dashboard";
import ResearchStart from "./pages/ResearchStart";
import ResearchJob from "./pages/ResearchJob";
import PaperStart from "./pages/PaperStart";
import PaperJob from "./pages/PaperJob";
import ConfigPage from "./pages/Config";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "research/start", element: <ResearchStart /> },
      { path: "research/:jobId", element: <ResearchJob /> },
      { path: "paper/start", element: <PaperStart /> },
      { path: "paper/:jobId", element: <PaperJob /> },
      { path: "config", element: <ConfigPage /> },
    ],
  },
]);

export default router;
