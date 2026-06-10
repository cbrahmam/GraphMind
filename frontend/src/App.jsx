import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import GraphExplorer from './pages/GraphExplorer'
import QueryPage from './pages/QueryPage'
import IngestPage from './pages/IngestPage'
import SchemaPage from './pages/SchemaPage'
import HistoryPage from './pages/HistoryPage'
import InsightsPage from './pages/InsightsPage'

export default function App() {
  return (
    <div className="flex h-screen bg-[#0D1117] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/graph" element={<GraphExplorer />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/ingest" element={<IngestPage />} />
          <Route path="/schema" element={<SchemaPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>
    </div>
  )
}
