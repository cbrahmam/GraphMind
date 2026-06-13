import { useState } from 'react'
import { Shapes, Triangle, Star, Link2 } from 'lucide-react'

export default function MotifsPage() {
  const [motifs, setMotifs] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadMotifs = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/motifs/all')
      setMotifs(await res.json())
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Shapes className="w-5 h-5 text-pink-400" /> Motif Detection
        </h1>
        <button onClick={loadMotifs} disabled={loading}
          className="px-4 py-2 bg-pink-500/10 text-pink-400 rounded-lg hover:bg-pink-500/20">
          {loading ? 'Scanning...' : 'Detect Motifs'}
        </button>
      </div>

      {motifs && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <Triangle className="w-6 h-6 text-pink-400 mx-auto mb-1" />
              <div className="text-xl font-bold text-pink-400">{motifs.triangles?.count || 0}</div>
              <div className="text-xs text-gray-500">Triangles</div>
            </div>
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <Star className="w-6 h-6 text-yellow-400 mx-auto mb-1" />
              <div className="text-xl font-bold text-yellow-400">{motifs.stars?.count || 0}</div>
              <div className="text-xs text-gray-500">Star Patterns</div>
            </div>
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <Link2 className="w-6 h-6 text-blue-400 mx-auto mb-1" />
              <div className="text-xl font-bold text-blue-400">{motifs.chains?.count || 0}</div>
              <div className="text-xs text-gray-500">Chains</div>
            </div>
          </div>

          {motifs.stars?.motifs?.length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-gray-400 mb-2">Star Patterns (hub entities)</h2>
              {motifs.stars.motifs.map((s, i) => (
                <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 mb-1">
                  <span className="text-sm text-yellow-400 font-medium">{s.center?.name}</span>
                  <span className="text-xs text-gray-500 ml-2">{s.degree} connections</span>
                </div>
              ))}
            </div>
          )}

          {motifs.triangles?.motifs?.length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-gray-400 mb-2">Triangles (tight clusters)</h2>
              {motifs.triangles.motifs.slice(0, 10).map((t, i) => (
                <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 mb-1 text-xs text-gray-300">
                  {t.nodes?.map(n => n.name).join(' — ')}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!motifs && !loading && (
        <p className="text-center text-gray-500 py-20">Click "Detect Motifs" to find structural patterns</p>
      )}
    </div>
  )
}
