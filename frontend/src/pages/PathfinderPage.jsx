import { useState } from 'react'
import { Route, ArrowRight } from 'lucide-react'

export default function PathfinderPage() {
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const findPath = async () => {
    if (!from.trim() || !to.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`/api/pathfinder/shortest?from_entity=${encodeURIComponent(from)}&to_entity=${encodeURIComponent(to)}`)
      setResult(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <Route className="w-5 h-5 text-blue-400" /> Path Finder
      </h1>

      <div className="flex gap-2 mb-6">
        <input value={from} onChange={e => setFrom(e.target.value)} placeholder="From entity..."
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <ArrowRight className="w-5 h-5 text-gray-500 self-center" />
        <input value={to} onChange={e => setTo(e.target.value)} placeholder="To entity..."
          onKeyDown={e => e.key === 'Enter' && findPath()}
          className="flex-1 bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-gray-200" />
        <button onClick={findPath} disabled={loading}
          className="px-4 py-2 bg-blue-500/10 text-blue-400 rounded-lg hover:bg-blue-500/20 disabled:opacity-50">
          {loading ? 'Finding...' : 'Find Path'}
        </button>
      </div>

      {result && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          {result.found ? (
            <>
              <div className="text-sm text-gray-400 mb-3">Shortest path: {result.depth} steps</div>
              <div className="flex flex-wrap items-center gap-2">
                {result.steps?.map((s, i) => (
                  <span key={i} className={s.type === 'node'
                    ? 'text-sm text-purple-400 bg-purple-400/10 px-3 py-1 rounded-full'
                    : 'text-xs text-gray-500'}>
                    {s.type === 'node' ? s.name : `→ [${s.relationship}] →`}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-500">No path found between these entities</p>
          )}
        </div>
      )}
    </div>
  )
}
