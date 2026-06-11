import { useState } from 'react'
import { GitCompare, Camera } from 'lucide-react'
import { api } from '../api/client'

export default function DiffPage() {
  const [snapshots, setSnapshots] = useState([])
  const [diff, setDiff] = useState(null)
  const [loading, setLoading] = useState(false)
  const [snapshotName, setSnapshotName] = useState('')

  const takeSnapshot = async () => {
    const name = snapshotName.trim() || `snap_${Date.now()}`
    try {
      const result = await api.graphSnapshot(name)
      setSnapshots(prev => [...prev, { name, ...result }])
      setSnapshotName('')
    } catch (e) {
      alert(e.message)
    }
  }

  const computeDiff = async () => {
    if (snapshots.length < 2) return
    setLoading(true)
    try {
      const before = snapshots[snapshots.length - 2].name
      const after = snapshots[snapshots.length - 1].name
      const result = await api.graphDiff(before, after)
      setDiff(result)
    } catch (e) {
      alert(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold text-white">Graph Diff</h2>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 space-y-3">
        <p className="text-sm text-gray-400">Take snapshots before and after ingestion to see what changed.</p>
        <div className="flex gap-2">
          <input value={snapshotName} onChange={e => setSnapshotName(e.target.value)} placeholder="Snapshot name (optional)" className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200 outline-none" />
          <button onClick={takeSnapshot} className="flex items-center gap-1.5 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm">
            <Camera className="w-3.5 h-3.5" /> Snapshot
          </button>
        </div>
        {snapshots.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {snapshots.map((s, i) => (
              <span key={i} className="px-2 py-1 bg-[#0d1117] border border-[#30363d] rounded text-xs text-gray-300">
                {s.name} ({s.nodes} nodes)
              </span>
            ))}
          </div>
        )}
        {snapshots.length >= 2 && (
          <button onClick={computeDiff} disabled={loading} className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-white text-sm">
            <GitCompare className="w-3.5 h-3.5" /> {loading ? 'Computing...' : 'Compare Last Two'}
          </button>
        )}
      </div>

      {diff && (
        <div className="space-y-4">
          <div className="grid grid-cols-5 gap-3">
            {[
              { label: 'Nodes Added', value: diff.summary.nodes_added, color: 'green' },
              { label: 'Nodes Removed', value: diff.summary.nodes_removed, color: 'red' },
              { label: 'Nodes Updated', value: diff.summary.nodes_updated, color: 'blue' },
              { label: 'Rels Added', value: diff.summary.relationships_added, color: 'green' },
              { label: 'Rels Removed', value: diff.summary.relationships_removed, color: 'red' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 text-center">
                <div className={`text-lg font-bold text-${color}-400`}>{value}</div>
                <div className="text-xs text-gray-500">{label}</div>
              </div>
            ))}
          </div>

          {diff.new_nodes?.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
              <h3 className="text-sm font-medium text-green-400 mb-2">New Nodes</h3>
              <div className="flex flex-wrap gap-1">
                {diff.new_nodes.map((n, i) => (
                  <span key={i} className="px-2 py-0.5 bg-green-500/10 text-green-400 rounded text-xs">{n.name} ({n.label})</span>
                ))}
              </div>
            </div>
          )}

          {diff.new_relationships?.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
              <h3 className="text-sm font-medium text-blue-400 mb-2">New Relationships</h3>
              <div className="space-y-1">
                {diff.new_relationships.map((r, i) => (
                  <div key={i} className="text-xs text-gray-300">{r.from_name} <span className="text-blue-400">-[{r.type}]-&gt;</span> {r.to_name}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
