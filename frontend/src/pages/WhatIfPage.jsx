import { useState } from 'react'
import { FlaskRound, Trash2, Plus } from 'lucide-react'

export default function WhatIfPage() {
  const [tab, setTab] = useState('remove')
  const [entity, setEntity] = useState('')
  const [fromE, setFromE] = useState('')
  const [toE, setToE] = useState('')
  const [relType, setRelType] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const simulateRemove = async () => {
    if (!entity.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`/api/whatif/remove/${encodeURIComponent(entity)}`)
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  const simulateAdd = async () => {
    if (!fromE.trim() || !toE.trim() || !relType.trim()) return
    setLoading(true)
    try {
      const res = await fetch('/api/whatif/add-relationship', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_entity: fromE, to_entity: toE, relationship_type: relType }),
      })
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <FlaskRound className="w-5 h-5 text-amber-400" /> What-If Simulation
      </h1>

      <div className="flex gap-2 mb-6">
        <button onClick={() => { setTab('remove'); setResult(null) }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs ${tab === 'remove' ? 'bg-red-500/10 text-red-400' : 'text-gray-400 bg-[#161b22]'}`}>
          <Trash2 className="w-3.5 h-3.5" /> Remove Entity
        </button>
        <button onClick={() => { setTab('add'); setResult(null) }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs ${tab === 'add' ? 'bg-green-500/10 text-green-400' : 'text-gray-400 bg-[#161b22]'}`}>
          <Plus className="w-3.5 h-3.5" /> Add Relationship
        </button>
      </div>

      {tab === 'remove' && (
        <div className="flex gap-2 mb-6">
          <input value={entity} onChange={e => setEntity(e.target.value)} placeholder="Entity to remove..."
            onKeyDown={e => e.key === 'Enter' && simulateRemove()}
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={simulateRemove} disabled={loading}
            className="px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20">Simulate</button>
        </div>
      )}

      {tab === 'add' && (
        <div className="flex gap-2 mb-6">
          <input value={fromE} onChange={e => setFromE(e.target.value)} placeholder="From..."
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <input value={relType} onChange={e => setRelType(e.target.value)} placeholder="RELATIONSHIP_TYPE"
            className="w-48 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <input value={toE} onChange={e => setToE(e.target.value)} placeholder="To..."
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
          <button onClick={simulateAdd} disabled={loading}
            className="px-4 py-2 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500/20">Simulate</button>
        </div>
      )}

      {result && !result.error && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          {result.impact_score !== undefined && (
            <>
              <div className="text-lg text-white font-bold mb-2">Impact Score: {result.impact_score}</div>
              <div className="text-sm text-gray-400">Relationships removed: {result.relationships_removed}</div>
              <div className="text-sm text-gray-400">Would orphan: {result.would_orphan?.length || 0} entities</div>
              <div className="text-sm text-gray-400">Would disconnect: {result.would_disconnect_pairs?.length || 0} pairs</div>
              {result.would_orphan?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {result.would_orphan.map((o, i) => (
                    <span key={i} className="text-xs bg-red-400/10 text-red-300 px-2 py-0.5 rounded">{o.name}</span>
                  ))}
                </div>
              )}
            </>
          )}
          {result.impact && (
            <>
              <div className="text-sm text-gray-400">Impact: <span className="text-white font-medium">{result.impact}</span></div>
              <div className="text-sm text-gray-400">Current distance: {result.current_distance < 0 ? 'Not connected' : result.current_distance}</div>
              <div className="text-sm text-gray-400">New distance: 1</div>
              {result.newly_reachable_from_source?.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-gray-500 mb-1">Newly reachable:</div>
                  <div className="flex flex-wrap gap-1">
                    {result.newly_reachable_from_source.map((n, i) => (
                      <span key={i} className="text-xs bg-green-400/10 text-green-300 px-2 py-0.5 rounded">{n}</span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
