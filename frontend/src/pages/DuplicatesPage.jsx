import { useState, useEffect } from 'react'
import { Copy, Merge } from 'lucide-react'

export default function DuplicatesPage() {
  const [duplicates, setDuplicates] = useState([])
  const [threshold, setThreshold] = useState(0.8)
  const [loading, setLoading] = useState(false)

  const loadDuplicates = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/duplicates/?threshold=${threshold}`)
      const data = await res.json()
      setDuplicates(data.duplicates || [])
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  useEffect(() => { loadDuplicates() }, [])

  const merge = async (keepId, removeId) => {
    try {
      await fetch('/api/duplicates/merge', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keep_id: keepId, remove_id: removeId }),
      })
      loadDuplicates()
    } catch (e) { console.error(e) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <Copy className="w-5 h-5 text-orange-400" /> Duplicate Detection
      </h1>
      <p className="text-sm text-gray-500 mb-6">Find and merge duplicate entities</p>

      <div className="flex items-center gap-3 mb-6">
        <label className="text-xs text-gray-500">Threshold:</label>
        <input type="range" min="0.5" max="1" step="0.05" value={threshold}
          onChange={e => setThreshold(parseFloat(e.target.value))}
          className="w-40" />
        <span className="text-xs text-gray-400">{Math.round(threshold * 100)}%</span>
        <button onClick={loadDuplicates} disabled={loading}
          className="px-3 py-1.5 bg-orange-500/10 text-orange-400 rounded-lg text-xs hover:bg-orange-500/20">
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </div>

      <div className="space-y-2">
        {duplicates.map((d, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 flex items-center gap-3">
            <div className="flex-1">
              <span className="text-sm text-gray-200">{d.entity_a.name}</span>
              <span className="text-xs text-purple-400 ml-1">({d.entity_a.label})</span>
            </div>
            <span className="text-xs text-orange-400 font-medium">{Math.round(d.similarity * 100)}%</span>
            <div className="flex-1 text-right">
              <span className="text-sm text-gray-200">{d.entity_b.name}</span>
              <span className="text-xs text-purple-400 ml-1">({d.entity_b.label})</span>
            </div>
            <button onClick={() => merge(d.entity_a.id, d.entity_b.id)}
              className="flex items-center gap-1 text-xs text-green-400 hover:text-green-300 px-2 py-1 rounded bg-green-400/10">
              <Merge className="w-3 h-3" /> Merge
            </button>
          </div>
        ))}
      </div>

      {!loading && duplicates.length === 0 && (
        <p className="text-center text-gray-500 py-10">No duplicates found at {Math.round(threshold * 100)}% threshold</p>
      )}
    </div>
  )
}
