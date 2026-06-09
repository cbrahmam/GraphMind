import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Network, GitBranch, Upload, MessageSquare, Search } from 'lucide-react'
import useStore from '../store/useStore'
import { api } from '../api/client'

const LABEL_COLORS = {
  Person: '#3b82f6', Organization: '#22c55e', Technology: '#a855f7',
  Location: '#f97316', Event: '#ef4444', Concept: '#14b8a6', Product: '#ec4899',
}

export default function Dashboard() {
  const navigate = useNavigate()
  const stats = useStore(s => s.stats)
  const suggestions = useStore(s => s.suggestions)
  const ingestions = useStore(s => s.ingestions)
  const fetchStats = useStore(s => s.fetchStats)
  const fetchSuggestions = useStore(s => s.fetchSuggestions)
  const fetchIngestions = useStore(s => s.fetchIngestions)
  const [schema, setSchema] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchSuggestions()
    fetchIngestions()
    api.graphSchema().then(setSchema).catch(() => {})
  }, [fetchStats, fetchSuggestions, fetchIngestions])

  const labelCounts = stats?.label_counts || {}
  const relCounts = stats?.relationship_type_counts || {}
  const maxLabel = Math.max(1, ...Object.values(labelCounts))
  const maxRel = Math.max(1, ...Object.values(relCounts))

  return (
    <div className="p-6 space-y-6 max-w-6xl">
      <h2 className="text-2xl font-bold text-white">Dashboard</h2>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Nodes', value: stats?.total_nodes ?? 0, icon: Network, color: 'purple' },
          { label: 'Relationships', value: stats?.total_relationships ?? 0, icon: GitBranch, color: 'blue' },
          { label: 'Labels', value: Object.keys(labelCounts).length, icon: Network, color: 'green' },
          { label: 'Rel Types', value: Object.keys(relCounts).length, icon: GitBranch, color: 'orange' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">{label}</span>
              <Icon className={`w-4 h-4 text-${color}-400`} />
            </div>
            <div className="text-2xl font-bold text-white">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Label Distribution</h3>
          <div className="space-y-2">
            {Object.entries(labelCounts).map(([label, count]) => (
              <div key={label} className="flex items-center gap-2">
                <span className="text-xs text-gray-400 w-24 truncate">{label}</span>
                <div className="flex-1 bg-[#0d1117] rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${(count / maxLabel) * 100}%`, backgroundColor: LABEL_COLORS[label] || '#6b7280' }}
                  />
                </div>
                <span className="text-xs text-gray-300 w-8 text-right">{count}</span>
              </div>
            ))}
            {!Object.keys(labelCounts).length && <p className="text-xs text-gray-500">No data yet. Ingest a document to get started.</p>}
          </div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Relationship Distribution</h3>
          <div className="space-y-2">
            {Object.entries(relCounts).slice(0, 8).map(([type, count]) => (
              <div key={type} className="flex items-center gap-2">
                <span className="text-xs text-gray-400 w-28 truncate">{type}</span>
                <div className="flex-1 bg-[#0d1117] rounded-full h-4 overflow-hidden">
                  <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${(count / maxRel) * 100}%` }} />
                </div>
                <span className="text-xs text-gray-300 w-8 text-right">{count}</span>
              </div>
            ))}
            {!Object.keys(relCounts).length && <p className="text-xs text-gray-500">No relationships yet.</p>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Ingestions</h3>
          <div className="space-y-2">
            {(ingestions || []).slice(0, 5).map(doc => (
              <div key={doc.id} className="flex items-center justify-between py-1">
                <span className="text-sm text-gray-300 truncate flex-1">{doc.filename}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  doc.status === 'built' ? 'bg-green-500/10 text-green-400' :
                  doc.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                  'bg-yellow-500/10 text-yellow-400'
                }`}>{doc.status}</span>
              </div>
            ))}
            {!(ingestions || []).length && <p className="text-xs text-gray-500">No documents ingested yet.</p>}
          </div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <button onClick={() => navigate('/ingest')} className="w-full flex items-center gap-2 px-3 py-2 bg-purple-500/10 text-purple-400 rounded-lg text-sm hover:bg-purple-500/20 transition-colors">
              <Upload className="w-4 h-4" /> Ingest Document
            </button>
            <button onClick={() => navigate('/query')} className="w-full flex items-center gap-2 px-3 py-2 bg-blue-500/10 text-blue-400 rounded-lg text-sm hover:bg-blue-500/20 transition-colors">
              <MessageSquare className="w-4 h-4" /> Ask a Question
            </button>
            <button onClick={() => navigate('/graph')} className="w-full flex items-center gap-2 px-3 py-2 bg-green-500/10 text-green-400 rounded-lg text-sm hover:bg-green-500/20 transition-colors">
              <Search className="w-4 h-4" /> Explore Graph
            </button>
          </div>
        </div>
      </div>

      {suggestions.length > 0 && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Suggested Queries</h3>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((q, i) => (
              <button key={i} onClick={() => navigate('/query', { state: { question: q } })} className="px-3 py-1.5 bg-[#0d1117] border border-[#30363d] rounded-full text-xs text-gray-300 hover:border-purple-500/50 hover:text-purple-400 transition-colors">
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
