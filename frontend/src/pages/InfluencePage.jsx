import { useState, useEffect } from 'react'
import { Crown, Search } from 'lucide-react'

export default function InfluencePage() {
  const [topEntities, setTopEntities] = useState([])
  const [search, setSearch] = useState('')
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/influence/top?limit=15')
      .then(r => r.json())
      .then(d => setTopEntities(d.entities || []))
      .catch(console.error)
  }, [])

  const searchEntity = async () => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`/api/influence/entity/${encodeURIComponent(search)}`)
      const data = await res.json()
      setDetail(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <Crown className="w-5 h-5 text-yellow-400" /> Influence Analysis
      </h1>
      <p className="text-sm text-gray-500 mb-6">Discover the most influential entities and their reach</p>

      <div className="flex gap-2 mb-6">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search entity..."
          onKeyDown={e => e.key === 'Enter' && searchEntity()}
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <button onClick={searchEntity} disabled={loading}
          className="px-4 py-2 bg-yellow-500/10 text-yellow-400 rounded-lg hover:bg-yellow-500/20">
          <Search className="w-4 h-4" />
        </button>
      </div>

      {detail && (
        <div className="mb-6 bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-lg text-white font-bold">{detail.entity}</span>
            <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded">{detail.label}</span>
            <span className="text-sm text-yellow-400 ml-auto">Score: {detail.influence_score}</span>
          </div>
          <div className="text-sm text-gray-400 mb-3">Total reach: {detail.total_reach} entities across {detail.depth_analyzed} layers</div>
          {Object.entries(detail.layers || {}).map(([depth, nodes]) => (
            <div key={depth} className="mb-2">
              <div className="text-xs text-gray-500 mb-1">{depth.replace('_', ' ')} ({nodes.length} entities)</div>
              <div className="flex flex-wrap gap-1">
                {nodes.slice(0, 10).map((n, i) => (
                  <span key={i} className="text-xs bg-[#0d1117] border border-[#30363d] rounded px-2 py-0.5 text-gray-300">
                    {n.name}
                  </span>
                ))}
                {nodes.length > 10 && <span className="text-xs text-gray-500">+{nodes.length - 10} more</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      <h2 className="text-sm font-medium text-gray-400 mb-3">Most Influential Entities</h2>
      <div className="space-y-1">
        {topEntities.map((e, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center gap-3 cursor-pointer hover:bg-[#1c2128]"
            onClick={() => { setSearch(e.name); setDetail(null); fetch(`/api/influence/entity/${encodeURIComponent(e.name)}`).then(r => r.json()).then(setDetail) }}>
            <span className="text-xs text-gray-500 w-6 text-right">{i + 1}</span>
            <span className="text-sm text-gray-200 flex-1">{e.name}</span>
            <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded">{e.label}</span>
            <span className="text-xs text-gray-500">{e.degree} connections</span>
            <span className="text-sm text-yellow-400 font-medium">{e.influence_score}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
