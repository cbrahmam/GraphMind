import { useState, useEffect } from 'react'
import { Database, Search, Plus } from 'lucide-react'

export default function VectorsPage() {
  const [stats, setStats] = useState(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [entityName, setEntityName] = useState('')
  const [entityText, setEntityText] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { loadStats() }, [])

  const loadStats = async () => {
    try {
      const res = await fetch('/api/vectors/stats')
      setStats(await res.json())
    } catch (e) { console.error(e) }
  }

  const searchVectors = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await fetch('/api/vectors/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 10 }),
      })
      const data = await res.json()
      setResults(data.results || [])
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  const storeVector = async () => {
    if (!entityName.trim() || !entityText.trim()) return
    try {
      await fetch('/api/vectors/store', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity_name: entityName, text: entityText }),
      })
      setEntityName('')
      setEntityText('')
      loadStats()
    } catch (e) { console.error(e) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <Database className="w-5 h-5 text-cyan-400" /> Vector Store
      </h1>
      <p className="text-sm text-gray-500 mb-6">Semantic search with vector embeddings</p>

      {stats && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="text-2xl font-bold text-cyan-400">{stats.total_vectors}</div>
            <div className="text-xs text-gray-500">Stored Vectors</div>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="text-2xl font-bold text-cyan-400">{stats.dimension || 0}</div>
            <div className="text-xs text-gray-500">Dimensions</div>
          </div>
        </div>
      )}

      <div className="mb-6">
        <h2 className="text-sm font-medium text-gray-400 mb-2">Semantic Search</h2>
        <div className="flex gap-2">
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search by meaning..."
            onKeyDown={e => e.key === 'Enter' && searchVectors()}
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={searchVectors} disabled={loading}
            className="px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg hover:bg-cyan-500/20">
            <Search className="w-4 h-4" />
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="space-y-2 mb-6">
          {results.map((r, i) => (
            <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center gap-3">
              <span className="text-sm text-gray-200 flex-1">{r.entity}</span>
              {r.label && <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded">{r.label}</span>}
              <span className="text-xs text-cyan-400">{(r.similarity * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
        <h2 className="text-sm font-medium text-gray-400 mb-3">Store New Embedding</h2>
        <div className="space-y-2">
          <input value={entityName} onChange={e => setEntityName(e.target.value)} placeholder="Entity name"
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <textarea value={entityText} onChange={e => setEntityText(e.target.value)} placeholder="Text to embed..."
            rows={3} className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={storeVector}
            className="flex items-center gap-1.5 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg hover:bg-cyan-500/20 text-sm">
            <Plus className="w-3.5 h-3.5" /> Store Embedding
          </button>
        </div>
      </div>
    </div>
  )
}
