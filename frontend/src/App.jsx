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
          <Route path="/schema" element={<SchemaPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/diff" element={<DiffPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}
