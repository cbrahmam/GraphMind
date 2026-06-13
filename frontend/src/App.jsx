import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import GraphExplorer from './pages/GraphExplorer'
import Graph3D from './pages/Graph3D'
import QueryPage from './pages/QueryPage'
import IngestPage from './pages/IngestPage'
import SchemaPage from './pages/SchemaPage'
import InsightsPage from './pages/InsightsPage'
import HistoryPage from './pages/HistoryPage'
import TimelinePage from './pages/TimelinePage'
import WatchlistPage from './pages/WatchlistPage'
import TemplatesPage from './pages/TemplatesPage'
import DiffPage from './pages/DiffPage'
import SettingsPage from './pages/SettingsPage'
import AnomalyPage from './pages/AnomalyPage'
import PredictionsPage from './pages/PredictionsPage'
import GapsPage from './pages/GapsPage'
import InfluencePage from './pages/InfluencePage'
import RSSPage from './pages/RSSPage'
import ReportsPage from './pages/ReportsPage'
import VectorsPage from './pages/VectorsPage'
import AuditPage from './pages/AuditPage'
import PathfinderPage from './pages/PathfinderPage'
import ComparisonPage from './pages/ComparisonPage'
import HypothesisPage from './pages/HypothesisPage'
import ResiliencePage from './pages/ResiliencePage'
import MotifsPage from './pages/MotifsPage'
import WhatIfPage from './pages/WhatIfPage'
import DuplicatesPage from './pages/DuplicatesPage'
import BackupsPage from './pages/BackupsPage'
import NotificationsPage from './pages/NotificationsPage'
import useWebSocket from './store/useWebSocket'

export default function App() {
  useWebSocket()

  return (
    <div className="flex h-screen bg-[#0D1117] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/graph" element={<GraphExplorer />} />
          <Route path="/graph3d" element={<Graph3D />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/ingest" element={<IngestPage />} />
          <Route path="/rss" element={<RSSPage />} />
          <Route path="/schema" element={<SchemaPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/pathfinder" element={<PathfinderPage />} />
          <Route path="/comparison" element={<ComparisonPage />} />
          <Route path="/hypothesis" element={<HypothesisPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
          <Route path="/influence" element={<InfluencePage />} />
          <Route path="/gaps" element={<GapsPage />} />
          <Route path="/anomaly" element={<AnomalyPage />} />
          <Route path="/motifs" element={<MotifsPage />} />
          <Route path="/whatif" element={<WhatIfPage />} />
          <Route path="/resilience" element={<ResiliencePage />} />
          <Route path="/duplicates" element={<DuplicatesPage />} />
          <Route path="/vectors" element={<VectorsPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/diff" element={<DiffPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/backups" element={<BackupsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}
