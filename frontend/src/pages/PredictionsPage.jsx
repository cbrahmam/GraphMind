import { useState, useEffect } from 'react'
import { Sparkles, GitBranch, Brain } from 'lucide-react'

export default function PredictionsPage() {
  const [tab, setTab] = useState('common')
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async (type) => {
    setLoading(true)
    setTab(type)
    try {
      const endpoints = {
        common: '/api/predictions/common-neighbors',
        structural: '/api/predictions/structural',
        ai: '/api/predictions/ai',
      }
      const res = await fetch(endpoints[type])
      const data = await res.json()
      setPredictions(data.predictions || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load('common') }, [])

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
        <Sparkles className="w-5 h-5 text-purple-400" /> Link Predictions
      </h1>
      <p className="text-sm text-gray-500 mb-6">Discover likely missing connections in your graph</p>

      <div className="flex gap-2 mb-6">
        {[
          { key: 'common', label: 'Common Neighbors', icon: GitBranch },
          { key: 'structural', label: 'Structural', icon: GitBranch },
          { key: 'ai', label: 'AI Predicted', icon: Brain },
        ].map(t => (
          <button key={t.key} onClick={() => load(t.key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${
              tab === t.key ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400 hover:text-gray-200 bg-[#161b22]'
            }`}>
            <t.icon className="w-3.5 h-3.5" /> {t.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-500 text-sm">Loading predictions...</p>}

      <div className="space-y-2">
        {predictions.map((p, i) => (
          <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-purple-400 font-medium">{p.entity1}</span>
              <span className="text-gray-500">→</span>
              <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded">
                {p.predicted_type || p.method}
              </span>
              <span className="text-gray-500">→</span>
              <span className="text-purple-400 font-medium">{p.entity2}</span>
              {p.confidence && (
                <span className="ml-auto text-xs text-gray-500">{Math.round(p.confidence * 100)}% confident</span>
              )}
              {p.score && !p.confidence && (
                <span className="ml-auto text-xs text-gray-500">Score: {p.score}</span>
              )}
            </div>
            {p.reasoning && <p className="text-xs text-gray-500 mt-1">{p.reasoning}</p>}
            {p.shared_connections?.length > 0 && (
              <p className="text-xs text-gray-500 mt-1">Shared: {p.shared_connections.join(', ')}</p>
            )}
          </div>
        ))}
      </div>

      {!loading && predictions.length === 0 && (
        <p className="text-center text-gray-500 py-10">No predictions found. Add more data to your graph.</p>
      )}
    </div>
  )
}
