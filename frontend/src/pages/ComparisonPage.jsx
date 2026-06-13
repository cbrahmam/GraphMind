import { useState } from 'react'
import { GitCompare } from 'lucide-react'

export default function ComparisonPage() {
  const [entityA, setEntityA] = useState('')
  const [entityB, setEntityB] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const compare = async () => {
    if (!entityA.trim() || !entityB.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`/api/compare/?entity_a=${encodeURIComponent(entityA)}&entity_b=${encodeURIComponent(entityB)}`)
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <GitCompare className="w-5 h-5 text-indigo-400" /> Entity Comparison
      </h1>

      <div className="flex gap-2 mb-6">
        <input value={entityA} onChange={e => setEntityA(e.target.value)} placeholder="Entity A..."
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <span className="text-gray-500 self-center">vs</span>
        <input value={entityB} onChange={e => setEntityB(e.target.value)} placeholder="Entity B..."
          onKeyDown={e => e.key === 'Enter' && compare()}
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <button onClick={compare} disabled={loading}
          className="px-4 py-2 bg-indigo-500/10 text-indigo-400 rounded-lg hover:bg-indigo-500/20">
          Compare
        </button>
      </div>

      {result && !result.error && (
        <div className="grid grid-cols-2 gap-4">
          {['entity_a', 'entity_b'].map(key => {
            const e = result[key]
            return (
              <div key={key} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
                <div className="text-lg text-white font-bold">{e.name}</div>
                <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded">{e.label}</span>
                <div className="text-xs text-gray-500 mt-2">{e.degree} connections</div>
                <div className="mt-2 space-y-1">
                  {Object.entries(e.properties || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-xs">
                      <span className="text-gray-500">{k}</span>
                      <span className="text-gray-300">{String(v).slice(0, 50)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}

          <div className="col-span-2 bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-sm text-white font-medium">Similarity</span>
              <span className="text-lg text-indigo-400 font-bold">
                {Math.round((result.comparison?.jaccard_similarity || 0) * 100)}%
              </span>
            </div>
            {result.comparison?.shared_neighbors?.length > 0 && (
              <div className="mb-2">
                <div className="text-xs text-gray-500 mb-1">Shared connections ({result.comparison.shared_neighbors.length})</div>
                <div className="flex flex-wrap gap-1">
                  {result.comparison.shared_neighbors.map((n, i) => (
                    <span key={i} className="text-xs bg-indigo-400/10 text-indigo-300 px-2 py-0.5 rounded">{n}</span>
                  ))}
                </div>
              </div>
            )}
            {result.comparison?.shared_relationship_types?.length > 0 && (
              <div className="text-xs text-gray-500">
                Shared relationship types: {result.comparison.shared_relationship_types.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
