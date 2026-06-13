import { useState, useEffect } from 'react'
import { ShieldAlert, Activity } from 'lucide-react'

export default function ResiliencePage() {
  const [analysis, setAnalysis] = useState(null)
  const [critical, setCritical] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/resilience/analysis').then(r => r.json()).catch(() => null),
      fetch('/api/resilience/critical?top_n=10').then(r => r.json()).catch(() => ({})),
    ]).then(([a, c]) => {
      setAnalysis(a)
      setCritical(c.critical_nodes || [])
      setLoading(false)
    })
  }, [])

  const ratingColor = { high: 'text-green-400', medium: 'text-yellow-400', low: 'text-red-400' }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
        <ShieldAlert className="w-5 h-5 text-red-400" /> Network Resilience
      </h1>

      {loading && <p className="text-gray-500">Analyzing network resilience...</p>}

      {analysis && (
        <>
          <div className="grid grid-cols-4 gap-3 mb-6">
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <div className={`text-xl font-bold ${ratingColor[analysis.resilience_rating] || 'text-gray-400'}`}>
                {analysis.resilience_rating?.toUpperCase()}
              </div>
              <div className="text-xs text-gray-500">Resilience</div>
            </div>
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <div className="text-xl font-bold text-blue-400">{analysis.density}</div>
              <div className="text-xs text-gray-500">Density</div>
            </div>
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <div className="text-xl font-bold text-purple-400">{analysis.degree_stats?.avg}</div>
              <div className="text-xs text-gray-500">Avg Degree</div>
            </div>
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 text-center">
              <div className="text-xl font-bold text-orange-400">{analysis.isolated_nodes}</div>
              <div className="text-xs text-gray-500">Isolated</div>
            </div>
          </div>

          {analysis.single_points_of_failure?.length > 0 && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-red-400 mb-2">Single Points of Failure</h2>
              <div className="space-y-1">
                {analysis.single_points_of_failure.map((s, i) => (
                  <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-2.5 flex items-center gap-3 text-sm">
                    <Activity className="w-3.5 h-3.5 text-red-400" />
                    <span className="text-gray-200">{s.name}</span>
                    <span className="text-xs text-purple-400">{s.label}</span>
                    <span className="text-xs text-gray-500 ml-auto">{s.connections} dependent connections</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {critical.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-2">Critical Nodes (removal impact)</h2>
          <div className="space-y-1">
            {critical.map((c, i) => (
              <div key={i} className="bg-[#161b22] border border-[#30363d] rounded-lg p-2.5 flex items-center gap-3 text-sm">
                <span className="text-xs text-gray-500 w-6 text-right">{i + 1}</span>
                <span className="text-gray-200 flex-1">{c.name}</span>
                <span className="text-xs text-purple-400">{c.label}</span>
                <span className="text-xs text-gray-500">{c.degree} conn</span>
                <span className="text-xs text-red-400 font-medium">{Math.round(c.criticality_score * 100)}% critical</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
